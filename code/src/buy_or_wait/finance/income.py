"""Associate salary evidence with employment before changing any cash flow.

An association is not a settlement or permission to forecast more income. It
only identifies which historical employment a supplied confirmation describes.
"""
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
import re

from buy_or_wait.ingest.loader import normalize_description


@dataclass(frozen=True)
class IncomeAssociation:
    event_id: str
    matched_series_key: str | None
    candidate_series_keys: tuple[str, ...]
    source_event_ids: tuple[str, ...]
    reason: str

    @property
    def ambiguous(self):
        return self.matched_series_key is None and bool(self.candidate_series_keys)


def employer_identity(description):
    from buy_or_wait.finance.recurrence import PAYROLL_ALIASES
    value = normalize_description(description)
    if value in PAYROLL_ALIASES:
        return ""
    words = re.findall(r"\w+", value)
    # These are roles/payment descriptions, not supplied employer names.
    roles = {"employer", "international", "primary", "second", "household", "income",
             "before", "after", "returning", "from", "leave", "previous", "new", "job",
             "temporary", "assignment", "seasonal", "contract", "peak", "season", "wages",
             "freelance", "milestone", "content", "consulting", "invoice", "independent", "work",
             "design", "application", "project", "website", "client", "retainer", "payment",
             "delivery", "driver", "platform", "payout", "weekly", "app", "earnings", "task",
             "marketplace", "pay"}
    generic = {"next", "confirmed", "salary", "payroll", "credit", "net", "base", "first", "prorated"}
    if set(words) <= roles | generic:
        return ""
    return " ".join(w for w in words if w not in generic)


def associate_income(events, as_of: date, evidence=None):
    from buy_or_wait.finance.recurrence import series_identity, SPECULATIVE
    events = list(events)
    if len({e.user_id for e in events}) > 1:
        raise ValueError("Income association requires one user's records")
    income = sorted([e for e in events if e.category == "salary" and e.direction == "credit"
                     and e.status in {"settled", "scheduled"}
                     and not any(w in e.description.lower() for w in SPECULATIVE)],
                    key=lambda e: (e.settlement_date, e.event_id))
    by_id = {e.event_id: e for e in events}
    history = defaultdict(list)
    assignments = {}
    for event in income:
        if event.status == "settled" and event.settlement_date < as_of:
            key = series_identity(event)
            history[key].append(event)
            assignments[event.event_id] = IncomeAssociation(event.event_id, key, (key,),
                                                             (event.event_id,), "historical employment")
    for event in income:
        if event.event_id in assignments:
            continue
        compatible = {key for key, rows in history.items() if rows[-1].currency == event.currency}
        selected = set()
        reason = "no historical employment identified; explicit occurrence only"
        sources = []
        ancestor = event.linked_event_id
        visited = {event.event_id}
        while ancestor and ancestor not in visited:
            visited.add(ancestor)
            prior = by_id.get(ancestor)
            if prior is None:
                break
            linked = assignments.get(ancestor)
            if linked and linked.matched_series_key in compatible:
                selected = {linked.matched_series_key}
                sources = [ancestor]
                reason = "explicit lifecycle link to employment"
                break
            ancestor = prior.linked_event_id
        if not selected and evidence:
            links = {key for patch in evidence.income_patches
                     if not patch.ambiguous_target and patch.target_event_ids is not None
                     and event.event_id in patch.target_event_ids
                     for key in (patch.target_series_keys or ()) if key in compatible}
            if len(links) == 1:
                selected = links
                reason = "validated scoped income evidence"
        name = employer_identity(event.description)
        if not selected and name:
            selected = {key for key in compatible if any(employer_identity(e.description) == name
                                                          for e in history[key])}
            reason = ("matching named employment" if selected else
                      "different named employment; explicit occurrence only")
        elif not selected:
            # An amount can change. Equal amounts also occur across employers.
            # Neither is evidence of identity. A generic confirmation needs a
            # unique compatible employment; same-day alternatives stay ambiguous.
            same_day = {key for key in compatible
                        if event.settlement_date.day in {e.settlement_date.day for e in history[key][-3:]}}
            selected = same_day or compatible
            reason = "unique compatible unnamed confirmation"
        if len(selected) > 1:
            reason = "ambiguous confirmation; no employment amendment or new recurrence"
        elif not selected and not name:
            reason = "no historical employment identified; explicit occurrence only"
        if not sources:
            sources = [e.event_id for key in sorted(selected) for e in history[key]]
        assignments[event.event_id] = IncomeAssociation(
            event.event_id, next(iter(selected)) if len(selected) == 1 else None,
            tuple(sorted(selected)), tuple(sorted(sources)), reason)
    return assignments


def income_target_key(event, associations):
    """Explicit occurrences may be amended even when employment is unknown."""
    from buy_or_wait.finance.recurrence import series_identity
    match = associations.get(event.event_id)
    if match and match.matched_series_key:
        return match.matched_series_key
    if match:
        return f"credit|salary|{event.currency}|explicit income event {event.event_id}"
    return series_identity(event)


def select_income_targets(events, associations, allowed_keys, *, linked_event_id="",
                          currency=None, subject="", quote=""):
    """One targeting policy for prepared facts and the deterministic fallback."""
    if linked_event_id:
        linked = next((e for e in events if e.event_id == linked_event_id), None)
        return {income_target_key(linked, associations)} if linked else set()
    compatible = [e for e in events if not currency or e.currency == currency]
    allowed = {income_target_key(e, associations) for e in compatible} & set(allowed_keys)
    name = employer_identity(subject)
    named = {income_target_key(e, associations) for e in compatible
             if (name and name == employer_identity(e.description)) or
             normalize_description(e.description) in normalize_description(quote)}
    # A named employer absent from this user's records must not target everyone.
    if name and not named:
        unnamed = {income_target_key(e, associations) for e in compatible
                   if not employer_identity(e.description)} & allowed
        return unnamed if len(unnamed) == 1 and len(allowed) == 1 else set()
    return named or allowed


def income_scope_event_ids(events, associations, selected, *, linked_event_id=""):
    if len(selected) != 1:
        return ()
    return tuple(sorted(e.event_id for e in events
                        if e.event_id == linked_event_id or
                        income_target_key(e, associations) in selected))
