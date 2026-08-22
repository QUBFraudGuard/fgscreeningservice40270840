import os

# protect against input with spaces after comma and empty string

BLOCKED_COUNTRIES = set(
    c.strip().upper() for c in os.environ.get("BLOCKED_COUNTRIES", "ES,IR,FR").split(",") if c.strip()
)

def check(transaction):

    country = transaction.get("country", "").strip().upper()

    if country in BLOCKED_COUNTRIES:
        return {"reason": f"country {transaction['country']} is restricted"}
    return None