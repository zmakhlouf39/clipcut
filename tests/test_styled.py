from collections import namedtuple

import pytest

from clipcut.styled import Style, ass_time, ass_color, group_words, build_ass
Word = namedtuple("Word", "start end word")

WORDS = [Word(0.0, 0.4, " Hello"), Word(0.4, 0.9, " there"), Word(1.0, 1.5, " friend")]

def test_time_format():
    assert ass_time(0) == "0:00:00.00"
    assert ass_time(1986) == "0:33:06.00"

def test_color_format():
    assert ass_color("FF0000") == "&H000000FF"
    assert ass_color("12ab34") == "&H0034AB12"

def test_group_one_word():
    assert group_words(WORDS, 1) == [(0.0, 0.4, "Hello"), (0.4, 0.9, "there"), (1.0, 1.5, "friend")]

def test_group_two_words_keeps_leftover():
    assert group_words(WORDS, 2) == [(0.0, 0.9, "Hello there"), (1.0, 1.5, "friend")]

def test_build_ass_has_style_and_lines():
    style = Style(font="Impact", size=90, animation="none", uppercase=True)
    text = build_ass(group_words(WORDS, 1), style, 1080, 1920)
    assert "Style: Default,Impact,90," in text
    assert "PlayResY: 1920" in text
    assert "Dialogue: 0,0:00:00.00,0:00:00.40,Default,,0,0,0,,HELLO" in text
    assert text.count("Dialogue:") == 3


def test_build_ass_rejects_unknown_animation():
    with pytest.raises(ValueError):
        build_ass([], Style(animation="spin"), 1080, 1920)