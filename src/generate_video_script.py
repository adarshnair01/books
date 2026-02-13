import os
import argparse
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional
from src.utils import load_env

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_env()

# --- Data Models ---

class Visual(BaseModel):
    type: str = Field(description="Type of visual: 'text_overlay', 'image', or 'code'")
    content: str = Field(description="Content to display. For 'image', use a placeholder description if actual path is unknown, or the image filename if obvious.")
    style: Optional[str] = Field(description="Visual style: 'kinetic', 'static', 'code_block', 'meme'", default="static")

class Segment(BaseModel):
    text: str = Field(description="The narration text (voiceover) for this segment. Keep it punchy and conversational.")
    visual: Visual = Field(description="The primary visual element to display during this narration.")
    transition: Optional[str] = Field(description="Transition to the NEXT segment: 'fade', 'slide', 'zoom', 'none'", default="fade")
    audio_cue: Optional[str] = Field(description="Audio mood or sound effect: 'upbeat', 'suspense', 'ding', 'scratch_record'", default="neutral")

class VideoScript(BaseModel):
    title: str = Field(description="The title of the video/chapter.")
    segments: List[Segment] = Field(description="List of video segments forming the sequential script.")

# --- Logic ---

def generate_script(chapter_path: str, output_path: str):
    """Generates a video script JSON from a markdown chapter file."""
    
    if not os.path.exists(chapter_path):
        logging.error(f"Chapter file not found: {chapter_path}")
        return

    logging.info(f"Reading chapter: {chapter_path}")
    with open(chapter_path, 'r') as f:
        chapter_content = f.read()

    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    parser = PydanticOutputParser(pydantic_object=VideoScript)

    prompt = PromptTemplate(
        template="""
        You are an expert video scriptwriter for a "Head First" style educational YouTube channel.
        Your goal is to turn the following technical book chapter into an ENGAGING, FUNNY, and VISUALLY DYNAMIC video script.

        **Guidelines:**
        1.  **Tone**: Conversational, witty, energetic. Use analogies, rhetorical questions, and "we". Avoid dry textbook language.
        2.  **Visuals**: Describe what the viewer sees. Use 'text_overlay' for key terms (kinetic typography), 'image' for diagrams/memes, and 'code' for snippets.
            *   IMPORTANT: If the markdown contains an image reference (e.g., `![alt](path)`), try to preserve it or map it to an 'image' visual.
        3.  **Pacing**: Keep segments short. Avoid walls of narration.
        4.  **Audio**: Suggest sound effects (ding, whoosh) and background music moods.
        
        **Chapter Content:**
        {chapter_content}

        **Output Format:**
        {format_instructions}
        """,
        input_variables=["chapter_content"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser

    logging.info("Generating script with Gemini...")
    try:
        script = chain.invoke({"chapter_content": chapter_content})
        
        # Save to file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(script.model_dump_json(indent=2))
        
        logging.info(f"Script saved to: {output_path}")

    except Exception as e:
        logging.error(f"Failed to generate script: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate AI Video Script")
    parser.add_argument("chapter_path", help="Path to input markdown chapter")
    parser.add_argument("output_path", help="Path to output JSON script")
    args = parser.parse_args()

    generate_script(args.chapter_path, args.output_path)
