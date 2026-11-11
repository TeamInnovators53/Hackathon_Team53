"""
Unit tests for GoogleTTSService.
"""

from src.google_tts_service import GoogleTTSService


def test_clean_text_for_speech():
    raw = "**Hello** Eleanor Vance! [K2U_ENG.700.au] Your balance is $25,000.50. `Check` details."
    cleaned = GoogleTTSService.clean_text_for_speech(raw)
    assert "**" not in cleaned
    assert "[K2U_ENG.700.au]" not in cleaned
    assert "`" not in cleaned
    assert "dollars" in cleaned
    assert "Eleanor Vance" in cleaned


def test_split_into_chunks():
    short_text = "Welcome to KeyBank."
    chunks = GoogleTTSService.split_into_chunks(short_text, max_chars=180)
    assert len(chunks) == 1
    assert chunks[0] == short_text

    long_text = "Sentence one is clear and simple. Sentence two is also quite informative and provides additional context for the caller. Sentence three wraps up the guidance with fee avoidance instructions."
    chunks2 = GoogleTTSService.split_into_chunks(long_text, max_chars=80)
    assert len(chunks2) > 1
    for c in chunks2:
        assert len(c) <= 80
