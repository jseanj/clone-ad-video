#!/usr/bin/env bash
# contact-sheet.sh — Assemble keyframes into a single side-by-side contact sheet for visual review.
# Usage:
#   scripts/contact-sheet.sh output_sheet.png frame1.png frame2.png frame3.png
set -euo pipefail

out="${1:?usage: contact-sheet.sh <out.png> <in1.png> [in2.png ...]}"
shift

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "Error: ffmpeg is required but not installed." >&2
  exit 1
fi

inputs=()
filter=""
count=0
for img in "$@"; do
  inputs+=(-i "$img")
  filter="${filter}[${count}:v]"
  count=$((count + 1))
done

filter="${filter}hstack=inputs=${count}[v]"

ffmpeg -y "${inputs[@]}" -filter_complex "$filter" -map "[v]" "$out" >/dev/null 2>&1
echo "  ✓ Contact sheet generated at $out"
