"""Command Line interface python -m clipcut talk.mp4 --captions"""
import argparse
import os
import shutil
import sys

from clipcut.silence import get_duration, detect_silences ,keep_segments, cut_video
from clipcut.captions import transcribe, write_srt

def build_parser():
    
    # description
    p = argparse.ArgumentParser(
        prog="clipcut", 
        description="Cut silences add captions to talking videos.",
        )
    
    # arguments
    p.add_argument("input", help="video file to process")
    p.add_argument("-o", "--output", help="output file(default: <input>_cut.mp4)")
    p.add_argument("--noise", type=float, default=-30, help="silence level in dB (default -30)")
    p.add_argument("--min-silence", type=float, default=0.5, help="shortest pause to cut, in seconds")
    p.add_argument("--padding", type=float, default=0.1, help="seconds of air kept around speech")
    p.add_argument("--no_cut", action="store_true", help="skip silence removal")
    p.add_argument("--captions", action="store_true", help="write an .srt caption file")
    p.add_argument("--lang", default=None, help="speech language, e.g. en, fr, ar (default: auto)")
    p.add_argument("--model", default="small", help="whisper model: tiny, base, small, medium")
    return p


def main(argv=None):
    # parse input
    args = build_parser().parse_args(argv)

    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        sys.exit("Error: ffmpeg is not installed or not on PATH.")
    if not os.path.isfile(args.input):
        sys.exit(f"Error: file not found: {args.input}")


    # split path into main file and (to be discarded) extension 
    base, _ = os.path.splitext(args.input)
    output = args.output or f"{base}_cut.mp4"
    current = args.input

    if not args.no_cut:
        duration = get_duration(current)
        silences = detect_silences(current, duration, args.noise, args.min_silence)
        segments = keep_segments(silences, duration, args.padding)
        if not segments:
            sys.exit("Error: the whole video is silent. Try a lower --noise value, e.g. -40.")
        cut_video(current, segments, output)
        new_duration = get_duration(output)
        print(f"Cut {len(silences)} silences: {duration:.1f}s -> {new_duration:.1f}s")
        current = output

    if args.captions:
        print("Transcribing (the first run downloads the model, about 500 MB)...")
        captions, language = transcribe(current, args.model, args.lang)
        
        if not captions:
            sys.exit("Error: no speech found, so there are not captions to write.")
        
        srt_path = os.path.splitext(output)[0] + ".srt"    
        write_srt(captions, srt_path)
        print(f"Wrote {len(captions)} captions ({language}) to {srt_path}")

    print("Done.")

if __name__ == "__main__":
    main()