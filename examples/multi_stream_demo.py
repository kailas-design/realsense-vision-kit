#!/usr/bin/env python3
"""
Multi-stream visualization demo for RealSense cameras
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from realsense_vision_toolkit import RealSenseCamera

def main():
    # Initialize and start stream
    camera = RealSenseCamera()
    camera.start()
    
    print("Starting multi-stream visualization. Press Ctrl+C to quit.")
    
    try:
        # Display multi-view
        camera.show_multiview(figsize=(12, 8))
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        # Release resources
        camera.stop()
        print("Stream stopped")

if __name__ == "__main__":
    main()