from pathlib import Path
from types import SimpleNamespace

import pytest

from clipcut.captions import transcribe, format_timestamp, write_srt, all_words

SAMPLE = Path(__file__).parent / ".." / "samples" / "Lizzie.wav"

#--------------------------transcribe----------------------------------------
@pytest.mark.slow
def test_transcribe_finds_the_words():
    segments, language = transcribe(str(SAMPLE), model_size="tiny", words=True)
    text = " ".join(s.text for s in segments).lower()
    assert language == "en"
    assert "let's talk about how i manage my time and how you can too." in text

#--------------------------format_timestamp------------------------------------

def test_format_is_formatting():

    assert format_timestamp(0) == "00:00:00,000"
    assert format_timestamp(75.5) == "00:01:15,500"
    assert format_timestamp(3661.042) == "01:01:01,042"

#-------------------------write_srt---------------------------------------------

def test_write_srt(tmp_path):
    segments = [
        SimpleNamespace(start=0.0, end=1.5, text=" Hello everyone "),
        SimpleNamespace(start=1.5, end=3.0, text="Welcome to clipcut"),
    ]
    srt = tmp_path / "out.srt"
    write_srt(segments, srt)
    assert srt.read_text(encoding="utf-8") == (
        "1\n00:00:00,000 --> 00:00:01,500\nHello everyone\n\n"
        "2\n00:00:01,500 --> 00:00:03,000\nWelcome to clipcut\n\n"
    )

#----------------------------all_words-------------------------------------------

@pytest.mark.slow
def test_word_timings_are_ordered():
    segments, _ = transcribe(str(SAMPLE), model_size="tiny", words=True)
    words = all_words(segments)

    assert words, "expected at least one word"
    for w in words:
        assert w.start <= w.end, f"bad timing for {w.word!r}: {w.start} > {w.end}"