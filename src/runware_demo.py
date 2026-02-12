import os
import asyncio
import re
from pathlib import Path
from dotenv import load_dotenv
import requests
from runware import Runware, IImageInference

async def run_demo():
    load_dotenv()
    api_key = os.getenv("RUNWARE_API_KEY")
    if not api_key:
        print("Error: RUNWARE_API_KEY not found in .env file.")
        return

    # 1. Initialize Runware
    runware = Runware(api_key=api_key)
    await runware.connect()

    # 2. Define prompt
    prompt = "A cartoon brain wearing a VR headset, looking amazed. In a clean, high-contrast, professional cartoon/hand-drawn style, suitable for a technical book like Head First series. White background, simple lines. Landscape 16:9 aspect ratio."
    
    print(f"Generating image for: {prompt}")
    
    # 3. Request Image
    image_request = IImageInference(
        model="google:4@2",
        positivePrompt=prompt,
        numberResults=1,
        width=2560,
        height=1440,
    )
    
    images = await runware.imageInference(requestImage=image_request)
    
    if not images:
        print("Failed to generate image.")
        return

    image_url = images[0].imageURL
    print(f"Image generated! URL: {image_url}")

    # 4. Save Image to the output/images directory so sync_to_web can find it
    output_dir = Path("output")
    images_dir = output_dir / "images" / "demo"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    image_path = images_dir / "runware_demo.png"
    
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(image_path, 'wb') as f:
            f.write(response.content)
        print(f"Image saved to {image_path}")
    else:
        print("Failed to download image.")
        return

    # 5. Create a demo MD in the output folder
    # This ensures it's picked up by the sync process
    demo_filename = "Chapter_0_Runware_Demo.md"
    demo_md_path = output_dir / demo_filename
    content = f"""# Chapter 0: Runware Demo

This is a demonstration of the new Runware image generation integration.

[DIAGRAM: A cartoon brain wearing a VR headset, looking amazed. Caption: "Runware Generated Brain"]

*The future of high-speed diagram generation is here!*
"""
    with open(demo_md_path, "w") as f:
        f.write(content)
    print(f"Created/Updated {demo_md_path}")

    # 6. Run sync_to_web.py logic to update frontend
    print("Syncing to web UI...")
    import sys
    sys.path.append(os.getcwd())
    from sync_to_web import sync_chapters_async
    await sync_chapters_async()

    print("\n✨ Done! Refresh your browser at http://localhost:5173/minimalist_genai_book/")
    print("Look for 'Chapter 0: Runware Demo' in the sidebar.")

if __name__ == "__main__":
    asyncio.run(run_demo())
