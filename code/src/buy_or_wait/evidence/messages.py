from __future__ import annotations

import re
from datetime import date, datetime
from dataclasses import replace
from decimal import Decimal, InvalidOperation

from buy_or_wait.config import Settings
from buy_or_wait.evidence.cache import EvidenceCache, content_hash
from buy_or_wait.evidence.models import EvidenceContext, EventPatch, IncomeSchedulePatch, RentPatch
from buy_or_wait.ingest.loader import Dataset, MessageRow

_AMOUNT_RE = re.compile(
    r"(?:IDR|INR|ZAR|EUR|USD|₹|Rp\.?)\s*([\d,]+(?:\.\d+)?)|"
    r"([\d,]+(?:\.\d+)?)\s*(?:IDR|INR|ZAR|EUR|USD)",
    re.IGNORECASE,
)
_DATE_RE = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")
_PERCENT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*%")

SCAM_PATTERNS = (
    "processing fee",
    "verify your account",
    "claim your prize",
    "send us",
    "wire transfer fee",
)


def _parse_amount(text: str) -> tuple[Decimal, str] | None:
    for match in _AMOUNT_RE.finditer(text):
        raw = (match.group(1) or match.group(2) or "").replace(",", "")
        if not raw:
            continue
        try:
            amount = Decimal(raw)
        except InvalidOperation:
            continue
        prefix = text[max(0, match.start() - 6) : match.end() + 6].upper()
        for ccy in ("IDR", "INR", "ZAR", "EUR", "USD"):
            if ccy in prefix or (ccy == "INR" and "₹" in prefix):
                return amount, ccy
        return amount, ""
    return None


def _parse_date(text: str) -> date | None:
    match = _DATE_RE.search(text)
    if match:
        return date.fromisoformat(match.group(1))
    return None


def _financial_text(text: str) -> str:
    directives = re.compile(r"ignore (?:all |previous |the |system |challenge )?(?:instructions|rules)|"
                            r"amount_safe_to_pay|recommended_payment_method|system prompt|you are now", re.I)
    return " ".join(part for part in re.split(r"(?<=[.!?])\s+|[\r\n]+", text)
                    if not directives.search(part))


