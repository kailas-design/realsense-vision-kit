import numpy as np
from typing import Optional, Union, List

class CoordinateTransformer:
    """Handles coordinate transformations between camera and world spaces"""
    
    def __init__(self, camera_pose: Optional[np.ndarray] = None):
        """
        Initialize coordinate transformer
        
        Args:
            camera_pose: 4x4 transformation matrix from world to camera coordinates.
                         If None, assumes camera is at world origin.
        """
        self.camera_pose = camera_pose if camera_pose is not None else np.eye(4)
    
    def camera_to_world(self, point: Union[List[float], np.ndarray]) -> np.ndarray:
        """
        Transform a point from camera coordinates to world coordinates
        
        Args:
            point: 3D point in camera coordinates (x, y, z)
            
        Returns:
            3D point in world coordinates
        """
        # Convert to homogeneous coordinates
        point_homogeneous = np.append(point, 1)
        # Apply inverse of camera pose (since camera_pose transforms world->camera)
        world_point = np.linalg.inv(self.camera_pose) @ point_homogeneous
        return world_point[:3]
    
    def world_to_camera(self, point: Union[List[float], np.ndarray]) -> np.ndarray:
        """
        Transform a point from world coordinates to camera coordinates
        
        Args:
            point: 3D point in world coordinates (x, y, z)
            
        Returns:
            3D point in camera coordinates
        """
        # Convert to homogeneous coordinates
        point_homogeneous = np.append(point, 1)
        camera_point = self.camera_pose @ point_homogeneous
        return camera_point[:3]
    
    def transform_point(self, point: Union[List[float], np.ndarray], 
                       from_frame: str, to_frame: str) -> np.ndarray:
        """
        Transform a point between different coordinate frames
        
        Args:
            point: 3D point to transform
            from_frame: Source frame ('camera' or 'world')
            to_frame: Target frame ('camera' or 'world')
            
        Returns:
            Transformed point in target frame
        """
        if from_frame == to_frame:
            return np.array(point)
        
        if from_frame == 'camera' and to_frame == 'world':
            return self.camera_to_world(point)
        elif from_frame == 'world' and to_frame == 'camera':
            return self.world_to_camera(point)
        else:
            raise ValueError(f"Invalid frame transformation. Supported frames: 'camera', 'world'. Got from={from_frame}, to={to_frame}")