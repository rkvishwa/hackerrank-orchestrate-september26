from __future__ import annotations

import csv
import hashlib
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from buy_or_wait.domain import REQUEST_TYPES


def _parse_date(value: str, fallback: str | None = None) -> date:
    value = (value or "").strip()
    if value:
        return date.fromisoformat(value)
    if fallback:
        return date.fromisoformat(fallback.strip())
    raise ValueError("Missing date value")


def _parse_decimal(value: str) -> Decimal | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def _split_pipe(value: str) -> list[str]:
    return [part.strip() for part in (value or "").split("|") if part.strip()]


@dataclass
class Profile:
    user_id: str
    home_currency: str
    current_available_balance: Decimal
    minimum_balance_to_keep: Decimal
    financial_priorities: list[str]
    expense_categories_to_protect: list[str]
    expense_categories_user_is_willing_to_reduce: list[str]
    expense_categories_user_is_willing_to_stop: list[str]
    payment_methods_user_will_consider: list[str]
    max_installment_months: int | None


@dataclass
class FinancialEvent:
    event_id: str
    user_id: str
    event_type: str
    description: str
    category: str
    direction: str
    amount: Decimal | None
    currency: str
    event_date: date
    settlement_date: date
    status: str
    linked_event_id: str
    flexibility: str
    minimum_allowed_amount: Decimal | None


@dataclass
class RequestRow:
    request_id: str
    user_id: str
    request_date: date
    request_type: str
    requested_amount: Decimal
    desired_completion_date: date
    allows_partial_payment: bool
    request_text: str


@dataclass
class PaymentOption:
    payment_option_id: str
    request_id: str
    payment_method: str
    payment_amount: Decimal
    number_of_payments: int
    first_payment_date: date
    payment_frequency_days: int | None
    financing_fee: Decimal
    total_payable_amount: Decimal


@dataclass
class MessageRow:
    message_id: str
    user_id: str
    request_id: str
    related_event_id: str
    sent_at: str
    source_type: str
    message_text: str


@dataclass
class ImageRow:
    image_id: str
    user_id: str
    request_id: str
    related_event_id: str


@dataclass
class ExchangeRate:
    rate_date: date
    from_currency: str
    to_currency: str
    rate: Decimal


@dataclass
class Dataset:
    version_hash: str
    profiles: dict[str, Profile]
    events_by_user: dict[str, list[FinancialEvent]]
    events_by_id: dict[str, FinancialEvent]
    requests: list[RequestRow]
    requests_by_id: dict[str, RequestRow]
    payment_options_by_request: dict[str, list[PaymentOption]]
    messages_by_user: dict[str, list[MessageRow]]
    messages_by_request: dict[str, list[MessageRow]]
    images_by_event: dict[str, ImageRow]
    images_by_id: dict[str, ImageRow]
    exchange_rates: list[ExchangeRate]
    media_dir: Path = field(default_factory=Path)


