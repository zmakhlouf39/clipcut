# clipcut

Command-line tool that turns raw talking-head footage into a cut short-form video.
It finds the silent pauses in a recording and cuts them out, and applies custom captions.

> **Status:** early stage. 
- ✅ Silence removal. 
- ✅ transcribtion.
- ✅ srt file creation.
- ✅ Automatic captions.
- ⌛GUI

## How it works

1. **Probe** the video length with `ffprobe`.
2. **Extract** the audio into a temporary 16 kHz mono WAV file. Silence detection on audio alone is much faster than on the full video.
3. **Detect** pauses longer than `--min-silence` that are quieter than `--noise` using FFmpeg's `silencedetect` filter.
4. **Invert** the pauses into the list of speaking segments, widened by `--padding` on each side.
5. **Cut** those segments from the original video with `trim`/`atrim` and join them with `concat`, then re-encode to H.264 video and AAC audio.

## Requirements

- Python 3
- [FFmpeg](https://ffmpeg.org/download.html) with `ffmpeg` and `ffprobe` available on your `PATH`

Check that FFmpeg is installed:

```bash
ffmpeg -version
ffprobe -version
```

## Installation

```bash
git clone https://github.com/zmakhlouf39/clipcut.git
cd clipcut
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

## Usage

```bash
python -m clipcut talk.mp4
```

This writes the cut video next to the input file. To choose the output name:

```bash
python -m clipcut talk.mp4 -o short.mp4
```

### Options

| Option | Default | What it does |
| --- | --- | --- |
| `input` | required | Video file to process |
| `-o`, `--output` | `<input>_cut.mp4` | Output file path |
| `--noise` | `-30` | Silence threshold in dB. Raise it (for example `-25`) if quiet speech gets cut. Lower it (for example `-35`) if pauses are not removed. |
| `--min-silence` | `0.5` | Shortest pause, in seconds, that gets cut |
| `--padding` | `0.1` | Seconds of audio and video kept on each side of speech |
| `--no_cut` | / | Skip silence removal |
| `--captions` | / | Write an .srt caption file |
| `--lang` | None | Speech language, e.g. en, fr, ar (default: auto) |
| `--model` | small | Whisper model: tiny, base, small, medium |

### Caption options
| Option | Default | What it does |
| --- | --- | --- |
| `words` | 1 | words per caption |
| `font` | Arial | caption font |
| `size` | 80 | caption size |
| `color` | white (FFFFFF) | caption color (in hex) |
| `animation` | pop | caption animation (none, fade, pop, bounce) |
| `position` | middle | caption position (top, middle, bottom) |
| `remove_punctuation` | False | Keeps or remove punctuation |

When it finishes, it prints how much was removed:

```
Cut 12 silence: 49.2s -> 31.8s
Saved talk_cut.mp4
```

## Project structure

```
clipcut/
├── clipcut/
│   ├── __init__.py
│   ├── __main__.py     # enables `python -m clipcut`
│   ├── cli.py          # argument parsing and the pipeline
│   ├── silence.py      # probing, silence detection, segment logic, cutting
│   └── captions.py     # transcription
│   └── styled.py       # caption customization
├── tests/
│   ├── test_silence.py
│   └── test_captions.py
│   └── test_styled.py
├── requirements.txt
└── LICENSE
```

## Development

Run the tests:

```bash
pytest
```

The silence tests generate small test videos with FFmpeg, so FFmpeg must be installed first.


## License

MIT. See [LICENSE](LICENSE).
