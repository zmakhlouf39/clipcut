"""Customizable word-by-word caption, written as an .ass subtitle file."""

import subprocess
import os
from dataclasses import dataclass


#-------------------------------setup-------------------------------------

@dataclass
class Style:
    font: str = "Arial"
    size: int = 80
    color: str = "FFFFFF"       
    outline_color : str = "000000"
    outline : int = 5           # outline thickness
    words_per_caption: int = 1
    animation: str = "pop"
    position: str = "middle"    #"top", "middle" or "bottom"
    uppercase: bool = True
    remove_punctuation: bool = False
ANIMATIONS = {
    "none": "",
    "fade": r"{\fad(120,0)}",
    "pop": r"{\fad(60,0)\fscx70\fscy70\t(0,120,\fscx100\fscy100)}",
    "bounce": r"{\fscx60\fscy60\t(0,90,\fscx115\fscy115)\t(90,160,\fscx100\fscy100)}",
}

POSITIONS = {"bottom": 2, "middle": 5, "top": 8}

PUNCTUATION = ",.!?;:…"

#--------------------------------helpers--------------------------------------------

def ass_time(seconds):
    """Turn 75.5 into '0:01:15.50' (ASS uses centiseconds)."""
    cs = round(seconds * 100)
    hours, cs = divmod(cs, 360_000) 
    minutes, cs = divmod(cs, 6_000)
    secs, cs = divmod(cs, 100)
    return f"{hours}:{(minutes):02}:{(secs):02}.{cs:02}"

def ass_color(rrggbb):
    """ASS writes colors blue-green-red: 'FF0000' (red) becomes '&H000000FF'."""
    r, g, b = rrggbb[0:2], rrggbb[2:4], rrggbb[4:6]
    return f"&H00{b}{g}{r}".upper()

def clean_word(word, remove_punctuation):
    """Trim spaces, and optionally punctuation at the edges of the word."""
    word = word.strip()
    return word.strip(PUNCTUATION) if remove_punctuation else word

def group_words(words, n, remove_punctuation=False):
    """technically independent but we using captions.py:all_words"""
    cleaned = [(w.start, w.end, clean_word(w.word, remove_punctuation)) for w in words]
    cleaned = [c for c in cleaned if c[2]]
    captions = []
    for i in range(0, len(cleaned), n):
        chunk = cleaned[i:i + n]
        captions.append((chunk[0][0], chunk[-1][1], " ".join(text for _, _, text in chunk)))
    return captions

def get_resolution(video_path):
    """Return (width, height) of the video's first video stream."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0", video_path],
        capture_output=True, text=True, check=True,
    ).stdout
    width, height = out.strip().split(",")[:2]
    return int(width), int(height)
#---------------------------main work------------------------------------------

def build_ass(captions, style, width, height):
    """Return the .ass file"""

    if style.animation not in ANIMATIONS:
        raise ValueError(f"unknown animation {style.animation!r}, pick one of {list(ANIMATIONS)}")
    if style.position not in POSITIONS:
        raise ValueError(f"unknown position {style.position!r}, pick one of {list(POSITIONS)}")
    margin_v = height // 8
    header = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        f"PlayResX: {width}\n"
        f"PlayResY: {height}\n"
        "\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,{style.font},{style.size},{ass_color(style.color)},&H000000FF,"
        f"{ass_color(style.outline_color)},&H00000000,1,0,0,0,100,100,0,0,1,"
        f"{style.outline},0,{POSITIONS[style.position]},40,40,{margin_v},1\n"
        "\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    effect = ANIMATIONS[style.animation]
    lines = []
    for start, end, text in captions:
        if style.uppercase:
            text = text.upper()
        lines.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Default,,0,0,0,,{effect}{text}")
    return header + "\n".join(lines) + "\n"

def burn_ass(video_path, ass_path, out_path):
    """Draw the styled captions onto the video itself."""
    video_path, ass_path, out_path = (os.path.abspath(p) for p in (video_path, ass_path, out_path))
    subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", video_path,
         "-vf", f"subtitles={os.path.basename(ass_path)}",
         "-c:v", "libx264", "-preset", "veryfast", 
         "-crf", "23",
         "-c:a", "aac",
         out_path],
         check=True, cwd=os.path.dirname(ass_path), # i hate windows, if you are a microsoft recruiter, ignore comment
    )