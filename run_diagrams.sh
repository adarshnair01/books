#!/bin/bash

# Configuration
CHAPTER_NUM=$1
START_CHAPTER=$2
END_CHAPTER=$3

VENV_PATH="venv/bin/python"

if [ -n "$CHAPTER_NUM" ]; then
    echo "Processing Chapter $CHAPTER_NUM..."
    $VENV_PATH src/process_diagrams.py --chapter "$CHAPTER_NUM"
elif [ -n "$START_CHAPTER" ] && [ -n "$END_CHAPTER" ]; then
    echo "Processing Chapters $START_CHAPTER to $END_CHAPTER..."
    $VENV_PATH src/process_diagrams.py --start "$START_CHAPTER" --end "$END_CHAPTER"
else
    echo "Processing all chapters..."
    $VENV_PATH src/process_diagrams.py
fi
