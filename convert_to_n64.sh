#!/usr/bin/env bash
set -euo pipefail

# Converts .v64 and .z64 files in IN_RAW to .n64 in IN_N64
# Moves existing .n64 files straight into IN_N64 unchanged
#
# Expected layout:
#   ./IN_RAW
#   ./IN_N64
#   ./n64romconvert
#
# Run from the folder containing those items:
#   bash convert_to_n64.sh

RAW_DIR="./IN_RAW"
OUT_DIR="./IN_N64"
CONVERTER="./n64romconvert"

mkdir -p "$OUT_DIR"

if [[ ! -d "$RAW_DIR" ]]; then
  echo "Error: input folder not found: $RAW_DIR"
  exit 1
fi

if [[ ! -x "$CONVERTER" ]]; then
  echo "Error: converter not found or not executable: $CONVERTER"
  echo "Try: chmod +x $CONVERTER"
  exit 1
fi

converted=0
moved=0
skipped=0
failed=0

for f in "$RAW_DIR"/*; do
  [[ -f "$f" ]] || continue

  filename="$(basename "$f")"

  # Lowercase extension handling
  ext="${filename##*.}"
  ext="${ext,,}"
  stem="${filename%.*}"
  out_file="$OUT_DIR/$stem.n64"

  # Avoid overwriting existing output files
  if [[ -e "$out_file" ]]; then
    echo "Skipping (output exists): $filename -> $(basename "$out_file")"
    ((skipped+=1))
    continue
  fi

  case "$ext" in
    v64|z64)
      echo "Converting: $filename -> $(basename "$out_file")"
      if "$CONVERTER" -T n64 -o "$out_file" "$f"; then
        ((converted+=1))
      else
        echo "Failed to convert: $filename"
        rm -f "$out_file"
        ((failed+=1))
      fi
      ;;
    n64)
      echo "Moving: $filename -> $OUT_DIR/"
      mv "$f" "$out_file"
      ((moved+=1))
      ;;
    *)
      echo "Ignoring unsupported file: $filename"
      ((skipped+=1))
      ;;
  esac
done

echo
echo "Done."
echo "Converted : $converted"
echo "Moved     : $moved"
echo "Skipped   : $skipped"
echo "Failed    : $failed"
