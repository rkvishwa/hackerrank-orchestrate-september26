from buy_or_wait.evidence.models import AmountRole


def infer_amount_role(description: str, direction: str, status: str) -> AmountRole:
    desc = description.lower()
    if "net salary" in desc or "payroll" in desc and direction == "credit":
        return "net_pay"
    if "outstanding" in desc or "balance due" in desc or "payable" in desc:
        return "balance_due"
    if "due" in desc and status in {"pending", "scheduled"}:
        return "amount_due"
    if "fare" in desc or "taxi" in desc:
        return "total_fare"
    if direction == "debit":
        return "invoice_total"
    return "unknown"
