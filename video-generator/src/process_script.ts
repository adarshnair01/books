import * as fs from 'fs';
import { VideoScript, Segment } from './types';

export function calculateScriptDuration(script: VideoScript, fps: number = 30): VideoScript {
    const WORDS_PER_MINUTE = 300; // Much faster pace as requested (approx 2x normal)
    const WORDS_PER_SECOND = WORDS_PER_MINUTE / 60;
    const MIN_DURATION_SEC = 1.5; // Reduced minimum duration

    let totalFrames = 0;

    const processedSegments = script.segments.map(segment => {
        const wordCount = segment.text.split(/\s+/).length;
        let durationSeconds = wordCount / WORDS_PER_SECOND;

        // Add buffer for visual absorption
        if (segment.visual.type === 'image' || segment.visual.type === 'code') {
            durationSeconds += 1.0; // Reduced buffer from 1.5
        }

        durationSeconds = Math.max(MIN_DURATION_SEC, durationSeconds);
        const durationInFrames = Math.ceil(durationSeconds * fps);

        totalFrames += durationInFrames;

        return {
            ...segment,
            durationInFrames
        };
    });

    return {
        ...script,
        segments: processedSegments,
        totalDurationInFrames: totalFrames
    };
}

// CLI to process and output enriched JSON
if (require.main === module) {
    const args = process.argv.slice(2);
    if (args.length < 1) {
        console.error("Usage: ts-node process_script.ts <input_json_path>");
        process.exit(1);
    }

    const inputPath = args[0];
    try {
        const rawData = fs.readFileSync(inputPath, 'utf-8');
        const script: VideoScript = JSON.parse(rawData);
        const enrichedScript = calculateScriptDuration(script);
        console.log(JSON.stringify(enrichedScript, null, 2));
    } catch (e) {
        console.error(`Error parsing script: ${e}`);
        process.exit(1);
    }
}
