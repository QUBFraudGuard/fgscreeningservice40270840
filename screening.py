# ============================================================================
# screening.py  —  THE ACTUAL FRAUD CHECK
# ============================================================================
#
# This is the heart of the whole app. It is the ONLY file that makes a real
# decision about a transaction. Everything else (app.py, the web page) just
# moves data around so that these two functions can run.
#
# What does it do?  It looks at each transaction and decides:
#     - "OK"          -> the amount looks normal
#     - "SUSPICIOUS"  -> the amount is bigger than a limit we set (the threshold)
#     - "ERROR"       -> the transaction was typed wrongly, so we can't check it
#
# A transaction is just a piece of text shaped like:  amount-card-country
# For example:  5000-1234-UK   means  amount=5000, card=1234, country=UK
#
# "Stateless" means this code remembers NOTHING between calls. There is no
# database and no saved file. Give it the same input and you always get the
# same output. That makes it easy to reason about and easy to scale later.
#
# NOTE For Task A: there is exactly ONE check here on purpose
# (amount over a threshold). Adding more checks — a banned-card list, a country
# rule, etc. — is YOUR job in the assignment. Do not add them to this file.
# ============================================================================


def screen_transaction(raw, threshold):
    """Check ONE transaction and return a small dictionary describing it.

    `raw`       : the transaction text, e.g. "5000-1234-UK"
    `threshold` : the amount limit; anything above this is flagged

    We never crash on bad input. If the text is wrong, we return an "ERROR"
    result instead of raising an exception, so a single bad transaction does
    not stop the rest of the batch from being checked.
    """

    # Step 1: split the text on the "-" characters.
    # "5000-1234-UK" becomes the list ["5000", "1234", "UK"].
    parts = raw.split("-")

    # Step 2: a correct transaction must have exactly 3 parts.
    # If not, it was typed wrongly -> report an ERROR and stop here.
    if len(parts) != 3:
        return {
            "transaction": raw,
            "decision": "ERROR",
            "reason": "expected amount-card-country",
        }

    # Step 3: give the three parts friendly names.
    # The "_" in front of _card and _country is a Python convention meaning
    # "we are not using this value right now" (only the amount matters here).
    amount_str, _card, _country = parts

    # Step 4: the amount must be a number. "5000" is fine, "abc" is not.
    # float() turns the text into a number; if it can't, it raises ValueError,
    # which we catch and turn into a friendly ERROR result.
    try:
        amount = float(amount_str)
    except ValueError:
        return {
            "transaction": raw,
            "decision": "ERROR",
            "reason": "amount is not numeric",
        }

    # Step 5: THE ONE CHECK. Is the amount bigger than the threshold?
    # If yes, flag it as SUSPICIOUS. (Exactly equal is NOT flagged.)
    if amount > threshold:
        return {
            "transaction": raw,
            "decision": "SUSPICIOUS",
            "reason": "amount over threshold",
        }

    # Step 6: it passed the check, so it's OK.
    return {"transaction": raw, "decision": "OK"}


def screen_batch(items, threshold):
    """Check a WHOLE BATCH of transactions separated by commas.

    `items` : the text from the request, e.g. "5000-1234-UK,50000-9999-UK"
    Returns a dictionary with three things:
        results       -> a list, one decision per transaction
        total_checked -> how many transactions we looked at
        flagged       -> how many were SUSPICIOUS
    """

    # Split the batch on commas into single transactions.
    # The "if t != ''" part throws away empty pieces, which can appear if the
    # text has a stray comma (e.g. "5000-1234-UK,," would give an empty piece).
    # If `items` is empty, we just use an empty list (nothing to check).
    transactions = [t for t in items.split(",") if t != ""] if items else []

    # Check every transaction by calling screen_transaction on each one.
    results = [screen_transaction(t, threshold) for t in transactions]

    # Count how many came back as SUSPICIOUS.
    flagged = sum(1 for r in results if r["decision"] == "SUSPICIOUS")

    # Bundle everything into the response shape the rest of the app expects.
    return {
        "results": results,
        "total_checked": len(results),
        "flagged": flagged,
    }
