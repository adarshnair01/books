from src.main import BookGenerator
from src.utils import load_env

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Demo Book Generator")
    parser.add_argument("--start", type=int, default=1, help="Chapter number to start from")
    args = parser.parse_args()

    load_env()
    generator = BookGenerator()
    # Use the small demo outline to save tokens
    generator.run(outline_path="config/demo_outline.md", start_chapter=args.start)
