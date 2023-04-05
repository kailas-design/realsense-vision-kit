import unittest
import numpy as np
from realsense_vision_toolkit.coordinate_transformer import CoordinateTransformer

class TestCoordinateTransformer(unittest.TestCase):
    def setUp(self):
        # Identity transform (camera at origin)
        self.transformer_identity = CoordinateTransformer()
        
        # Custom transform (camera shifted 1m along X)
        self.camera_pose = np.array([
            [1, 0, 0, 1],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        self.transformer_shifted = CoordinateTransformer(self.camera_pose)
    
    def test_identity_transform(self):
        # Test camera to world with identity transform
        point = [1.0, 2.0, 3.0]
        world_point = self.transformer_identity.camera_to_world(point)
        np.testing.assert_array_almost_equal(world_point, point)
        
        # Test world to camera with identity transform
        camera_point = self.transformer_identity.world_to_camera(point)
        np.testing.assert_array_almost_equal(camera_point, point)
    
    def test_shifted_transform(self):
        # Camera is shifted 1m along X
        # So world point (0,0,0) should be (-1,0,0) in camera coordinates
        world_point = [0.0, 0.0, 0.0]
        camera_point = self.transformer_shifted.world_to_camera(world_point)
        np.testing.assert_array_almost_equal(camera_point, [-1.0, 0.0, 0.0])
        
        # Camera point (-1,0,0) should be (0,0,0) in world coordinates
        world_point = self.transformer_shifted.camera_to_world([-1.0, 0.0, 0.0])
        np.testing.assert_array_almost_equal(world_point, [0.0, 0.0, 0.0])
    
    def test_transform_point(self):
        # Test transform_point method
        point = [1.0, 2.0, 3.0]
        
        # Camera to world
        result = self.transformer_identity.transform_point(point, "camera", "world")
        np.testing.assert_array_almost_equal(result, point)
        
        # World to camera
        result = self.transformer_identity.transform_point(point, "world", "camera")
        np.testing.assert_array_almost_equal(result, point)
        
        # Test with shifted transform
        result = self.transformer_shifted.transform_point([0.0, 0.0, 0.0], "world", "camera")
        np.testing.assert_array_almost_equal(result, [-1.0, 0.0, 0.0])
    
    def test_invalid_frame(self):
        # Test invalid frame transformation
        with self.assertRaises(ValueError) as context:
            self.transformer_identity.transform_point([1, 2, 3], "invalid", "world")
        self.assertIn("Invalid frame transformation", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            self.transformer_identity.transform_point([1, 2, 3], "camera", "invalid")
        self.assertIn("Invalid frame transformation", str(context.exception))

if __name__ == '__main__':
    unittest.main()