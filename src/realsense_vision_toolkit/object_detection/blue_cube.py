import cv2
import numpy as np
from typing import Tuple, Optional, Union, List
from .base import BaseObjectDetector
from ..utils import get_intrinsics, deproject_pixel_to_point

try:
    import pyrealsense2 as rs
except ImportError:
    rs = None

class BlueCubeDetector(BaseObjectDetector):
    """Detects blue cubes in RealSense camera streams"""
    
    def __init__(self, 
                 lower_blue: np.ndarray = np.array([110, 50, 50]),
                 upper_blue: np.ndarray = np.array([130, 255, 255]),
                 cube_size: float = 0.1,
                 min_contour_area: int = 100,
                 max_aspect_ratio: float = 2.0):
        """
        Initialize blue cube detector
        
        Args:
            lower_blue: Lower HSV threshold for blue color
            upper_blue: Upper HSV threshold for blue color
            cube_size: Size of the cube in meters (default 0.1m)
            min_contour_area: Minimum area for contour to be considered
            max_aspect_ratio: Maximum aspect ratio for contour (width/height)
        """
        self.lower_blue = lower_blue
        self.upper_blue = upper_blue
        self.cube_size = cube_size
        self.min_contour_area = min_contour_area
        self.max_aspect_ratio = max_aspect_ratio
    
    def detect(self, color_frame, depth_frame) -> Tuple[bool, Optional[Union[list, np.ndarray]], Optional[np.ndarray]]:
        """
        Detect blue cubes in the color frame and return their 3D position
        
        Args:
            color_frame: Color frame from camera
            depth_frame: Depth frame from camera
            
        Returns:
            Tuple containing:
                - success (bool): Whether detection was successful
                - position (list or None): 3D position of detected object
                - vertices (numpy.ndarray or None): Object vertices for visualization
        """
        color_img = self._preprocess_color(color_frame)
        if color_img is None:
            return False, None, None
        
        # Convert RGB to HSV
        hsv = cv2.cvtColor(color_img, cv2.COLOR_BGR2HSV)
        
        # Threshold the HSV image to get only blue colors
        mask = cv2.inRange(hsv, self.lower_blue, self.upper_blue)
        
        # Apply morphology to reduce noise
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours
        filtered_contours = self._filter_contours(contours, 
                                                self.min_contour_area, 
                                                self.max_aspect_ratio)
        
        for contour in filtered_contours:
            # Approximate the contour to a polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # If the polygon has 4 vertices, it is possibly a cube
            if len(approx) == 4:
                # Get centroid of contour
                M = cv2.moments(contour)
                if M["m00"] == 0:
                    continue
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                
                depth_value = self._get_depth_value(depth_frame, cX, cY)
                
                if depth_value > 0:
                    # Convert pixel coordinates to world coordinates
                    intrinsics = get_intrinsics(depth_frame)
                    if intrinsics:
                        x, y, z = deproject_pixel_to_point(intrinsics, [cX, cY], depth_value)
                        
                        # Calculate cube vertices for visualization
                        half_side = self.cube_size / 2
                        vertices = np.array([
                            [x - half_side, y - half_side, z - half_side],
                            [x + half_side, y - half_side, z - half_side],
                            [x + half_side, y + half_side, z - half_side],
                            [x - half_side, y + half_side, z - half_side],
                            [x - half_side, y - half_side, z + half_side],
                            [x + half_side, y - half_side, z + half_side],
                            [x + half_side, y + half_side, z + half_side],
                            [x - half_side, y + half_side, z + half_side]
                        ])
                        
                        return True, (x, y, z), vertices
        
        return False, None, None
    
    def draw_cube(self, image: np.ndarray, vertices: np.ndarray, 
                 intrinsics: 'rs.intrinsics', 
                 color: Tuple[int, int, int] = (0, 255, 0),
                 thickness: int = 2) -> np.ndarray:
        """
        Draw a cube on the image by projecting 3D vertices to 2D
        
        Args:
            image: Image to draw on
            vertices: 8x3 array of cube vertices
            intrinsics: Camera intrinsics
            color: Color of the cube edges
            thickness: Thickness of the cube edges
            
        Returns:
            Image with cube drawn
        """
        # Project 3D vertices to 2D
        projected_vertices = []
        for vertex in vertices:
            pixel = rs.rs2_project_point_to_pixel(intrinsics, vertex)
            projected_vertices.append((int(pixel[0]), int(pixel[1])))
        
        # Define edges of the cube
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Bottom face
            (4, 5), (5, 6), (6, 7), (7, 4),  # Top face
            (0, 4), (1, 5), (2, 6), (3, 7)   # Vertical edges
        ]
        
        # Draw edges
        for edge in edges:
            start = projected_vertices[edge[0]]
            end = projected_vertices[edge[1]]
            cv2.line(image, start, end, color, thickness)
        
        return image