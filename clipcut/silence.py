"""Finds silent parts in a video and cuts them off"""
import re    # regex handling
import subprocess # cli :)
import tempfile
from pathlib import Path

def get_duration(path_video): 
    # Return the length of a media file in seconds
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
         "default=noprint_wrappers=1:nokey=1", path_video],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())

def detect_silences(path_video, duration, noise_db=-30, min_silence=0.5):
    #tmp audio file, we dont want to get prompted by an overwite every time
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "audio.wav"
    #running the silence detection on an audio file is much faster actually !!
        subprocess.run(
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", path_video, "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
            str(wav)],
            check = True,
        )
        result = subprocess.run(
            ["ffmpeg", "-hide_banner", "-i", str(wav), "-af",
            f"silencedetect=noise={noise_db}dB:d={min_silence}",
            "-f", "null", "-"],
            capture_output=True, text=True,  
        ).stderr
    # Return a list of (start, end) times where the audio is silent. 
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", result)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", result)]

    if len(starts) > len(ends): # the video ends while still silent
        ends.append(duration)
    return list(zip(starts, ends))

def keep_segments(silences, duration, padding=0.1): # get the inverted segment, the talking
    segments = []
    cursor = 0.0
    for start, end in silences:
        seg_end = min(start + padding, duration)
        if seg_end - cursor > 0.2:
            segments.append((round(cursor, 3), round(seg_end, 3)))
        cursor = max(end - padding, 0.0)
    if duration - cursor > 0.2:
        segments.append((round(cursor, 3), round(duration, 3)))
    return segments

def cut_video(path_video, segments, out_path_video):
    """Write a new video that contains only the given segments."""
    parts = []
    for i, (start, end) in enumerate(segments):
        parts.append(f"[0:v]trim=start={start:.3f}:end={end:.3f},setpts=PTS-STARTPTS[v{i}]")
        parts.append(f"[0:a]atrim=start={start:.3f}:end={end:.3f},asetpts=PTS-STARTPTS[a{i}]")
    joined = "".join(f"[v{i}][a{i}]" for i in range(len(segments)))
    parts.append(f"{joined}concat=n={len(segments)}:v=1:a=1[outv][outa]")

    subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", path_video,
         "-filter_complex", ";".join(parts),
         "-map", "[outv]", "-map", "[outa]", 
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
         "-c:a", "aac", out_path_video],
        check=True,
    )