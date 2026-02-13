#!/bin/bash

# Configuration
# Resolve absolute paths
BASE_DIR="$(pwd)"
BOOK_DIR="$BASE_DIR/output/mmm_book"
VIDEO_OUT_DIR="$BASE_DIR/output/videos"
SCRIPT_OUT_DIR="$BASE_DIR/output/video_scripts"
IMAGES_DIR="$BOOK_DIR/images"
VIDEO_GEN_DIR="$BASE_DIR/video-generator"

mkdir -p "$VIDEO_OUT_DIR"
mkdir -p "$SCRIPT_OUT_DIR"

# Navigate to video-generator directory
cd "$VIDEO_GEN_DIR" || exit

# Loop through all markdown chapters
for chapter_file in "$BOOK_DIR"/Chapter_*.md; do
    echo "Processing $chapter_file..."
    
    filename=$(basename -- "$chapter_file")
    chapter_name="${filename%.*}"
    output_video="$VIDEO_OUT_DIR/${chapter_name}.mp4"

    if [ -f "$output_video" ]; then
        echo "Video already exists for $chapter_name. Skipping."
        echo "-----------------------------------"
        continue
    fi
    
    # Image directory name usually matches the chapter name
    image_dir_name="$chapter_name"
    
    # 1. Generate AI Script (if not exists)
    script_json="$SCRIPT_OUT_DIR/${chapter_name}.json"
    if [ ! -f "$script_json" ]; then
        echo "Generating AI Script for $chapter_name..."
        cd "$BASE_DIR" || exit
        python3 -m src.generate_video_script "$chapter_file" "$script_json"
        cd "$VIDEO_GEN_DIR" || exit
    else
        echo "AI Script already exists for $chapter_name. Skipping generation."
    fi

    # 2. Generate Images & Update Script Paths
    script_with_images="$SCRIPT_OUT_DIR/${chapter_name}_images.json"
    echo "Generating images for $chapter_name..."
    # Run from base dir to ensure paths are correct
    cd "$BASE_DIR" || exit
    # We output directly to public/images so Remotion can serve them
    # Note: Remotion public dir is video-generator/public
    public_images_dir="$VIDEO_GEN_DIR/public/images"
    python3 src/generate_images_from_script.py "$script_json" "$script_with_images" "$public_images_dir"
    cd "$VIDEO_GEN_DIR" || exit

    if [ $? -ne 0 ]; then
        echo "Error generating images for $chapter_name. Using original script."
        cp "$script_json" "$script_with_images"
    fi

    # 3. Enrich Script (Calculate Durations)
    enriched_json="$SCRIPT_OUT_DIR/${chapter_name}_enriched.json"
    echo "Enriching script (calculating durations)..."
    # Use the script with images as input
    npx ts-node src/process_script.ts "$script_with_images" > "$enriched_json"

    if [ $? -ne 0 ]; then
        echo "Error parsing/enriching script for $chapter_name. Skipping."
        continue
    fi

    # 4. Generate SRT Subtitles
    output_srt="$VIDEO_OUT_DIR/${chapter_name}.srt"
    echo "Generating subtitles for $chapter_name..."
    cd "$BASE_DIR" || exit
    python3 src/json_to_srt.py "$enriched_json" "$output_srt"
    cd "$VIDEO_GEN_DIR" || exit

    # 5. Render Video
    output_video="$VIDEO_OUT_DIR/${chapter_name}.mp4"
    echo "Rendering to $output_video..."
    
    # Use the enriched JSON as props
    ./node_modules/.bin/remotion render src/index.tsx ChapterVideo "$output_video" \
        --props="$enriched_json" \
        --overwrite

    if [ $? -eq 0 ]; then
        echo "Successfully rendered $chapter_name"
    else
        echo "Failed to render $chapter_name"
    fi
    
    # Cleanup images
    rm -rf "public/images/$image_dir_name"

    echo "-----------------------------------"
done
