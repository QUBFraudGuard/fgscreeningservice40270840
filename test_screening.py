# test_screening.py — CI-style tests for the single screening check.
#
# Covers the four cases required 
#   1. a normal batch (mix of OK and SUSPICIOUS),
#   2. the threshold boundary (== threshold is OK, just over is SUSPICIOUS),
#   3. empty input,
#   4. a malformed transaction.
#
# Run with: python -m pytest -q

from screening import screen_batch, screen_transaction

THRESHOLD = 10000


def test_normal_batch():
    # The sample input example 
    items = "5000-1234-UK,50000-9999-UK,200-4321-US,800-0000-CN"
    out = screen_batch(items, THRESHOLD)

    assert out["total_checked"] == 4
    assert out["flagged"] == 1

    decisions = [r["decision"] for r in out["results"]]
    assert decisions == ["OK", "SUSPICIOUS", "OK", "OK"]

    flagged = out["results"][1]
    assert flagged["transaction"] == "50000-9999-UK"
    assert flagged["reason"] == "amount over threshold"


def test_threshold_boundary():
    # Exactly on the threshold is OK; one over is SUSPICIOUS.
    on_threshold = screen_transaction("10000-1111-UK", THRESHOLD)
    assert on_threshold["decision"] == "OK"

    just_over = screen_transaction("10001-1111-UK", THRESHOLD)
    assert just_over["decision"] == "SUSPICIOUS"


def test_empty_input():
    out = screen_batch("", THRESHOLD)
    assert out["results"] == []
    assert out["total_checked"] == 0
    assert out["flagged"] == 0


def test_malformed_transaction_does_not_crash():
    # Missing the country part → ERROR, but the batch still processes.
    items = "5000-1234-UK,not-a-valid,9999-0000-US"
    out = screen_batch(items, THRESHOLD)

    assert out["total_checked"] == 3
    decisions = [r["decision"] for r in out["results"]]
    assert decisions == ["OK", "ERROR", "OK"]
    assert out["results"][1]["reason"]  # has a short reason


def test_non_numeric_amount_is_error():
    out = screen_transaction("abc-1234-UK", THRESHOLD)
    assert out["decision"] == "ERROR"
    assert out["reason"] == "amount is not numeric"
