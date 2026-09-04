import os


raw = os.environ.get("BLOCKED_CARDS", "9999,0000,1111,6666")
BLOCKED_CARDS = set(card.strip() for card in raw.split(",") if card.strip())

def check(transaction):
    if transaction.get("card", "") in BLOCKED_CARDS:
        return {"reason": "card on blocklist"}
    return None