def _hash_dataset(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()[:16]


def load_dataset(dataset_dir: Path) -> Dataset:
    paths = [
        dataset_dir / "financial_profiles.csv",
        dataset_dir / "financial_events.csv",
        dataset_dir / "requests.csv",
        dataset_dir / "request_payment_options.csv",
        dataset_dir / "exchange_rates.csv",
        dataset_dir / "messages.csv",
        dataset_dir / "images.csv",
    ]
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f"Missing dataset file: {path}")

    profiles: dict[str, Profile] = {}
    with (dataset_dir / "financial_profiles.csv").open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            max_months = row["max_installment_months"].strip()
            profiles[row["user_id"]] = Profile(
                user_id=row["user_id"],
                home_currency=row["home_currency"],
                current_available_balance=Decimal(row["current_available_balance"]),
                minimum_balance_to_keep=Decimal(row["minimum_balance_to_keep"]),
                financial_priorities=_split_pipe(row["financial_priorities"]),
                expense_categories_to_protect=_split_pipe(row["expense_categories_to_protect"]),
                expense_categories_user_is_willing_to_reduce=_split_pipe(
                    row["expense_categories_user_is_willing_to_reduce"]
                ),
                expense_categories_user_is_willing_to_stop=_split_pipe(
                    row["expense_categories_user_is_willing_to_stop"]
                ),
                payment_methods_user_will_consider=_split_pipe(row["payment_methods_user_will_consider"]),
                max_installment_months=int(max_months) if max_months else None,
            )

    events_by_user: dict[str, list[FinancialEvent]] = defaultdict(list)
    events_by_id: dict[str, FinancialEvent] = {}
    with (dataset_dir / "financial_events.csv").open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            event = FinancialEvent(
                event_id=row["event_id"],
                user_id=row["user_id"],
                event_type=row["event_type"],
                description=row["description"],
                category=row["category"],
                direction=row["direction"],
                amount=_parse_decimal(row["amount"]),
                currency=row["currency"],
                event_date=_parse_date(row["event_date"]),
                settlement_date=_parse_date(row["settlement_date"], row["event_date"]),
                status=row["status"],
                linked_event_id=(row.get("linked_event_id") or "").strip(),
                flexibility=row["flexibility"],
                minimum_allowed_amount=_parse_decimal(row.get("minimum_allowed_amount", "")),
            )
            events_by_user[event.user_id].append(event)
            events_by_id[event.event_id] = event

    requests: list[RequestRow] = []
    requests_by_id: dict[str, RequestRow] = {}
    with (dataset_dir / "requests.csv").open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if row["request_type"] not in REQUEST_TYPES:
                raise ValueError(f"Invalid request_type: {row['request_type']}")
            req = RequestRow(
                request_id=row["request_id"],
                user_id=row["user_id"],
                request_date=_parse_date(row["request_date"]),
                request_type=row["request_type"],
                requested_amount=Decimal(row["requested_amount"]),
                desired_completion_date=_parse_date(row["desired_completion_date"]),
                allows_partial_payment=row["allows_partial_payment"].strip().lower() == "true",
                request_text=row["request_text"],
            )
            requests.append(req)
            requests_by_id[req.request_id] = req

    payment_options_by_request: dict[str, list[PaymentOption]] = defaultdict(list)
    with (dataset_dir / "request_payment_options.csv").open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            freq = row["payment_frequency_days"].strip()
            option = PaymentOption(
                payment_option_id=row["payment_option_id"],
                request_id=row["request_id"],
                payment_method=row["payment_method"],
                payment_amount=Decimal(row["payment_amount"]),
                number_of_payments=int(row["number_of_payments"]),
                first_payment_date=_parse_date(row["first_payment_date"]),
                payment_frequency_days=int(freq) if freq else None,
                financing_fee=Decimal(row["financing_fee"]),
                total_payable_amount=Decimal(row["total_payable_amount"]),
            )
            payment_options_by_request[option.request_id].append(option)

    for request_id, options in payment_options_by_request.items():
        if not (2 <= len(options) <= 4):
            raise ValueError(f"Request {request_id} has {len(options)} payment options")

    messages_by_user: dict[str, list[MessageRow]] = defaultdict(list)
    messages_by_request: dict[str, list[MessageRow]] = defaultdict(list)
    with (dataset_dir / "messages.csv").open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            msg = MessageRow(
                message_id=row["message_id"],
                user_id=row["user_id"],
                request_id=(row.get("request_id") or "").strip(),
                related_event_id=(row.get("related_event_id") or "").strip(),
                sent_at=row["sent_at"],
                source_type=row["source_type"],
                message_text=row["message_text"],
            )
            messages_by_user[msg.user_id].append(msg)
            if msg.request_id:
                messages_by_request[msg.request_id].append(msg)

    images_by_event: dict[str, ImageRow] = {}
    images_by_id: dict[str, ImageRow] = {}
    with (dataset_dir / "images.csv").open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            image = ImageRow(
                image_id=row["image_id"],
                user_id=row["user_id"],
                request_id=(row.get("request_id") or "").strip(),
                related_event_id=row["related_event_id"],
            )
            images_by_event[image.related_event_id] = image
            images_by_id[image.image_id] = image

    exchange_rates: list[ExchangeRate] = []
    with (dataset_dir / "exchange_rates.csv").open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            exchange_rates.append(
                ExchangeRate(
                    rate_date=_parse_date(row["rate_date"]),
                    from_currency=row["from_currency"],
                    to_currency=row["to_currency"],
                    rate=Decimal(row["rate"]),
                )
            )

    return Dataset(
        version_hash=_hash_dataset(paths),
        profiles=profiles,
        events_by_user=dict(events_by_user),
        events_by_id=events_by_id,
        requests=requests,
        requests_by_id=requests_by_id,
        payment_options_by_request=dict(payment_options_by_request),
        messages_by_user=dict(messages_by_user),
        messages_by_request=dict(messages_by_request),
        images_by_event=images_by_event,
        images_by_id=images_by_id,
        exchange_rates=exchange_rates,
        media_dir=dataset_dir / "media" / "images",
    )


def normalize_description(description: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", description.lower()).strip()
