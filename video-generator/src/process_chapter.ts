import * as fs from 'fs';
import * as path from 'path';

// This script will be run by node, so we use CommonJS or configure node to use modules if needed.
// For now, let's assume TS-Node execution.

export interface TimelineItem {
    type: 'title' | 'heading' | 'text' | 'image';
    content: string;
    duration: number;
}


export function parseChapter(markdownPath: string, imageBaseProps: { webPath: string; localPath: string }, preview: boolean = false): { title: string; timeline: TimelineItem[]; totalDuration: number } {
    const content = fs.readFileSync(markdownPath, 'utf-8');
    const lines = content.split('\n');
    const timeline: TimelineItem[] = [];
    let title = "Untitled Chapter";
    let diagramCount = 1;
    let totalDuration = 0;

    const FPS = 30;
    const WORDS_PER_MINUTE = 200;
    const WORDS_PER_SECOND = WORDS_PER_MINUTE / 60;

    for (const line of lines) {
        let item: TimelineItem | null = null;
        if (line.startsWith('# ')) {
            title = line.replace('# ', '').trim();
            item = { type: 'title', content: title, duration: 150 };
        } else if (line.startsWith('## ') || line.startsWith('### ')) {
            const heading = line.replace(/^#+ /, '').trim();
            item = { type: 'heading', content: heading, duration: 90 };
        } else if (line.trim().startsWith('[DIAGRAM:')) {
            // Find the corresponding image file
            try {
                const files = fs.readdirSync(imageBaseProps.localPath);
                const imageFile = files.find(f => f.startsWith(`diagram_${diagramCount}_`) && f.endsWith('.png'));

                if (imageFile) {
                    item = { type: 'image', content: path.join(imageBaseProps.webPath, imageFile), duration: 150 };
                } else {
                    console.warn(`Warning: Image for diagram ${diagramCount} not found in ${imageBaseProps.localPath}`);
                }
                diagramCount++;
            } catch (e) {
                console.warn(`Error reading image directory: ${e}`);
            }
        } else if (line.trim().length > 0) {
            const text = line.trim();
            const wordCount = text.split(/\s+/).length;
            const durationSeconds = Math.max(2, wordCount / WORDS_PER_SECOND);
            item = { type: 'text', content: text, duration: Math.ceil(durationSeconds * FPS) };
        }

        if (item) {
            timeline.push(item);
            totalDuration += item.duration || 0;
        }
    }

    if (preview) {
        totalDuration = Math.min(totalDuration, 900);
    }

    return { title, timeline, totalDuration };
}

// CLI usage
if (require.main === module) {
    const args = process.argv.slice(2);
    if (args.length < 2) {
        console.error("Usage: ts-node process_chapter.ts <markdown_file> <image_dir_name>");
        process.exit(1);
    }

    const markdownPath = args[0];
    const imageDirName = args[1]; // e.g. Chapter_7_...
    const preview = args.includes('--preview');

    // We assume images are symlinked to public/images/
    // So webPath is /images/{imageDirName}
    // And localPath is public/images/{imageDirName} (relative to CWD) or resolved absolute path

    const webPath = `/images/${imageDirName}`;
    const localPath = path.join(process.cwd(), 'public', 'images', imageDirName);

    const result = parseChapter(markdownPath, { webPath, localPath }, preview);
    console.log(JSON.stringify(result, null, 2));
}
