#!/bin/bash

# Default values
TITLE=""
DESC=""
OUTPUT="output"

# Usage help
usage() {
  echo "Usage: ./create_book.sh --title \"Book Title\" --desc \"Book Description\" [--output \"folder_name\"]"
  exit 1
}

# Parse arguments
while [[ "$#" -gt 0 ]]; do
  case $1 in
    --title) TITLE="$2"; shift ;;
    --desc) DESC="$2"; shift ;;
    --output) OUTPUT="$2"; shift ;;
    *) echo "Unknown parameter: $1"; usage ;;
  esac
  shift
done

if [[ -z "$TITLE" || -z "$DESC" ]]; then
  usage
fi

echo "📖 Starting Book Generation System..."
echo "Title: $TITLE"
echo "Theme: $DESC"
echo "Output: $OUTPUT"
echo "-----------------------------------"

# Run the python script
./venv/bin/python generate_full_book.py --title "$TITLE" --desc "$DESC" --output_folder "$OUTPUT"
