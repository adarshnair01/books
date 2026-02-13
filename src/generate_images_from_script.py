import os
import json
import argparse
import asyncio
import re
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# Reuse logic from process_diagrams mostly, but adapted for the script JSON
class ImageGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = None

    async def generate(self, prompt, output_path):
        if os.path.exists(output_path):
            print(f"Image already exists: {output_path}")
            return True

        if not self.client:
            print("No API Key.")
            return False

        print(f"Generating: {prompt[:50]}...")
        try:
            full_prompt = f"{prompt}. In a clean, high-contrast, professional cartoon/hand-drawn style, suitable for a technical book like Head First series. White background, simple lines. Landscape 16:9 aspect ratio."
            response = await self.client.aio.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[full_prompt],
            )
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        part.as_image().save(output_path)
                        return True
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False

async def process_script(input_path, output_path, images_dir):
    with open(input_path, 'r') as f:
        script = json.load(f)
    
    # Chapter name from filename
    chapter_name = Path(input_path).stem
    # If the file is enriched, it might have _enriched suffix, strip it
    if "_enriched" in chapter_name:
        chapter_name = chapter_name.replace("_enriched", "")

    # Output dir for images
    images_output_dir = Path(images_dir) / chapter_name
    images_output_dir.mkdir(parents=True, exist_ok=True)

    load_dotenv()
    generator = ImageGenerator(os.getenv("GEMINI_API_KEY"))

    segments = script.get("segments", [])
    updated_segments = []

    for i, seg in enumerate(segments):
        visual = seg.get("visual", {})
        if visual.get("type") == "image":
            description = visual.get("content", "")
            # Sanitize description for filename
            safe_desc = re.sub(r'[^a-z0-9]', '_', description.lower())[:50]
            filename = f"scene_{i}_{safe_desc}.png"
            image_path = images_output_dir / filename
            
            # Generate image
            await generator.generate(description, image_path)
            
            # Update content to web path (relative to public)
            # We assume images will be copied to public/images/Chapter_X
            visual["content"] = f"/images/{chapter_name}/{filename}"
        
        updated_segments.append(seg)
    
    script["segments"] = updated_segments
    
    with open(output_path, 'w') as f:
        json.dump(script, f, indent=2)
    print(f"Saved updated script with images to {output_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_json")
    parser.add_argument("output_json")
    parser.add_argument("images_dir")
    args = parser.parse_args()
    
    asyncio.run(process_script(args.input_json, args.output_json, args.images_dir))

if __name__ == "__main__":
    main()
