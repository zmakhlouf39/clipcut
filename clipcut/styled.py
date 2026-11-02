"""Customizable word-by-word caption, written as an .ass subtitle file."""

import subprocess
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

ANIMATIONS = {
    "none": "",
    "fade": r"{\fad(120,0)}",
    "pop": r"{\fad(60,0)\fscx70\fscy70\t(0,120,\fscx100\fscy100)}",
    "bounce": r"{\fscx60\fscy60\t(0,90,\fscx115\fscy115)\t(90,160,\fscx100\fscy100)}",
}

POSITIONS = {"bottom": 2, "middle": 5, "top": 8}

#--------------------------------helpers--------------------------------------------

def ass_time(seconds):
    """Turn 75.5 into '0:01:15.50' (ASS uses centiseconds)."""
    cs = round(seconds * 100)
    hours, cs = divmod(cs, 360_000)
    minutes, cs = divmod(cs, 6_000)
    secs, cs = divmod(cs, 100)
    return f"{hours}:{minutes:02}:{secs:02}.{cs:02}"

def ass_color(rrggbb):
    """ASS writes colors blue-green-red: 'FF0000' (red) becomes '&H000000FF'."""
    r, g, b = rrggbb[0:2], rrggbb[2:4], rrggbb[4:6]
    return f"&H00{b}{g}{r}".upper()

def group_words(words, n):
    """technically independent but we using captions.py:all_words"""
    captions = []
    for i in range(0, len(words), n):
        chunk = words[i:i + n]
        text = " ".join(w.word.strip() for w in chunk)
        captions.append((chunk[0].start, chunk[-1].end, text))
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
