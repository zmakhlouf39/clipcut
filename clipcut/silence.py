"""Finds silent parts in a video and cuts them off"""
import re    # regex handling
import subprocess # cli :)

def get_duration(path): 
    # Return the length of a media file in seconds
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
         "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())

def detect_silences(path, duration, noise_db=-30, min_silence=0.5):
    # Return a list of (start, end) times where the audio is silent.
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", path, "-af", f"silencedetect=noise={noise_db}dB:d={min_silence}",
         "-f", "null", "-"],
         capture_output=True, text=True,  
    )
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", result.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", result.stderr)]

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

def cut_video(path, segments, out_path): # cutting the video
    expr = "+".join(f"between(t,{s:.3f},{e:.3f})" for s, e in segments)
    subprocess.run(
        ["ffmpeg", "-y", "hide_banner", "-loglevel", "error", "-i", path,
         "-vf", f"select='{expr}',setpts=N/FRAME_RATE/TB",
         "-af", f"select='{expr}',asetpts=N/SR/TB",
         out_path],
         check=True,
    )