#!/usr/bin/env bash
# probe-mp4.sh — Physical media contract verification for ad video deliverables
# Checks resolution and fps; reports codec/duration. Does not inspect visual safe zones.
set -euo pipefail

mp4="${1:?usage: probe-mp4.sh <file.mp4> [WxH] [fps]}"
exp_res="${2:-}"
exp_fps="${3:-}"

if ! command -v ffprobe >/dev/null 2>&1; then
  echo "Error: ffprobe is required but not installed." >&2
  exit 1
fi

q() { ffprobe -v error -select_streams v:0 -show_entries "$1" -of csv=p=0 "$mp4" | head -1; }

w=$(q stream=width)
h=$(q stream=height)
codec=$(q stream=codec_name)
rate=$(q stream=r_frame_rate)
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$mp4")
fps=$(awk -v r="$rate" 'BEGIN{split(r,a,"/"); printf "%.4g", (a[2]+0)?a[1]/a[2]:a[1]}')

printf '  [probe] %s: %sx%s | codec: %s | fps: %s | duration: %.2fs\n' "$(basename "$mp4")" "$w" "$h" "$codec" "$fps" "${dur:-0}"

fail=0
if [ -n "$exp_res" ] && [ "${w}x${h}" != "$exp_res" ]; then
  echo "  ✗ resolution mismatch: got ${w}x${h}, expected $exp_res" >&2
  fail=1
fi

if [ -n "$exp_fps" ] && ! awk -v a="$fps" -v b="$exp_fps" 'BEGIN{d=a-b; exit !(d<0.5 && d>-0.5)}'; then
  echo "  ✗ fps mismatch: got $fps, expected $exp_fps" >&2
  fail=1
fi

if [ "$codec" != "h264" ]; then
  echo "  ⚠ warning: video codec is $codec (standard ad delivery requires h264)" >&2
fi

if [ "$fail" -eq 0 ]; then
  echo "  ✓ Physical specification matches contract."
else
  exit 1
fi
