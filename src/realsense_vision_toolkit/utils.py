import pyrealsense2 as rs
import numpy as np
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    import pyrealsense2 as rs

def frame_to_array(frame: Optional[rs.frame]) -> Optional[np.ndarray]:
    """
    Convert a RealSense frame to a numpy array
    
    Args:
        frame: RealSense frame to convert
        
    Returns:
        Numpy array representation of the frame or None if frame is invalid
    """
    if frame is None:
        return None
        
    if frame.is_depth_frame():
        return np.asanyarray(frame.get_data())
    elif frame.is_video_frame():
        return np.asanyarray(frame.get_data())
    else:
        return None

def get_intrinsics(frame: rs.frame) -> Optional[rs.intrinsics]:
    """
    Get camera intrinsics from a frame
    
    Args:
        frame: Frame to extract intrinsics from
        
    Returns:
        Camera intrinsics or None if frame is invalid
    """
    if frame:
        return frame.profile.as_video_stream_profile().intrinsics
    return None

def deproject_pixel_to_point(intrinsics: rs.intrinsics, 
                            pixel: List[int], 
                            depth: float) -> List[float]:
    """
    Deproject a pixel to a 3D point
    
    Args:
        intrinsics: Camera intrinsics
        pixel: Pixel coordinates [x, y]
        depth: Depth value at the pixel
        
    Returns:
        3D point coordinates [x, y, z]
    """
    return rs.rs2_deproject_pixel_to_point(intrinsics, pixel, depth)