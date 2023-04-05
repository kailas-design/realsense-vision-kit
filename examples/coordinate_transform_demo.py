#!/usr/bin/env python3
"""
Coordinate transformation demo for RealSense cameras
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from realsense_vision_toolkit import RealSenseCamera, CoordinateTransformer
import cv2

def main():
    # Initialize camera
    camera = RealSenseCamera()
    camera.start()
    
    # Initialize coordinate transformer
    transformer = CoordinateTransformer()
    
    print("Starting coordinate transformation demo. Click on color image to see coordinates. Press 'q' to quit.")
    
    try:
        while True:
            # Get frames
            frames = camera.get_frames(align_to=rs.stream.color)
            
            # Convert frames to arrays
            color_image = camera.frame_to_array(frames['color'])
            depth_image = camera.frame_to_array(frames['depth'])
            
            if color_image is not None and depth_image is not None:
                # Display images
                cv2.imshow('Color', color_image)
                cv2.imshow('Depth', depth_image)
                
                # Wait for mouse click
                def mouse_callback(event, x, y, flags, param):
                    if event == cv2.EVENT_LBUTTONDOWN:
                        print(f"Clicked at color pixel: ({x}, {y})")
                        
                        # Get depth value at clicked point
                        depth_value = frames['depth'].get_distance(x, y)
                        if depth_value <= 0:
                            print("No valid depth value at this location")
                            return
                        
                        # Transform to 3D point in camera coordinates
                        intrinsics = camera.get_intrinsics(frames['depth'])
                        point = camera.deproject_pixel_to_point(intrinsics, [x, y], depth_value)
                        print(f"3D point in camera coordinates: {point}")
                        
                        # Transform to world coordinates (assuming camera at origin)
                        world_point = transformer.camera_to_world(point)
                        print(f"3D point in world coordinates: {world_point}")
                
                # Set mouse callback
                cv2.setMouseCallback('Color', mouse_callback)
            
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