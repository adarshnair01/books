import os
import re
import ast
import time
from crewai import Crew, Process, Task
from langchain_google_genai import ChatGoogleGenerativeAI
from src.agents import BookAgents
from src.tasks import BookTasks
from src.utils import load_env

# Check for environment variables
load_env()

class BookGenerator:
    def __init__(self):
        self.agents = BookAgents()
        self.tasks = BookTasks()
        self.output_dir = "output"

    def _read_file(self, file_path):
        with open(file_path, "r") as f:
            return f.read()

    def _parse_list_output(self, output_str):
        """
        Robustly parses a string representation of a list.
        Handles cases where the LLM might wrap the list in markdown code blocks.
        """
        try:
            # Remove markdown code blocks if present
            cleaned_output = re.sub(r"```(?:json|python)?\n?(.*?)```", r"\1", output_str, flags=re.DOTALL).strip()
            return ast.literal_eval(cleaned_output)
        except (ValueError, SyntaxError) as e:
            print(f"Error parsing list output: {e}\nRaw output: {output_str}")
            # Fallback: simple split if it looks like a list
            if "[" in output_str and "]" in output_str:
                 # extremely naive fallback
                 return [s.strip().strip("'").strip('"') for s in output_str.strip("[]").split(",")]
            return []

    def run(self, outline_path="config/outline.md", start_chapter=1, skip_existing=True, sleep_between_chapters=30):
        style_guide_path = "config/style_guide.md"
        
        outline_content = self._read_file(outline_path)
        style_guide = self._read_file(style_guide_path)

        # 1. Parse Outline (Naive parsing for now, assuming standard structure)
        # In a real app, I'd use an LLM to parse this structure first, but let's do a simple regex for chapters
        chapters = re.split(r"^### Chapter", outline_content, flags=re.MULTILINE)[1:] # Skip preamble
        
        for i, chapter_raw in enumerate(chapters):
            chapter_num = i + 1
            
            if chapter_num < start_chapter:
                continue

            lines = chapter_raw.strip().split("\n")
            # Clean title: remove any leading numbers (e.g., "1 The Attention..." -> "The Attention...")
            chapter_title = re.sub(r"^\d+\s*", "", lines[0].strip()).replace(":", "")
            
            # Prepare filename
            safe_title = "".join(x for x in chapter_title if x.isalnum() or x in (" ", "_", "-")).strip().replace(" ", "_")
            chapter_filename = f"{self.output_dir}/Chapter_{chapter_num}_{safe_title}.md"

            # Check if any file for this chapter already exists to skip
            # This is more robust than an exact filename match if titles change slightly
            existing_files = [f for f in os.listdir(self.output_dir) if f.startswith(f"Chapter_{chapter_num}_")]
            
            if skip_existing and existing_files:
                print(f"Skipping Chapter {chapter_num} (already exists: {existing_files[0]})")
                continue

            chapter_topics = "\n".join(lines[1:])
            
            print(f"\nProcessing Chapter {chapter_num}: {chapter_title}...")
            
            # 2. Expand Chapter
            print(f"  Expanding topics for Chapter {chapter_num}...")
            strategist = self.agents.content_strategist()
            expansion_task = self.tasks.expand_syllabus(strategist, chapter_title, chapter_topics)
            
            # We run a mini-crew just for expansion
            expansion_crew = Crew(
                agents=[strategist],
                tasks=[expansion_task],
                verbose=True
            )
            detailed_outline_raw = expansion_crew.kickoff()
            sub_sections = self._parse_list_output(detailed_outline_raw.raw if hasattr(detailed_outline_raw, 'raw') else str(detailed_outline_raw))
            
            print(f"  > Generated {len(sub_sections)} sub-sections.")

            chapter_content = [f"# Chapter {chapter_num}: {chapter_title}\n\n"]
            
            # 3. Write Sub-sections
            writer = self.agents.writer()
            reviewer = self.agents.reviewer()
            editor = self.agents.editor()

            for sub_section in sub_sections:
                # Handle formatted string like "Title: Description"
                if ":" in sub_section:
                    sec_title, sec_desc = sub_section.split(":", 1)
                else:
                    sec_title, sec_desc = sub_section, "Explain this concept in detail."
                
                print(f"    Writing section: {sec_title}...")
                
                # 3.1 Create Tasks using the helper methods
                write_task = self.tasks.write_section(writer, sec_title, sec_desc, style_guide)
                review_task = self.tasks.review_content(reviewer, context=[write_task])
                edit_task = self.tasks.edit_content(editor, context=[write_task, review_task])
                
                section_crew = Crew(
                    agents=[writer, reviewer, editor],
                    tasks=[write_task, review_task, edit_task],
                    verbose=True
                )
                
                result = section_crew.kickoff()
                
                # CrewAI returns a CrewOutput object in newer versions, or string in older.
                # result.raw is the safe bet for usually string content.
                final_text = result.raw if hasattr(result, 'raw') else str(result)
                chapter_content.append(final_text + "\n\n")
            
            # Save Chapter
            with open(chapter_filename, "w") as f:
                f.write("".join(chapter_content))
            
            print(f"  Finished Chapter {chapter_num}. Saved to {chapter_filename}")
            
            if chapter_num < len(chapters):
                print(f"  Sleeping for {sleep_between_chapters} seconds to avoid rate limits...")
                time.sleep(sleep_between_chapters)
            
    def run_formatter(self):
        """Iterate through all generated chapters and apply consistent formatting."""
        print("\n" + "="*50)
        print("STARTING GLOBAL FORMATTING PASS...")
        print("="*50)
        
        files = sorted([f for f in os.listdir(self.output_dir) if f.endswith(".md") and f.startswith("Chapter_")])
        
        if not files:
            print("No chapter files found in output directory.")
            return

        formatter_agent = self.agents.formatter()
        
        for filename in files:
            file_path = os.path.join(self.output_dir, filename)
            print(f"Formatting {filename}...")
            
            content = self._read_file(file_path)
            format_task = self.tasks.format_chapter(formatter_agent, content)
            
            crew = Crew(
                agents=[formatter_agent],
                tasks=[format_task],
                verbose=True
            )
            
            result = crew.kickoff()
            formatted_content = result.raw if hasattr(result, 'raw') else str(result)
            
            with open(file_path, "w") as f:
                f.write(formatted_content)
                
            print(f"  Finished formatting {filename}.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AI Book Generator")
    parser.add_argument("--outline", default="config/outline.md", help="Path to the outline file")
    parser.add_argument("--start", type=int, default=1, help="Chapter number to start from")
    parser.add_argument("--no-skip", action="store_false", dest="skip", help="Don't skip existing chapters")
    parser.add_argument("--sleep", type=int, default=30, help="Seconds to sleep between chapters")
    parser.add_argument("--format-only", action="store_true", help="Only run the formatter pass")
    parser.set_defaults(skip=True)
    
    args = parser.parse_args()
    
    generator = BookGenerator()
    
    if args.format_only:
        generator.run_formatter()
    else:
        # Run regular generation
        generator.run(outline_path=args.outline, start_chapter=args.start, skip_existing=args.skip, sleep_between_chapters=args.sleep)
        
        # After generation, run the formatter
        generator.run_formatter()
