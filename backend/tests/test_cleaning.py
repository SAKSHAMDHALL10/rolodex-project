from app.services.cleaning import clean_profile_text


def test_removes_nav_chrome():
    raw = """Skip to main content
Home My Network Jobs Messaging Notifications

Priya Shenoy
Senior Backend Engineer
Follow  Connect  Message
About
I build backend systems.
"""
    cleaned = clean_profile_text(raw)
    assert "Skip to main content" not in cleaned
    assert "Home" not in cleaned.splitlines()
    assert "Priya Shenoy" in cleaned
    assert "I build backend systems." in cleaned


def test_removes_duplicate_adjacent_lines():
    raw = "Priya Shenoy\nPriya Shenoy\nEngineer"
    cleaned = clean_profile_text(raw)
    assert cleaned.count("Priya Shenoy") == 1


def test_empty_input_returns_empty_string():
    assert clean_profile_text("") == ""
    assert clean_profile_text(None) == ""


def test_collapses_excess_blank_lines():
    raw = "Line one\n\n\n\n\nLine two"
    cleaned = clean_profile_text(raw)
    assert "\n\n\n" not in cleaned
