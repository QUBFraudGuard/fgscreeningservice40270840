import country_check


def test_country_on_blocklist():
    result = country_check.check({"country": "ES"})
    assert result == {"reason": "country ES is restricted"}


def test_country_not_on_blocklist():
    result = country_check.check({"country": "US"})
    assert result is None


def test_lc_country_on_blocklist():
    result = country_check.check({"country": "ir"})
    assert result == {"reason": "country IR is restricted"}


def test_missing_country_key_does_not_crash():
    result = country_check.check({})
    assert result is None