from clipcut.silence import keep_segments

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