from rapidfuzz import fuzz

from app.core.config import settings


def test_identical_names_score_100():
    assert fuzz.token_sort_ratio("Priya Shenoy", "Priya Shenoy") == 100


def test_reordered_names_still_match_above_threshold():
    score = fuzz.token_sort_ratio("Shenoy Priya", "Priya Shenoy")
    assert score >= settings.DUPLICATE_NAME_FUZZ_THRESHOLD


def test_different_names_score_low():
    score = fuzz.token_sort_ratio("Priya Shenoy", "Daniel Okafor")
    assert score < settings.DUPLICATE_NAME_FUZZ_THRESHOLD


def test_minor_typo_still_matches():
    score = fuzz.token_sort_ratio("Priya Shenoy", "Priya Shenoi")
    assert score >= settings.DUPLICATE_NAME_FUZZ_THRESHOLD
