"""Transcribe speech and write"""

def transcribe(path, model_size="medium", language=None, words=False):
    """Return (segments, detected_language) using faster-whisper on the CPU."""
    from faster_whisper import WhisperModel
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        path,
        language=language,
        vad_filter=True,
        vad_parameters=dict(
            speech_pad_ms=100,           # was 400: less padding added before speech
            min_silence_duration_ms=500, # was 2000: split at pauses of half a second
        ),
        word_timestamps=words,
)
    return list(segments), info.language

def format_timestamp(seconds):
    """acurate SRT time format"""
    ms = int(round(seconds * 1000))
    hours, ms = divmod(ms, 3_600_000)
    minutes, ms = divmod(ms, 60_000)
    secs, ms = divmod(ms, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"


def write_srt(segments, srt_path):
    """Write segments into an .srt file."""
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            f.write(f"{i}\n")
            f.write(f"{format_timestamp(seg.start)} --> {format_timestamp(seg.end)}\n")
            f.write(f"{seg.text.strip()}\n\n")

def all_words(segments):
    """Flatten the per-segment words into one list (need words = True)"""
    return [w for seg in segments for w in seg.words]