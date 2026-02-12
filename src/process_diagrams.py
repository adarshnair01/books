import os
import re
import argparse
from pathlib import Path
from dotenv import load_dotenv
import asyncio
from google import genai
from google.genai import types

class ImageGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = None

    async def initialize(self):
        # google-genai client doesn't need explicit connect like Runware
        pass

    async def generate(self, prompt, output_path):
        """
        Generates an image based on the prompt and saves it to output_path.
        Returns True if successful, False otherwise.
        """
        if os.path.exists(output_path):
            print(f"Image already exists, skipping generation: {output_path}")
            return True

        if not self.client:
            print(f"Skipping image generation (no api-key): {prompt[:50]}...")
            return False

        print(f"Generating image for prompt: {prompt[:100]}...")
        
        try:
            # Adding style guidance to the prompt to keep it consistent with Head First
            full_prompt = f"{prompt}. In a clean, high-contrast, professional cartoon/hand-drawn style, suitable for a technical book like Head First series. White background, simple lines. Landscape 16:9 aspect ratio."
            
            # Using the new generate_content API for image generation as requested
            response = await self.client.aio.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[full_prompt],
            )
            
            image_saved = False
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        image = part.as_image()
                        image.save(output_path)
                        image_saved = True
                        break
            
            if image_saved:
                return True
            else:
                print("No image data found in the response parts.")
                return False
                
        except Exception as e:
            print(f"Error generating image: {e}")
            return False

class DiagramProcessor:
    def __init__(self, output_dir, images_subdir="images"):
        self.output_dir = Path(output_dir)
        self.images_base_dir = self.output_dir / images_subdir
        self.diagram_pattern = re.compile(r'\[DIAGRAM: (.*?)\]', re.DOTALL)
        self.caption_pattern = re.compile(r'Caption: "(.*?)"', re.DOTALL)

    async def process_file(self, file_path, generator, inplace=False):
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"File {file_path} not found.")
            return

        print(f"\n--- Processing {file_path.name} ---")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        new_content = content
        matches = list(self.diagram_pattern.finditer(content))
        
        if not matches:
            print(f"No diagrams found in {file_path.name}.")
            return

        print(f"Found {len(matches)} diagrams to process.")

        # Folder for this chapter's images
        chapter_name = file_path.stem
        chapter_image_dir = self.images_base_dir / chapter_name
        chapter_image_dir.mkdir(parents=True, exist_ok=True)

        # Process in reverse to keep indices correct after replacement
        processed_count = 0
        for i, match in enumerate(reversed(matches)):
            diagram_index = len(matches) - i
            diagram_content = match.group(1).strip()
            
            # Try to extract caption
            caption_match = self.caption_pattern.search(diagram_content)
            caption = caption_match.group(1) if caption_match else f"Diagram {diagram_index}"
            
            # Clean prompt for generation
            prompt = diagram_content
            if caption_match:
                prompt = diagram_content.replace(caption_match.group(0), "").strip()
            prompt = prompt.strip('"').strip("'")

            # Generate filename
            safe_caption = re.sub(r'[^a-z0-9]', '_', caption.lower())[:40]
            filename = f"diagram_{diagram_index}_{safe_caption}.png"
            image_path = chapter_image_dir / filename
            
            # Generate the image (this skips if exists)
            if await generator.generate(prompt, image_path):
                if inplace:
                    # Only do replacement if we are writing back to the file
                    relative_image_path = f"images/{chapter_name}/{filename}"
                    replacement = f"![{caption}]({relative_image_path})"
                    start, end = match.span()
                    new_content = new_content[:start] + replacement + new_content[end:]
                processed_count += 1
            else:
                print(f"Failed to generate image for diagram {diagram_index}")

        if processed_count > 0 and inplace:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Successfully updated {file_path.name} with {processed_count} images.")
        elif processed_count > 0:
            print(f"Generated {processed_count} images for {file_path.name} (Source file untouched).")
        else:
            print(f"No changes made to {file_path.name}.")

async def main_async():
    parser = argparse.ArgumentParser(description="Extract and generate images for [DIAGRAM: ...] tags in markdown using Gemini.")
    parser.add_argument("--chapter", type=int, help="Single chapter number to process.")
    parser.add_argument("--start", type=int, help="Start chapter number.")
    parser.add_argument("--end", type=int, help="End chapter number.")
    parser.add_argument("--dir", type=str, default="output", help="Directory containing markdown chapters.")
    parser.add_argument("--inplace", action="store_true", help="Modify source files in place (replace [DIAGRAM] with image link).")
    
    args = parser.parse_args()
    load_dotenv()
    
    output_dir = Path(args.dir)
    processor = DiagramProcessor(output_dir)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env file.")
        return

    generator = ImageGenerator(api_key=api_key) 
    await generator.initialize()

    files_to_process = []
    
    if args.chapter:
        pattern = f"Chapter_{args.chapter}_*.md"
        files_to_process.extend(output_dir.glob(pattern))
    elif args.start and args.end:
        for i in range(args.start, args.end + 1):
            pattern = f"Chapter_{i}_*.md"
            files_to_process.extend(output_dir.glob(pattern))
    else:
        # Process all chapters
        files_to_process.extend(output_dir.glob("Chapter_*.md"))

    # Sort files by chapter number
    def get_chapter_num(path):
        match = re.search(r'Chapter_(\d+)', path.name)
        return int(match.group(1)) if match else 0

    files_to_process.sort(key=get_chapter_num)

    if not files_to_process:
        print(f"No matching chapter files found in {output_dir.absolute()}.")
        return

    print(f"Found {len(files_to_process)} chapters to process.")
    for file_path in files_to_process:
        await processor.process_file(file_path, generator, inplace=args.inplace)

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
