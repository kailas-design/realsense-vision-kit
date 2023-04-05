import pyrealsense2 as rs

def record_sample_bag(output_path: str = "sample.bag", 
                     duration_seconds: int = 5,
                     depth_resolution: tuple = (640, 480),
                     color_resolution: tuple = (640, 480),
                     fps: int = 30):
    """
    Record sample bag file for testing
    
    Args:
        output_path: Path to save the bag file
        duration_seconds: Duration to record in seconds
        depth_resolution: Depth stream resolution (width, height)
        color_resolution: Color stream resolution (width, height)
        fps: Frames per second
    """
    # Create a config and enable recording
    config = rs.config()
    config.enable_stream(rs.stream.depth, 
                        depth_resolution[0], depth_resolution[1], 
                        rs.format.z16, fps)
    config.enable_stream(rs.stream.color, 
                        color_resolution[0], color_resolution[1], 
                        rs.format.bgr8, fps)
    config.enable_record_to_file(output_path)
    
    pipeline = rs.pipeline()
    pipeline.start(config)
    
    print(f"Recording to {output_path} for {duration_seconds} seconds...")
    try:
        for _ in range(fps * duration_seconds):
            pipeline.wait_for_frames()
    finally:
        pipeline.stop()
        print(f"Sample bag recorded to {output_path}")

if __name__ == "__main__":
    record_sample_bag()