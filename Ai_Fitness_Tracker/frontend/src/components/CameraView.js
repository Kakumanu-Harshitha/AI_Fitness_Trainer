import React, { useEffect, useRef, useState, forwardRef } from 'react';
import * as mpPose from '@mediapipe/pose';
import { Camera } from '@mediapipe/camera_utils';
import { drawConnectors, drawLandmarks } from '@mediapipe/drawing_utils';

/**
 * CameraView Component for React Web
 * Uses MediaPipe Pose for AI tracking with video and canvas overlay.
 */
const CameraView = forwardRef(({ type = 'front', onLandmarks, style, children }, ref) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const poseRef = useRef(null);
  const cameraRef = useRef(null);
  const onLandmarksRef = useRef(onLandmarks);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  // Keep onLandmarksRef up to date
  useEffect(() => {
    onLandmarksRef.current = onLandmarks;
  }, [onLandmarks]);

  useEffect(() => {
    let active = true;
    let loadingTimeout = null;

    async function initMediaPipe() {
      try {
        setLoading(true);
        
        // Timeout if loading takes too long (e.g., 15 seconds)
        loadingTimeout = setTimeout(() => {
          if (active && loading) {
            setError('MediaPipe is taking too long to load. Please check your internet connection and refresh.');
            setLoading(false);
          }
        }, 15000);

        // Initialize Pose with specific version for stability
        const pose = new mpPose.Pose({
          locateFile: (file) => {
            return `https://cdn.jsdelivr.net/npm/@mediapipe/pose@${mpPose.VERSION}/${file}`;
          }
        });

        if (!active) {
          pose.close();
          return;
        }

        pose.setOptions({
          modelComplexity: 1,
          smoothLandmarks: true,
          enableSegmentation: false,
          minDetectionConfidence: 0.5,
          minTrackingConfidence: 0.5
        });

        pose.onResults((results) => {
          if (!active || !canvasRef.current || !videoRef.current) return;

          const canvas = canvasRef.current;
          const ctx = canvas.getContext('2d');
          const videoWidth = videoRef.current.videoWidth;
          const videoHeight = videoRef.current.videoHeight;

          if (canvas.width !== videoWidth || canvas.height !== videoHeight) {
            canvas.width = videoWidth;
            canvas.height = videoHeight;
          }

          ctx.save();
          ctx.clearRect(0, 0, canvas.width, canvas.height);

          if (results.poseLandmarks) {
            // Draw skeleton
            drawConnectors(ctx, results.poseLandmarks, mpPose.POSE_CONNECTIONS, {
              color: '#B4FF39',
              lineWidth: 4
            });
            drawLandmarks(ctx, results.poseLandmarks, {
              color: '#FF0000',
              lineWidth: 2,
              radius: 4
            });

            // Pass landmarks to parent
            if (onLandmarksRef.current) {
              try {
                // Pass normalized landmarks (0-1) as expected by the AI engines
                const normalizedLandmarks = results.poseLandmarks.map(lm => ({
                  x: lm.x,
                  y: lm.y,
                  z: lm.z,
                  score: lm.visibility !== undefined ? lm.visibility : 1.0
                }));
                onLandmarksRef.current(normalizedLandmarks);
              } catch (e) {
                console.warn('[CameraView] Error in onLandmarks callback:', e);
              }
            }
          }
          ctx.restore();
        });

        poseRef.current = pose;

        // Initialize Camera
        if (videoRef.current) {
          const camera = new Camera(videoRef.current, {
            onFrame: async () => {
              if (active && poseRef.current && videoRef.current) {
                // Ensure video is ready and has dimensions
                if (videoRef.current.readyState < 2 || videoRef.current.videoWidth === 0) {
                  return;
                }
                
                try {
                  await poseRef.current.send({ image: videoRef.current });
                } catch (e) {
                  // Only log if not a "waiting on dependencies" or "null" error we're already seeing
                  if (!e.message?.includes('null') && !e.message?.includes('dependencies')) {
                    console.warn('[CameraView] Frame processing error:', e);
                  }
                }
              }
            },
            width: 640,
            height: 480
          });
          
          if (!active) {
            pose.close();
            return;
          }

          cameraRef.current = camera;
          await camera.start();
          
          if (active) {
            clearTimeout(loadingTimeout);
            setLoading(false);
          } else {
            camera.stop();
            pose.close();
          }
        }
      } catch (err) {
        if (active) {
          clearTimeout(loadingTimeout);
          console.error('[CameraView] Error:', err);
          setError(err.message || 'Failed to start camera');
          setLoading(false);
        }
      }
    }

    initMediaPipe();

    return () => {
      active = false;
      clearTimeout(loadingTimeout);
      if (cameraRef.current) {
        try { cameraRef.current.stop(); } catch (e) {}
        cameraRef.current = null;
      }
      if (poseRef.current) {
        try { poseRef.current.close(); } catch (e) {}
        poseRef.current = null;
      }
    };
  }, []); // Only run once on mount

  return (
    <div className={`relative w-full h-full bg-black overflow-hidden ${style || ''}`}>
      {loading && (
        <div className="absolute inset-0 flex flex-col items-center justify-center z-10 bg-black bg-opacity-50">
          <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-4 text-primary font-semibold">Starting AI Camera...</p>
        </div>
      )}
      
      {error && (
        <div className="absolute inset-0 flex flex-col items-center justify-center z-10 bg-black bg-opacity-80 p-4 text-center">
          <p className="text-red-500">{error}</p>
        </div>
      )}

      <video
        ref={videoRef}
        className="absolute inset-0 w-full h-full object-contain scale-x-[-1]"
        playsInline
        muted
      />
      
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full object-contain scale-x-[-1]"
      />
      
      <div className="relative z-20 w-full h-full">
        {children}
      </div>
    </div>
  );
});

export default CameraView;
