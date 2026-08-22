import full_screening
THRESHOLD = 10000


def test_malformed_card():
    result = full_screening.validate_fields("CARD", "UK")
    assert result == "invalid card format: CARD"


def test_malformed_country():
    result = full_screening.validate_fields("1111", "usa")
    assert result == "invalid country format: usa"


def test_valid_fields_pass():
    result = full_screening.validate_fields("1111", "UK")
    assert result is None


def test_missing_card():
    result = full_screening.validate_fields("", "UK")
    assert result == "invalid card format: missing"


def test_missing_country():
    result = full_screening.validate_fields("1111", "")
    assert result == "invalid country format: missing"

def test_transaction_triggers_2_tests():
    result = full_screening.validate_fields("1111", "")
    assert result == "invalid country format: missing"

def test_orchestrator_passes_through_screening_py_error():
    result = full_screening.screen_transaction_full("abc-1234-UK", THRESHOLD)

    assert result["decision"] == "ERROR"
    assert result["reason"] == "amount is not numeric"


def test_multiple_checks_triggered_stops_at_first_match():
    result = full_screening.screen_transaction_full("500-9999-ES", THRESHOLD)

    assert result["decision"] == "SUSPICIOUS"
    assert result["reason"] == "card on blocklist"


def test_batch_mixes_ok_suspicious_and_error():
    items = ",".join([
        "5000-1234-UK",      # OK
        "50000-1234-UK",     # SUSPICIOUS - amount
        "500-9999-UK",       # SUSPICIOUS - blocklist
        "500-1234-KP",       # SUSPICIOUS - country
        "abc-1234-UK",       # ERROR - non-numeric amount
        "5000-CARD-UK",      # ERROR - invalid card format
    ])

    out = full_screening.screen_batch_full(items, THRESHOLD)

    assert out["total_checked"] == 6
    assert out["flagged"] == 3  # only SUSPICIOUS count toward "flagged"

    decisions = [r["decision"] for r in out["results"]]
    assert decisions == [
        "OK", "SUSPICIOUS", "SUSPICIOUS", "SUSPICIOUS", "ERROR", "ERROR",
    ]


def test_empty_batch():
    out = full_screening.screen_batch_full("", THRESHOLD)

    assert out["total_checked"] == 0
    assert out["flagged"] == 0
    assert out["results"] == []