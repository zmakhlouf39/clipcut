import subprocess
import pytest
from clipcut.captions import burn_ass
from clipcut.silence import get_duration
from pathlib import Path
MINIMAL_ASS = r"""[Script Info]
ScriptType: v4.00+
PlayResX: 320
PlayResY: 240

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,40,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,3,0,5,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:00.50,Default,,0,0,0,,{\fad(60,0)\fscx70\fscy70\t(0,120,\fscx100\fscy100)}hello
Dialogue: 0,0:00:00.50,0:00:01.00,Default,,0,0,0,,{\fad(60,0)\fscx70\fscy70\t(0,120,\fscx100\fscy100)}yo
Dialogue: 0,0:00:01.00,0:00:01.50,Default,,0,0,0,,{\fad(60,0)\fscx70\fscy70\t(0,120,\fscx100\fscy100)}hi
Dialogue: 0,0:00:01.50,0:00:02.00,Default,,0,0,0,,{\fad(60,0)\fscx70\fscy70\t(0,120,\fscx100\fscy100)}:3
"""

def test_burn_ass_writes_a_video(tmp_path):
    video = tmp_path / "bg.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
         "-i", "color=c=blue:s=320x240:d=2", "-pix_fmt", "yuv420p", str(video)],
        check=True,
    )
    ass = tmp_path / "subs.ass"
    ass.write_text(MINIMAL_ASS, encoding="utf-8")
    out = tmp_path / "out.mp4"

    burn_ass(str(video), str(ass), str(out))

    assert out.exists()
    assert get_duration(str(out)) == pytest.approx(2.0, abs=0.2)