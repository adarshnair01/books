import { Composition } from 'remotion';
import { ChapterVideo } from './ChapterVideo';
import { VideoScript } from './types';
import './style.css';

export const RemotionRoot: React.FC = () => {
    return (
        <>
            <Composition
                id="ChapterVideo"
                component={ChapterVideo}
                durationInFrames={150} // Fallback
                fps={30}
                width={1920}
                height={1080}
                defaultProps={{
                    title: 'Title',
                    segments: []
                } as VideoScript}
                calculateMetadata={async ({ props }) => {
                    // Props are untyped in calculateMetadata usually, so we cast
                    const videoProps = props as unknown as VideoScript;

                    let duration = 0;
                    if (videoProps.totalDurationInFrames) {
                        duration = videoProps.totalDurationInFrames;
                    } else if (videoProps.segments) {
                        duration = videoProps.segments.reduce((acc, item) => acc + (item.durationInFrames || 90), 0);
                    }

                    return {
                        durationInFrames: Math.max(30, duration),
                        props: videoProps
                    };
                }}
            />
        </>
    );
};
