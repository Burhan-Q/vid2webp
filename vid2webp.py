"""Convert a video file to an animated WebP using OpenCV + Pillow."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import cv2
from PIL import Image


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="vid2webp",
        description="Convert a video file to an animated WebP.",
    )
    parser.add_argument(
        "input_pos",
        nargs="?",
        metavar="INPUT",
        help="Input video file (positional).",
    )
    parser.add_argument(
        "output_pos",
        nargs="?",
        metavar="OUTPUT",
        help="Output .webp path (positional). Defaults to <input stem>.webp.",
    )
    parser.add_argument("-i", "--input", dest="input_flag", help="Input video file.")
    parser.add_argument("-o", "--output", dest="output_flag", help="Output .webp path.")
    parser.add_argument(
        "--height",
        type=int,
        default=640,
        help="Output height in px, aspect preserved (default: 640). Never upscales.",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=30.0,
        help="Target frame rate (default: 30). Never upsamples beyond source.",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=65,
        help="WebP quality 0-100 (default: 65).",
    )
    parser.add_argument(
        "--method",
        type=int,
        default=4,
        choices=range(7),
        metavar="{0-6}",
        help="WebP compression effort 0-6 (default: 4).",
    )
    return parser.parse_args(argv)


def resolve_io(args: argparse.Namespace) -> tuple[Path, Path]:
    """Merge positional and flag forms into a single (input, output) pair."""
    if args.input_pos and args.input_flag:
        raise SystemExit("error: input given both positionally and with -i/--input")
    if args.output_pos and args.output_flag:
        raise SystemExit("error: output given both positionally and with -o/--output")

    input_str = args.input_flag or args.input_pos
    if not input_str:
        raise SystemExit("error: no input video given (positional or -i/--input)")

    input_path = Path(input_str)
    output_str = args.output_flag or args.output_pos
    output_path = Path(output_str) if output_str else input_path.with_suffix(".webp")
    return input_path, output_path


def validate(input_path: Path, output_path: Path) -> None:
    if not input_path.is_file():
        raise SystemExit(f"error: input video not found: {input_path}")
    out_dir = output_path.parent
    if not out_dir.exists():
        raise SystemExit(f"error: output directory does not exist: {out_dir}")


def extract_frames(
    input_path: Path, target_fps: float, target_height: int
) -> tuple[list[Image.Image], float]:
    """Decode and subsample frames, resizing each to target height.

    Returns the kept frames and the effective fps actually used (never above
    the source fps, since we don't synthesize frames).
    """
    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise SystemExit(f"error: could not open video: {input_path}")

    src_fps = cap.get(cv2.CAP_PROP_FPS)
    if not src_fps or src_fps <= 0:
        src_fps = target_fps  # fall back to keeping every frame
    effective_fps = min(target_fps, src_fps)
    step = src_fps / target_fps if target_fps < src_fps else 1.0

    frames: list[Image.Image] = []
    next_pick = 0.0
    idx = 0
    while cap.grab():
        if idx >= next_pick:
            ok, frame = cap.retrieve()
            if not ok:
                break
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            if target_height and img.height > target_height:
                width = round(img.width * target_height / img.height)
                img = img.resize((width, target_height), Image.LANCZOS)
            frames.append(img)
            next_pick += step
        idx += 1
    cap.release()

    if not frames:
        raise SystemExit(f"error: no frames decoded from video: {input_path}")
    return frames, effective_fps


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    input_path, output_path = resolve_io(args)
    validate(input_path, output_path)

    t0 = time.time()
    frames, effective_fps = extract_frames(input_path, args.fps, args.height)
    decode_t = time.time() - t0

    duration_ms = round(1000.0 / effective_fps)
    t1 = time.time()
    frames[0].save(
        output_path,
        format="WEBP",
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,
        loop=0,
        quality=args.quality,
        method=args.method,
    )
    encode_t = time.time() - t1

    w, h = frames[0].size
    size_mb = output_path.stat().st_size / 1_000_000
    print(
        f"{output_path}: {len(frames)} frames @ {effective_fps:g}fps, {w}x{h}, "
        f"{size_mb:.1f} MB (decode {decode_t:.1f}s, encode {encode_t:.1f}s)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
