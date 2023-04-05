#!/usr/bin/env python3
"""
3D object detection demo for RealSense cameras
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import cv2
import numpy as np
from realsense_vision_toolkit import RealSenseCamera, BlueCubeDetector

def main():
    # Initialize camera and detector
    camera = RealSenseCamera()
    camera.start()
    detector = BlueCubeDetector()
    
    print("Starting 3D object detection. Press 'q' to quit.")
    
    try:
        while True:
            # Get frames
            frames = camera.get_frames(align_to=rs.stream.color)
            
            # Detect blue cube
            success, position, vertices = detector.detect(frames['color'], frames['depth'])
            
            if success:
                print(f"Cube detected at position: {position}")
                
                # Draw cube on color image
                color_image = camera.frame_to_array(frames['color'])
                if color_image is not None and vertices is not None:
                    intrinsics = camera.get_intrinsics(frames['color'])
                    detector.draw_cube(color_image, vertices, intrinsics)
                    cv2.imshow('Blue Cube Detection', color_image)
            
            # Check for quit key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        # Release resources
        camera.stop()
        cv2.destroyAllWindows()
        print("Stream stopped")

if __name__ == "__main__":
    main()