import os
import argparse
from crewai import Crew
from src.main import BookGenerator
from src.utils import load_env

def main():
    parser = argparse.ArgumentParser(description="Generate a complete book from a title and description.")
    parser.add_argument("--title", required=True, help="Title of the book")
    parser.add_argument("--desc", required=True, help="Description/Theme of the book")
    parser.add_argument("--output_folder", default="output", help="Folder to save the book")
    parser.add_argument("--sleep", type=int, default=30, help="Seconds to sleep between chapters")
    
    args = parser.parse_args()
    
    load_env()
    generator = BookGenerator()
    generator.output_dir = args.output_folder
    
    if not os.path.exists(generator.output_dir):
        os.makedirs(generator.output_dir)

    outline_path = os.path.join(generator.output_dir, "generated_outline.md")

    # 1. Generate Outline
    if not os.path.exists(outline_path):
        print(f"\n🚀 Designing book structure for: {args.title}...")
        architect = generator.agents.book_architect()
        outline_task = generator.tasks.generate_outline(architect, args.title, args.desc)
        
        outline_crew = Crew(
            agents=[architect],
            tasks=[outline_task],
            verbose=True
        )
        
        result = outline_crew.kickoff()
        outline_content = result.raw if hasattr(result, 'raw') else str(result)
        
        with open(outline_path, "w") as f:
            f.write(outline_content)
        print(f"✅ Outline generated and saved to {outline_path}")
    else:
        print(f"⏩ Outline already exists at {outline_path}, skipping generation.")

    # 2. Run the Full Generation Loop
    print("\n✍️ Starting chapter generation...")
    generator.run(outline_path=outline_path, sleep_between_chapters=args.sleep)

    # 3. Final Formatting Pass
    print("\n✨ Finalizing book formatting...")
    generator.run_formatter()

    # 4. Image Generation & Frontend Sync
    print("\n🎨 Generating images and publishing to frontend...")
    from sync_to_web import sync_chapters_async
    import asyncio
    asyncio.run(sync_chapters_async(output_dir=generator.output_dir))

    print(f"\n🎉 DONE! Your book '{args.title}' is ready in '{args.output_folder}'")
    print(f"📖 You can view it by running ./launch_reader.sh")

if __name__ == "__main__":
    main()