class MessageResolver:
    def __init__(self, dataset: Dataset, settings: Settings | None = None):
        self.dataset = dataset
        self.settings = settings or Settings()
        self.cache = EvidenceCache(
            self.settings.resolved_evidence_cache_dir,
            self.dataset.version_hash,
        )

    def resolve_for_user(self, user_id: str, request_date: date, request_id: str | None = None) -> EvidenceContext:
        ctx = EvidenceContext()
        messages = list(self.dataset.messages_by_user.get(user_id, []))
        if request_id:
            messages.extend(self.dataset.messages_by_request.get(request_id, []))
        seen: set[str] = set()
        for message in sorted(messages, key=lambda m: m.sent_at):
            if message.message_id in seen:
                continue
            seen.add(message.message_id)
            if message.user_id != user_id or (message.request_id and message.request_id != request_id):
                continue
            if datetime.fromisoformat(message.sent_at.replace("Z", "+00:00")).date() > request_date:
                continue
            patch = self._resolve_message(message, request_date)
            patch.event_patches = {key: replace(value, source=message.source_type, observed_at=message.sent_at)
                                   for key, value in patch.event_patches.items()}
            ctx = ctx.merge(patch)
        return ctx

    def _resolve_message(self, message: MessageRow, request_date: date) -> EvidenceContext:
        from buy_or_wait.evidence.structured import FactExtractor
        from buy_or_wait.evidence.interpret import interpret_message
        prepared = FactExtractor(self.dataset, self.settings).message(message)
        if prepared is not None:
            return interpret_message(self.dataset, self.settings, message, request_date, prepared)
        ctx = self._extract_message_context(message, request_date)
        if not ctx.income_patches:
            return ctx
        from buy_or_wait.finance.recurrence import detect_recurring_series, series_identity, SPECULATIVE
        events = [e for e in self.dataset.events_by_user.get(message.user_id, [])
                  if e.direction == "credit" and e.category == "salary"
                  and e.status in {"settled", "scheduled"}
                  and not any(word in e.description.lower() for word in SPECULATIVE)]
        recurring = detect_recurring_series(events, request_date, self.settings.recurrence)
        keys = {s.series_key for s in recurring}
        if not keys:
            keys = {series_identity(e) for e in events if e.settlement_date < request_date}
        from buy_or_wait.finance.income import (associate_income, select_income_targets,
                                               income_scope_event_ids)
        associations = associate_income(events, request_date)
        currencies = {p.currency for p in ctx.income_patches if p.currency}
        targets = select_income_targets(events, associations, keys,
            linked_event_id=message.related_event_id,
            currency=next(iter(currencies)) if len(currencies) == 1 else None,
            quote=_financial_text(message.message_text))
        ambiguous = len(targets) != 1
        target_events = income_scope_event_ids(events, associations, targets,
                                               linked_event_id=message.related_event_id)
        ctx.income_patches = [replace(p, target_series_keys=tuple(sorted(targets)) if not ambiguous else (),
                                     target_event_ids=target_events,
                                     ambiguous_target=ambiguous) for p in ctx.income_patches]
        if ambiguous:
            ctx.notes.append(f"ambiguous income target; no increase or resumption {message.message_id}")
        return ctx

    def _extract_message_context(self, message: MessageRow, request_date: date) -> EvidenceContext:
        text = _financial_text(message.message_text)
        # Discard directives about the agent/output, retaining separate factual sentences.
        lower = text.lower()
        ctx = EvidenceContext()
        if not text.strip():
            ctx.notes.append(f"ignored embedded instructions {message.message_id}")
            return ctx

        if any(pattern in lower for pattern in SCAM_PATTERNS):
            ctx.notes.append(f"ignored scam message {message.message_id}")
            return ctx

        if "matching debit and credit" in lower or "transfer between your two accounts" in lower:
            if message.related_event_id:
                ctx.suppressed_event_ids.add(message.related_event_id)
                related = self.dataset.events_by_id.get(message.related_event_id)
                if related and related.linked_event_id:
                    ctx.suppressed_event_ids.add(related.linked_event_id)
            ctx.notes.append(f"internal transfer net-zero {message.message_id}")
            return ctx

        if any(p in lower for p in ("employment has ended", "no regular salary payments scheduled",
                                    "seasonal contract has ended", "no off-season income")):
            effective = _parse_date(text) or request_date
            ctx.income_patches.append(
                IncomeSchedulePatch(category="salary", stop_after=effective)
            )
            ctx.notes.append(f"employment ended {message.message_id}")
            return ctx

        if "refund" in lower and ("not credited" in lower or "not been posted" in lower or "still pending" in lower):
            if message.related_event_id:
                ctx.event_patches[message.related_event_id] = EventPatch(
                    event_id=message.related_event_id,
                    suppress=True,
                )
                ctx.suppressed_event_ids.add(message.related_event_id)
            ctx.notes.append(f"pending refund ignored {message.message_id}")
            return ctx

        if "commission" in lower and ("not approved" in lower or "belum disetujui" in lower or "not included" in lower):
            ctx.notes.append(f"commission excluded {message.message_id}")

        if ("payout" in lower or "app earnings" in lower) and any(p in lower for p in
                ("still pending", "not withdrawable", "isn't withdrawable", "isn\u2019t withdrawable", "can change until")):
            ctx.income_patches.append(IncomeSchedulePatch(unconfirmed_variable_income=True))
            ctx.notes.append(f"unconfirmed platform earnings excluded {message.message_id}")

        if "rent" in lower and "increases" in lower and "%" in lower:
            pct_match = _PERCENT_RE.search(text)
            if pct_match:
                multiplier = Decimal("1") + Decimal(pct_match.group(1)) / Decimal("100")
                effective = _parse_date(text) or request_date
                ctx.rent_patches.append(RentPatch(multiplier=multiplier, effective_from=effective))
                ctx.notes.append(f"rent increase {message.message_id}")
            return ctx

        salary_patterns = (
            "salary",
            "gaji",
            "payroll",
            "monthly pay",
            "penggajian",
        )
        if any(p in lower for p in salary_patterns):
            parsed = _parse_amount(text)
            effective = _parse_date(text)
            if not parsed and effective and any(p in lower for p in ("expected on", "revised date", "rescheduled")):
                from buy_or_wait.finance.recurrence import detect_recurring_series, project_series_dates
                from datetime import timedelta
                future = []
                for series in detect_recurring_series(self.dataset.events_by_user.get(message.user_id, []),
                                                       request_date, self.settings.recurrence):
                    if series.category == "salary" and series.direction == "credit":
                        anchor = self.dataset.events_by_id[series.template_event_id].settlement_date
                        future.extend(project_series_dates(request_date, request_date + timedelta(days=40),
                            series.cadence_days, anchor, monthly=series.monthly, anchor_day=series.anchor_day))
                if future:
                    ctx.income_patches.append(IncomeSchedulePatch(original_date=min(future), payment_date=effective))
                    ctx.notes.append(f"salary date amended {message.message_id}")
            if parsed:
                amount, _ccy = parsed
                # A stated upcoming cycle is not a permanent change to all future pay.
                future = sorted(e.settlement_date for e in self.dataset.events_by_user.get(message.user_id, [])
                                if e.category == "salary" and e.settlement_date >= request_date
                                and e.status == "scheduled")
                from buy_or_wait.finance.recurrence import detect_recurring_series, project_series_dates
                from datetime import timedelta
                for series in detect_recurring_series(self.dataset.events_by_user.get(message.user_id, []),
                                                       request_date, self.settings.recurrence):
                    if series.category == "salary" and series.direction == "credit":
                        anchor = self.dataset.events_by_id[series.template_event_id].settlement_date
                        future.extend(project_series_dates(request_date, request_date + timedelta(days=40),
                                      series.cadence_days, anchor, monthly=series.monthly, anchor_day=series.anchor_day))
                next_cycle = min(future) if future else effective
                cycle_only = any(p in lower for p in ("next salary", "next payroll", "affected pay cycle"))
                if "reduced" in lower or "temporary" in lower or "sementara" in lower:
                    ctx.income_patches.append(
                        IncomeSchedulePatch(
                            category="salary",
                            amount=amount,
                            effective_from=effective or request_date,
                            effective_until=next_cycle if cycle_only else None,
                            currency=_ccy or None,
                        )
                    )
                elif "naik" in lower or "increases" in lower or "confirmed" in lower or "dikonfirmasi" in lower:
                    ctx.income_patches.append(
                        IncomeSchedulePatch(
                            category="salary",
                            amount=amount,
                            effective_from=effective or request_date,
                            currency=_ccy or None,
                            resume_from=effective if "resumes" in lower else None,
                        )
                    )
                elif "resumes" in lower or "confirmed for" in lower:
                    ctx.income_patches.append(
                        IncomeSchedulePatch(
                            category="salary",
                            amount=amount,
                            effective_from=effective or request_date,
                            resume_from=effective,
                            currency=_ccy or None,
                        )
                    )
                ctx.notes.append(f"salary patch {message.message_id}")

        if message.related_event_id and "cancel" in lower and not any(p in lower for p in ("not cancel", "not been cancel")):
            ongoing = bool(re.search(r"(?:subscription|membership|standing order|recurring (?:payment|bill)|contract)\s+(?:(?:has been|is|was)\s+)?cancel", lower)
                           or re.search(r"cancel(?:led|ed)?\s+(?:the |my |your )?(?:subscription|membership|standing order)", lower)
                           or "no future charges" in lower or "no further payments" in lower)
            ctx.event_patches[message.related_event_id] = EventPatch(
                event_id=message.related_event_id,
                cancel=True,
                cancel_scope="series" if ongoing else "occurrence",
                cancel_from=(_parse_date(text) or datetime.fromisoformat(message.sent_at.replace("Z", "+00:00")).date()) if ongoing else None,
            )
        if message.related_event_id and any(p in lower for p in ("settled", "has been credited", "payment posted")):
            ctx.event_patches[message.related_event_id] = EventPatch(
                event_id=message.related_event_id, status="settled", settlement_date=_parse_date(text))
        if message.related_event_id and any(p in lower for p in ("delayed", "rescheduled", "postponed")):
            revised = _parse_date(text)
            if revised:
                ctx.event_patches[message.related_event_id] = EventPatch(
                    event_id=message.related_event_id, settlement_date=revised)

        if (
            self.settings.llm_enabled
            and not self.settings.deterministic_mode
            and message.related_event_id
            and message.related_event_id not in ctx.event_patches
        ):
            llm_patch = self._llm_message_facts(message)
            ctx = ctx.merge(llm_patch)

        return ctx

    def _llm_message_facts(self, message: MessageRow) -> EvidenceContext:
        from buy_or_wait.llm.azure_client import AzureEvidenceClient

        source_hash = __import__("hashlib").sha256(
            repr((message.message_text, message.user_id, message.related_event_id, message.sent_at,
                  self.settings.azure_chat_deployment)).encode()).hexdigest()
        cached = self.cache.read("message", message.message_id, source_hash)
        if cached and cached.get("facts"):
            from buy_or_wait.llm.usage import UsageTracker
            UsageTracker.instance().cache_hit("message", source_hash)
            return self._facts_to_context(cached["facts"], message)

        client = AzureEvidenceClient(self.settings)
        facts = client.extract_message_facts(message.message_text, message.message_id)
        if facts.get("facts"):
            self.cache.write("message", message.message_id, source_hash, {"facts": facts})
        return self._facts_to_context(facts, message)

    def _facts_to_context(self, facts: dict, message: MessageRow) -> EvidenceContext:
        ctx = EvidenceContext()
        for fact in facts.get("facts", []):
            event_id = fact.get("event_id") or message.related_event_id
            if not event_id:
                continue
            event = self.dataset.events_by_id.get(event_id)
            if (event is None or event.user_id != message.user_id or
                    event_id != message.related_event_id):
                continue
            if fact.get("type") == "cancel":
                ctx.event_patches[event_id] = EventPatch(event_id=event_id, cancel=True)
            elif fact.get("type") in {"amount", "amendment", "settlement", "confirm"} and fact.get("amount") is not None:
                try:
                    amount = Decimal(str(fact["amount"]))
                    if amount.is_finite() and amount >= 0 and fact.get("currency") in {None, "", event.currency}:
                        ctx.event_patches[event_id] = EventPatch(event_id, amount=amount, explicit=False)
                except InvalidOperation:
                    pass
        return ctx
