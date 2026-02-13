import json
import argparse
import sys
from datetime import timedelta

def frames_to_timestamp(frames, fps):
    seconds = frames / fps
    td = timedelta(seconds=seconds)
    # timedelta string is like "0:00:05.123456"
    # SRT format is HH:MM:SS,mmm
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    milliseconds = int(td.microseconds / 1000)
    
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def generate_srt(json_path, output_path, fps=30):
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        segments = data.get('segments', [])
        
        srt_content = ""
        current_frame = 0
        
        for i, segment in enumerate(segments):
            duration = segment.get('durationInFrames', 90)
            start_frame = current_frame
            end_frame = current_frame + duration
            
            start_time = frames_to_timestamp(start_frame, fps)
            end_time = frames_to_timestamp(end_frame, fps)
            
            text = segment.get('text', '').strip()
            
            # SRT index starts at 1
            srt_content += f"{i + 1}\n"
            srt_content += f"{start_time} --> {end_time}\n"
            srt_content += f"{text}\n\n"
            
            current_frame += duration
            
        with open(output_path, 'w') as f:
            f.write(srt_content)
            
        print(f"Successfully generated SRT captions at {output_path}")
        return True
        
    except Exception as e:
        print(f"Error generating SRT: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert JSON video script to SRT subtitles.")
    parser.add_argument("input_json", help="Path to enriched JSON script")
    parser.add_argument("output_srt", help="Path to output SRT file")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second (default: 30)")
    
    args = parser.parse_args()
    
    generate_srt(args.input_json, args.output_srt, args.fps)
