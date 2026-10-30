import subprocess

import pytest

from clipcut.silence import get_duration, detect_silences, keep_segments, cut_video 

#------------------fake vid-----------------------------
def make_test_video(path, volume_expr):
    #7.5 second vid
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-f", "lavfi", "-i", "testsrc=size=320x240:rate=25:duration=7.5",
         "-f", "lavfi", "-i", "sine=f=440:d=7.5",
         "-af", f"volume='{volume_expr}':eval=frame",
         "-shortest", "-pix_fmt", "yuv420p", str(path)],
        check=True,
    )
    return str(path)
#---Talking---|--Silence---|--Talking---|-Silence--|
#0------------2------------4------------6---------7.5
@pytest.fixture
def video_with_pauses(tmp_path):
    return make_test_video(tmp_path / "pause.mp4", "if(between(t,2,4)+between(t,6,7.5), 0, 1)")
#return make_test_video(pytest tmp_path creates pause.mp4, if(condition, TRUE, FALSE))

#------------------get_duration-----------------------------------

def test_duration_of_vid(video_with_pauses):
    assert get_duration(video_with_pauses) == pytest.approx(7.5, abs=0.1)

#-----------------detect_silences--------------------------------
def test_detect_silences_finds_both_pauses(video_with_pauses):
    duration = get_duration(video_with_pauses)
    silences = detect_silences(video_with_pauses, duration)
    assert len(silences) == 2
    (s1, e1), (s2, e2) = silences
    assert s1 == pytest.approx(2.0, abs=0.1)
    assert e1 == pytest.approx(4.0, abs=0.1)
    assert s2 == pytest.approx(6.0, abs=0.1)
    assert e2 == pytest.approx(7.5, abs=0.1)

def test_detect_silences_on_talking_only_video(tmp_path):
    path = make_test_video(tmp_path / "talk.mp4", "1")  # volume 1 = never silent
    assert detect_silences(path, get_duration(path)) == []

#--------------------keep_segments-------------------------------
def test_no_silence_keeps_everything():
    assert keep_segments([], duration=10) == [(0.0, 10.0)]

def test_silence_in_the_middle_is_removed():
    segments = keep_segments([(3.0, 5.0)], duration = 10, padding = 0)
    assert segments == [(0.0, 3.0), (5.0, 10.0)]

def test_padding_keeps_a_little_air():
    segments = keep_segments([(3.0, 5.0)], duration=10, padding=0.1)
    assert segments == [(0.0, 3.1), (4.9, 10.0)]

def test_all_silent_video_returns_nothing():
    assert keep_segments([(0.0, 10.0)], duration=10, padding=0) == []

def test_local(video_with_pauses):
    duration = get_duration(video_with_pauses)
    segments = keep_segments(detect_silences(video_with_pauses, duration), duration)
    expected = [(0.0, 2.0), (4.0,6.0)]
    assert len(segments) == len(expected)
    for seg, exp in zip(segments, expected):
        assert seg == pytest.approx(exp, abs=0.3)


#---------------------------cut_video------------------------------

def test_cut_video_output_length_matches_segments(video_with_pauses, tmp_path):
    duration = get_duration(video_with_pauses)
    segments = keep_segments(detect_silences(video_with_pauses, duration), duration)
    out = str(tmp_path / "cut.mp4")
    cut_video(video_with_pauses, segments, out)
    expected = sum(end - start for start, end in segments)
    assert get_duration(out) == pytest.approx(expected, abs=0.3)