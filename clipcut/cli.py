"""Command Line interface python -m clipcut talk.mp4"""
import argparse
import os
from clipcut.silence import get_duration, detect_silences ,keep_segments, cut_video

def main(argv=None):
    # description
    p = argparse.ArgumentParser(prog="clipcut", description="Cut silences from talking heads.")
    
    # arguments
    p.add_argument("input", help="video file to process")
    p.add_argument("-o", "--output", help="output file(default: <input>_clipcut.mp4)")
    p.add_argument("--noise", type=float, default=-30, help="silence level in dB (default -30)")
    p.add_argument("--min-silence", type=float, default=0.5, help="shortest pause to cut, in seconds")
    p.add_argument("--padding", type=float, default=0.1, help="seconds of air kept around speech")
    # parse input
    args = p.parse_args(argv)

    # split path into main file and (to be discarded) extension 
    base, _ = os.path.split(args.input)
    output = args.output or f"{base}_cut.mp4"
    
    duration = get_duration(args.input)
    silences = detect_silences(args.input, duration, args.noise, args.min_silence)
    segments = keep_segments(silences, duration, args.padding)
    cut_video(args.input, segments, output)

    print(f"Cut {len(silences)} silence: {duration:.1f}s -> {get_duration(output):.1f}s")
    print(f"Saved {output}")
