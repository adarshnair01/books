import { AbsoluteFill, useVideoConfig, useCurrentFrame, interpolate, spring, staticFile } from 'remotion';
import React from 'react';
import { VideoScript, Segment } from './types';
import './style.css';

export const ChapterVideo: React.FC<VideoScript> = ({ title, segments }) => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();

    // Calculate start frame for each segment
    let currentStartFrame = 0;
    const segmentsWithTiming = (segments || []).map(segment => {
        const start = currentStartFrame;
        const duration = segment.durationInFrames || 90; // Fallback
        currentStartFrame += duration;
        return { ...segment, startFrame: start, endFrame: start + duration };
    });

    // Find active segment
    const activeSegment = segmentsWithTiming.find(
        s => frame >= s.startFrame && frame < s.endFrame
    );

    // Fallback if no active segment (e.g. intro/outro or error)
    if (!activeSegment) {
        if (frame < 0) return <AbsoluteFill style={{ backgroundColor: 'white' }}><h1>{title}</h1></AbsoluteFill>;
        return <AbsoluteFill style={{ backgroundColor: 'black', color: 'white', display: 'flex', justifyContent: 'center', alignItems: 'center' }}><h1>End of Chapter</h1></AbsoluteFill>;
    }

    // Animation for text (spring pop-up and slide up)
    const segmentFrame = frame - activeSegment.startFrame;

    // Dynamic Spring for Scale
    const scale = spring({
        frame: segmentFrame,
        fps,
        config: {
            damping: 12,
            stiffness: 200,
        }
    });

    // Fade in
    const opacity = interpolate(segmentFrame, [0, 5], [0, 1]);

    // Slide up
    const translateY = interpolate(segmentFrame, [0, 10], [50, 0], { extrapolateRight: 'clamp' });

    // Dynamic background movement (subtle zoom)
    const bgScale = interpolate(segmentFrame, [0, 150], [1, 1.1]);

    return (
        <AbsoluteFill style={{ backgroundColor: 'white', fontFamily: 'Arial' }}>
            {/* Background/Visual Layer */}
            <AbsoluteFill style={{ overflow: 'hidden' }}>
                {activeSegment.visual.type === 'image' && (
                    <img
                        src={staticFile(activeSegment.visual.content)}
                        style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover',
                            transform: `scale(${bgScale})`
                        }}
                    />
                )}
                {activeSegment.visual.type === 'text_overlay' && (
                    <div style={{
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center',
                        height: '100%',
                        flexDirection: 'column',
                        padding: 50,
                        textAlign: 'center',
                        backgroundColor: activeSegment.visual.content.length < 50 ? '#ffcc00' : 'white' // Pop color for short text
                    }}>
                        <h1 style={{
                            fontSize: 100,
                            fontWeight: 'bold',
                            opacity,
                            transform: `scale(${scale})`,
                            textShadow: '0px 10px 40px rgba(0,0,0,0.2)',
                            color: '#333'
                        }}>
                            {activeSegment.visual.content}
                        </h1>
                    </div>
                )}
                {activeSegment.visual.type === 'code' && (
                    <div style={{
                        padding: 40,
                        backgroundColor: '#1e1e1e',
                        color: '#d4d4d4',
                        fontFamily: 'monospace',
                        fontSize: 24,
                        height: '100%',
                        whiteSpace: 'pre-wrap',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        transform: `scale(${scale})`
                    }}>
                        {activeSegment.visual.content}
                    </div>
                )}
            </AbsoluteFill>

            {/* Title Watermark */}
            <div style={{ position: 'absolute', top: 30, left: 30, fontSize: 24, opacity: 0.5 }}>
                {title}
            </div>

        </AbsoluteFill>
    );
};
