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

async def process_diagrams_in_content(content, chapter_name, book_id, output_dir, generator):
    """
    Finds [DIAGRAM: ...] tags in content, generates images to output_dir/images/
    and replaces tags with markdown image links for the web.
    """
    diagram_pattern = re.compile(r'\[DIAGRAM: (.*?)\]', re.DOTALL)
    caption_pattern = re.compile(r'Caption: "(.*?)"', re.DOTALL)
    
    matches = list(diagram_pattern.finditer(content))
    if not matches:
        return content

    # Directory for images LOCALLY in the output folder
    output_images_base = Path(output_dir) / "images"
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
            # NEW: The path in the markdown should be /images/<book_id>/... for absolute resolution
            relative_path = f"/images/{book_id}/{chapter_name}/{filename}"
            replacement = f"![{caption}]({relative_path})"
            
            start, end = match.span()
            new_content = new_content[:start] + replacement + new_content[end:]
        else:
            print(f"Failed to generate diagram for {chapter_name}, index {diagram_index}")

    return new_content

async def sync_chapters_async(output_dir="output"):
    load_dotenv()
    base_content_dir = Path("frontend/public/content")
    
    # 1. Determine Book Identity
    # Try to get title from generated_outline.md if it exists
    book_title = "Untitled Book"
    outline_path = Path(output_dir) / "generated_outline.md"
    if outline_path.exists():
        with open(outline_path, "r") as f:
            full_outline = f.read()
            first_line = full_outline.split('\n')[0].strip()
            
            # Case 1: Standard markdown header
            if first_line.startswith("# "):
                book_title = first_line.replace("# ", "").strip()
            # Case 2: Phrases like "outline for 'Title'" or similar
            else:
                title_match = re.search(r"['\"]([^'\"]+)['\"]", first_line)
                if title_match:
                    book_title = title_match.group(1).strip()
                elif "outline for" in first_line.lower():
                    book_title = first_line.split("outline for")[-1].strip().strip(' :.').title()
    
    # Create a safe ID for the folder based on the output directory name to stay consistent
    book_id = Path(output_dir).name
    book_dir = base_content_dir / book_id
    book_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Setup Generator for diagrams
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("RUNWARE_API_KEY")
    generator = ImageGenerator(api_key=api_key)
    await generator.initialize()

    chapters = []
    
    # 3. Process Chapters
    files = [f for f in os.listdir(output_dir) if f.endswith(".md") and f.startswith("Chapter_")]
    files.sort(key=lambda x: int(re.search(r'Chapter_(\d+)', x).group(1)) if re.search(r'Chapter_(\d+)', x) else 0)
    
    for i, filename in enumerate(files):
        path = os.path.join(output_dir, filename)
        with open(path, "r") as f:
            content = f.read()
            
        # Extract title
        match = re.search(r"^# (.*)", content, re.MULTILINE)
        raw_title = match.group(1).strip() if match else filename
        clean_title = re.sub(r"^(Chapter \d+:?)\s+\d+(?:\.\d+)*\s*", r"\1 ", raw_title)
        
        # Clean content
        markdown_blocks = re.findall(r"```markdown\s*(.*?)\s*```", content, re.DOTALL)
        final_content = "\n\n".join(markdown_blocks) if markdown_blocks else content
        final_content = re.sub(r"^# Chapter \d+:.*?\n", "", final_content, flags=re.IGNORECASE).strip()
        
        # Process diagrams using THE specific output folder for images
        chapter_id_name = Path(filename).stem
        final_content = await process_diagrams_in_content(final_content, chapter_id_name, book_id, output_dir, generator)

        web_filename = f"chapter_{i+1}.md"
        with open(book_dir / web_filename, "w") as f:
            f.write(final_content)
        
        chapters.append({
            "id": i + 1,
            "title": clean_title,
            "filename": web_filename
        })
        
    # 4. Save book-specific index
    with open(book_dir / "book.json", "w") as f:
        json.dump(chapters, f, indent=2)

    # 5. Update global books.json index
    global_index_path = base_content_dir / "books.json"
    books_index = []
    if global_index_path.exists():
        try:
            with open(global_index_path, "r") as f:
                books_index = json.load(f)
        except:
            books_index = []
            
    # Update or add this book
    new_book_entry = {
        "id": book_id,
        "title": book_title,
        "path": book_id
    }
    
    # Check if already exists
    existing = next((b for b in books_index if b["id"] == book_id), None)
    if existing:
        books_index[books_index.index(existing)] = new_book_entry
    else:
        books_index.append(new_book_entry)
        
    with open(global_index_path, "w") as f:
        json.dump(books_index, f, indent=2)
        
    # 6. Sync images to frontend root public folder
    image_source = os.path.join(output_dir, "images")
    image_target = os.path.join("frontend/public/images", book_id)
    if os.path.exists(image_source):
        os.makedirs(image_target, exist_ok=True)
        # copy everything from output/images/ into frontend/public/images/<book_id>/
        shutil.copytree(image_source, image_target, dirs_exist_ok=True)
        print(f"Synced images to {image_target}")
    
    print(f"Synced '{book_title}' ({len(chapters)} chapters) to frontend.")

def main():
    parser = argparse.ArgumentParser(description="Sync generated book chapters and images to the frontend.")
    parser.add_argument("--dir", type=str, help="The specific book directory to sync (e.g., output/statistics_book)")
    parser.add_argument("--all", action="store_true", help="Sync all books found in the output/ directory")
    
    args = parser.parse_args()
    
    if args.all:
        output_base = Path("output")
        if not output_base.exists():
            print("Error: 'output' directory not found.")
            return
            
        # Find all directories that contain at least one Chapter_*.md file
        book_dirs = []
        for d in output_base.iterdir():
            if d.is_dir():
                chapters = list(d.glob("Chapter_*.md"))
                if chapters:
                    book_dirs.append(d)
        
        if not book_dirs:
            print("No books found in output/ to sync.")
            return
            
        print(f"🔄 Syncing {len(book_dirs)} books...")
        for book_dir in book_dirs:
            print(f"\n--- Syncing {book_dir.name} ---")
            asyncio.run(sync_chapters_async(output_dir=str(book_dir)))
    
    elif args.dir:
        if not os.path.exists(args.dir):
            print(f"Error: Directory {args.dir} does not exist.")
            return
        asyncio.run(sync_chapters_async(output_dir=args.dir))
    else:
        # Default behavior: sync 'output' if it has chapters, otherwise ask
        if list(Path("output").glob("Chapter_*.md")):
            asyncio.run(sync_chapters_async(output_dir="output"))
        else:
            parser.print_help()
            print("\nHint: Try --dir output/statistics_book or --all")

if __name__ == "__main__":
    import argparse
    main()
