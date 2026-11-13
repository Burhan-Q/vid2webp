# vid2webp

Convert a video file to an animated WebP. Pure Python (OpenCV + Pillow), no
ffmpeg binary required.

## Requirements

- [uv](https://docs.astral.sh/uv/) — it manages the Python version and the
  dependencies for you.
- Python 3.9+ if you install the dependencies yourself.

## Install

Run it without installing anything, from a clone of this repo:

```sh
uvx --from . vid2webp input.mp4 output.webp
```

Or install it as a command on your `PATH`:

```sh
uv tool install .
vid2webp input.mp4 output.webp
```

Both commands must be run from the repo directory. The package is not on PyPI
yet, so plain `uvx vid2webp` (without `--from .`) fails with
"vid2webp was not found in the package registry".

`uv tool uninstall vid2webp` removes the installed command.

## Usage

```sh
vid2webp input.mp4 output.webp        # positional
vid2webp -i input.mp4 -o output.webp  # flags
vid2webp input.mp4                     # output defaults to input.webp
vid2webp --help                        # all options
```

| Flag        | Default | Description |
|-------------|---------|-------------|
| `--height`  | 640     | Output height in px, aspect preserved. Never upscales. `0` keeps the source resolution. |
| `--fps`     | 30      | Target frame rate, fractional values allowed. Never upsamples beyond the source. |
| `--quality` | 65      | WebP quality, 0–100. |
| `--method`  | 4       | WebP compression effort, 0–6 (higher = slower, marginally smaller). |

Input and output can be given positionally or with `-i/--input` and
`-o/--output`, but not both ways at once — doing so is an error.

When the output path is omitted it replaces the input's extension, so
`clip.mp4` becomes `clip.webp`. The output directory must already exist.

## Behaviour

- Only the video is converted; audio is dropped.
- Frames are decoded, resized with Lanczos, and written as one animated WebP
  that loops forever.
- The frame rate is capped at the source rate — frames are dropped, never
  duplicated.
- Output is always an animated WebP, even for a single-frame input.

On success the tool prints a one-line summary:

```
output.webp: 90 frames @ 30fps, 640x480, 0.2 MB (decode 0.0s, encode 0.5s)
```

Errors (missing input, undecodable video, non-existent output directory)
go to stderr and exit with status 1.

## License

MIT — see [LICENSE](LICENSE).
