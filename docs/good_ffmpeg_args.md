# FFMPEG Ideal arguments

* AVIF output is significantly smaller (WEBP not supported) than GIF
  * same video at 960 + 30 FPS ~ 13.9 MB GIF, AVIF w/ same settings ~4.1 MB
* 1080 helped imrove text readability
* 30 FPS 

ffmpeg -y -loglevel error -i INPUT.mp4 -filter_complex "fps=30,scale=1080:-1:flags=lanczos,split[s0][s1];[s0]palettegen=stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" -loop 0 OUTPUT.avif
