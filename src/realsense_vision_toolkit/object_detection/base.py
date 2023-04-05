from typing import Optional, Tuple, Union, List
import numpy as np

class BaseObjectDetector:
    """Base class for object detection with RealSense cameras"""
    
    def detect(self, color_frame, depth_frame) -> Tuple[bool, Optional[Union[list, np.ndarray]], Optional[np.ndarray]]:
        """
        Detect objects in frames
        
        Args:
            color_frame: Color frame from camera
            depth_frame: Depth frame from camera
            
        Returns:
            Tuple containing:
                - success (bool): Whether detection was successful
                - position (list or None): 3D position of detected object
                - vertices (numpy.ndarray or None): Object vertices for visualization
        """
        raise NotImplementedError("Subclasses must implement detect method")
    
    def _preprocess_color(self, color_frame) -> Optional[np.ndarray]:
        """Preprocess color frame for detection"""
        if color_frame is None:
            return None
        return np.asanyarray(color_frame.get_data())
    
    def _get_depth_value(self, depth_frame, x: int, y: int) -> float:
        """Get depth value at specific pixel"""
        if depth_frame is None:
            return 0.0
        return depth_frame.get_distance(x, y)
    
    def _filter_contours(self, contours, min_area: int = 100, max_aspect_ratio: float = 2.0) -> List[np.ndarray]:
        """Filter contours based on area and aspect ratio"""
        filtered = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area:
                continue
                
            rect = cv2.minAreaRect(contour)
            width, height = rect[1]
            aspect_ratio = max(width, height) / min(width, height) if min(width, height) > 0 else float('inf')
            
            if aspect_ratio <= max_aspect_ratio:
                filtered.append(contour)
                
        return filtered