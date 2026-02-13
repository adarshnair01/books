export interface Visual {
    type: 'text_overlay' | 'image' | 'code';
    content: string;
    style?: 'kinetic' | 'static' | 'code_block' | 'meme';
}

export interface Segment {
    text: string;
    visual: Visual;
    transition?: 'fade' | 'slide' | 'zoom' | 'none';
    audio_cue?: string;
    durationInFrames?: number; // Calculated field
}

export interface VideoScript {
    title: string;
    segments: Segment[];
    totalDurationInFrames?: number; // Calculated field
}
