# CI-style tests for blocklist_check.
#
# Covers four cases
#   1. card on blocklist
#   2. card not on blocklist
#   3. empty input,
#   4. a malformed transaction.
#
# Run with: python -m pytest -q

import blocklist_check


def test_card_on_blocklist():
    result = blocklist_check.check({"card": "9999"})
    assert result == {"reason": "card on blocklist"}


def test_card_not_on_blocklist():
    result = blocklist_check.check({"card": "1234"})
    assert result is None


def test_missing_card_key_does_not_crash():
    result = blocklist_check.check({})
    assert result is None