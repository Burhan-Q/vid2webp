# vid2webp

Convert a video file to an animated WebP. Pure Python (OpenCV + Pillow), no
ffmpeg required.

## Run without installing

```sh
uvx vid2webp input.mp4 output.webp
```

## Install as a tool

```sh
uv tool install .
vid2webp input.mp4 output.webp
```

## Usage

```sh
vid2webp input.mp4 output.webp        # positional
vid2webp -i input.mp4 -o output.webp  # flags
vid2webp input.mp4                     # output defaults to input.webp
```

| Flag        | Default | Description |
|-------------|---------|-------------|
| `--height`  | 640     | Output height in px, aspect preserved. Never upscales. |
| `--fps`     | 30      | Target frame rate. Never upsamples beyond the source. |
| `--quality` | 65      | WebP quality, 0–100. |
| `--method`  | 4       | WebP compression effort, 0–6 (higher = slower, marginally smaller). |
