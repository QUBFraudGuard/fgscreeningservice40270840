
# since we can't edit screening.py, added an orchestrator that can handle all the checks

from screening import screen_transaction
import blocklist_check
import country_check
import reputation_check
import re

CARD_PATTERN = re.compile(r"^\d{4}$")
COUNTRY_PATTERN = re.compile(r"^[A-Z]{2}$")

# malformed or missing input handling for card and country

def validate_fields(card, country):
    if not CARD_PATTERN.match(card):
        return f"invalid card format: {card or 'missing'}"
    if not COUNTRY_PATTERN.match(country):
        return f"invalid country format: {country or 'missing'}"
    return None

def screen_transaction_full(raw, threshold):
    base_result = screen_transaction(raw, threshold)

    if base_result["decision"] != "OK":
        return base_result

    _amount_str, card, country = raw.split("-")

    card = card.strip()
    country = country.strip().upper()

    format_error = validate_fields(card, country)
    if format_error:
        return {"transaction": raw, "decision": "ERROR", "reason": format_error}

    transaction = {"raw": raw, "card": card, "country": country}

    for check_fn in [blocklist_check.check, country_check.check, reputation_check.check]:
        result = check_fn(transaction)
        if result:
            return {"transaction": raw, "decision": "SUSPICIOUS", **result}

    return base_result


def screen_batch_full(items, threshold):
    
    transactions = [t for t in items.split(",") if t != ""] if items else []

    results = [screen_transaction_full(t, threshold) for t in transactions]

    flagged = sum(1 for r in results if r["decision"] == "SUSPICIOUS")

    return {
        "results": results,
        "total_checked": len(results),
        "flagged": flagged,
    }