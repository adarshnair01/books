import os
import asyncio
import re
import shutil
import json
from pathlib import Path
from dotenv import load_dotenv
import requests

# Import the new ImageGenerator
from src.process_diagrams import ImageGenerator

async def process_diagrams_in_content(content, chapter_name, generator):
    """
    Finds [DIAGRAM: ...] tags in content, generates images to output/images/
    and replaces tags with markdown image links.
    Returns the modified content.
    """
    diagram_pattern = re.compile(r'\[DIAGRAM: (.*?)\]', re.DOTALL)
    caption_pattern = re.compile(r'Caption: "(.*?)"', re.DOTALL)
    
    matches = list(diagram_pattern.finditer(content))
    if not matches:
        return content

    # Directory for images in both output and frontend
    output_images_base = Path("output/images")
    chapter_image_dir = output_images_base / chapter_name
    chapter_image_dir.mkdir(parents=True, exist_ok=True)

    new_content = content
    # Process in reverse to maintain indices
    for i, match in enumerate(reversed(matches)):
        diagram_index = len(matches) - i
        diagram_content = match.group(1).strip()
        
        # Extract caption or use default
        cap_match = caption_pattern.search(diagram_content)
        caption = cap_match.group(1) if cap_match else f"Diagram {diagram_index}"
        
        # Clean prompt
        prompt = diagram_content
        if cap_match:
            prompt = diagram_content.replace(cap_match.group(0), "").strip()
        prompt = prompt.strip('"').strip("'")

        # Filename
        safe_caption = re.sub(r'[^a-z0-9]', '_', caption.lower())[:40]
        filename = f"diagram_{diagram_index}_{safe_caption}.png"
        image_path = chapter_image_dir / filename
        
        # Generate image (this will skip if it exists)
        if await generator.generate(prompt, image_path):
            # The path in the markdown should be relative to the content folder
            relative_path = f"images/{chapter_name}/{filename}"
            replacement = f"![{caption}]({relative_path})"
            
            start, end = match.span()
            new_content = new_content[:start] + replacement + new_content[end:]
        else:
            print(f"Failed to generate diagram for {chapter_name}, index {diagram_index}")

    return new_content

async def sync_chapters_async():
    load_dotenv()
    output_dir = "output"
    target_dir = "frontend/public/content"
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)
        
    # Prioritize Gemini API Key for diagrams
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("RUNWARE_API_KEY")
    generator = ImageGenerator(api_key=api_key)
    await generator.initialize()

    chapters = []
    
    # Get all .md files in output and sort them numerically
    files = [f for f in os.listdir(output_dir) if f.endswith(".md")]
    files.sort(key=lambda x: int(re.search(r'Chapter_(\d+)', x).group(1)) if re.search(r'Chapter_(\d+)', x) else 0)
    
    for i, filename in enumerate(files):
        path = os.path.join(output_dir, filename)
        with open(path, "r") as f:
            content = f.read()
            
        # 1. Extract the primary title for the sidebar
        match = re.search(r"^# (.*)", content, re.MULTILINE)
        raw_title = match.group(1).strip() if match else filename
        clean_title = re.sub(r"^(Chapter \d+:?)\s+\d+(?:\.\d+)*\s*", r"\1 ", raw_title)
        
        # 2. Extract content from inside ```markdown blocks if present
        markdown_blocks = re.findall(r"```markdown\s*(.*?)\s*```", content, re.DOTALL)
        if markdown_blocks:
            final_content = "\n\n".join(markdown_blocks)
        else:
            final_content = content
            
        # 3. Clean up the content (remove redundant top-level headers)
        final_content = re.sub(r"^# Chapter \d+:.*?\n", "", final_content, flags=re.IGNORECASE).strip()
        
        # NEW: Process diagrams during sync (does not touch source files)
        chapter_id_name = Path(filename).stem
        final_content = await process_diagrams_in_content(final_content, chapter_id_name, generator)

        # 4. New filename for web
        web_filename = f"chapter_{i+1}.md"
        with open(os.path.join(target_dir, web_filename), "w") as f:
            f.write(final_content)
        
        chapters.append({
            "id": i + 1,
            "title": clean_title,
            "filename": web_filename
        })
        
    # Sync images to frontend root public folder
    # This makes 'images/...' paths in markdown work correctly
    image_source = os.path.join(output_dir, "images")
    image_target = "frontend/public/images" 
    if os.path.exists(image_source):
        if os.path.exists(image_target):
            shutil.rmtree(image_target)
        shutil.copytree(image_source, image_target)
        print(f"Synced images to {image_target}")

    with open(os.path.join(target_dir, "book.json"), "w") as f:
        json.dump(chapters, f, indent=2)
    
    print(f"Synced {len(chapters)} chapters to frontend.")

def sync_chapters():
    asyncio.run(sync_chapters_async())

if __name__ == "__main__":
    sync_chapters()
