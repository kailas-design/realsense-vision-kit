import unittest
import numpy as np
from unittest.mock import MagicMock, patch
from realsense_vision_toolkit.object_detection.blue_cube import BlueCubeDetector
from realsense_vision_toolkit.utils import frame_to_array
from .helpers import FakeIntrinsics, FakeFrame

class TestBlueCubeDetector(unittest.TestCase):
    def setUp(self):
        self.detector = BlueCubeDetector()
        
        # Create mock color frame with blue square
        self.mock_color_frame = MagicMock()
        self.mock_color_frame.get_data.return_value = np.zeros((480, 640, 3), dtype=np.uint8)
        self.mock_color_frame.get_data.return_value[20:40, 20:40] = [255, 0, 0]  # Blue in BGR
        
        # Create mock depth frame
        self.mock_depth_frame = MagicMock()
        self.mock_depth_frame.get_distance.return_value = 1.0
        
        # Create fake intrinsics
        self.fake_intrinsics = FakeIntrinsics()
    
    def test_detect_blue_cube(self):
        # Test detection with valid blue cube
        success, position, vertices = self.detector.detect(self.mock_color_frame, self.mock_depth_frame)
        self.assertTrue(success)
        self.assertIsNotNone(position)
        self.assertIsNotNone(vertices)
        self.assertEqual(len(vertices), 8)
        self.assertAlmostEqual(position[2], 1.0, places=5)
    
    def test_no_detection(self):
        # Create empty color frame
        empty_color_frame = MagicMock()
        empty_color_frame.get_data.return_value = np.zeros((480, 640, 3), dtype=np.uint8)
        
        success, position, vertices = self.detector.detect(empty_color_frame, self.mock_depth_frame)
        self.assertFalse(success)
        self.assertIsNone(position)
        self.assertIsNone(vertices)
    
    def test_invalid_depth(self):
        # Create depth frame with zero depth
        invalid_depth_frame = MagicMock()
        invalid_depth_frame.get_distance.return_value = 0.0
        
        success, position, vertices = self.detector.detect(self.mock_color_frame, invalid_depth_frame)
        self.assertFalse(success)
        self.assertIsNone(position)
        self.assertIsNone(vertices)
    
    def test_custom_color_thresholds(self):
        # Test with custom color thresholds
        custom_detector = BlueCubeDetector(
            lower_blue=np.array([100, 100, 100]),
            upper_blue=np.array([120, 255, 255])
        )
        
        success, position, vertices = custom_detector.detect(self.mock_color_frame, self.mock_depth_frame)
        self.assertTrue(success)
    
    def test_draw_cube(self):
        # Test drawing cube on image
        _, _, vertices = self.detector.detect(self.mock_color_frame, self.mock_depth_frame)
        color_img = frame_to_array(self.mock_color_frame)
        
        result_img = self.detector.draw_cube(color_img, vertices, self.fake_intrinsics)
        self.assertIsNotNone(result_img)
        self.assertEqual(result_img.shape, (480, 640, 3))
    
    def test_contour_filtering(self):
        # Test contour filtering with min_area and aspect_ratio
        detector = BlueCubeDetector(min_contour_area=1000, max_aspect_ratio=1.5)
        
        # Create a large rectangle (should pass)
        large_rect = np.array([[[10, 10]], [[10, 100]], [[100, 100]], [[100, 10]]])
        filtered = detector._filter_contours([large_rect])
        self.assertEqual(len(filtered), 1)
        
        # Create a small rectangle (should be filtered out)
        small_rect = np.array([[[10, 10]], [[10, 15]], [[15, 15]], [[15, 10]]])
        filtered = detector._filter_contours([small_rect])
        self.assertEqual(len(filtered), 0)
        
        # Create a rectangle with high aspect ratio (should be filtered out)
        tall_rect = np.array([[[10, 10]], [[10, 100]], [[11, 100]], [[11, 10]]])
        filtered = detector._filter_contours([tall_rect])
        self.assertEqual(len(filtered), 0)

if __name__ == '__main__':
    unittest.main()