import unittest
from unittest.mock import MagicMock, patch
from realsense_vision_toolkit.camera import RealSenseCamera, CameraConnectionError
import pyrealsense2 as rs
import numpy as np
from .helpers import FakeIntrinsics, FakeFrame

class TestRealSenseCamera(unittest.TestCase):
    @patch('pyrealsense2.pipeline')
    @patch('pyrealsense2.config')
    def test_start_success(self, mock_config, mock_pipeline):
        # Mock the pipeline and config
        mock_profile = MagicMock()
        mock_device = MagicMock()
        mock_sensor = MagicMock()
        
        mock_profile.get_device.return_value = mock_device
        mock_device.first_depth_sensor.return_value = mock_sensor
        mock_sensor.get_depth_scale.return_value = 0.001
        
        mock_pipeline.return_value.start.return_value = mock_profile
        mock_pipeline.return_value.wait_for_frames.return_value = MagicMock()
        
        camera = RealSenseCamera()
        camera.start()
        
        self.assertIsNotNone(camera.profile)
        self.assertEqual(camera.depth_scale, 0.001)
    
    @patch('pyrealsense2.pipeline')
    @patch('pyrealsense2.config')
    def test_start_failure(self, mock_config, mock_pipeline):
        mock_pipeline.return_value.start.side_effect = RuntimeError("Camera not connected")
        camera = RealSenseCamera()
        
        with self.assertRaises(CameraConnectionError):
            camera.start()
    
    @patch('pyrealsense2.pipeline')
    @patch('pyrealsense2.config')
    def test_get_frames(self, mock_config, mock_pipeline):
        # Mock frames
        mock_frames = MagicMock()
        mock_frames.get_depth_frame.return_value = FakeFrame(is_depth=True)
        mock_frames.get_color_frame.return_value = FakeFrame(is_depth=False)
        mock_frames.get_infrared_frame.side_effect = [FakeFrame(is_depth=False), FakeFrame(is_depth=False)]
        
        mock_pipeline.return_value.wait_for_frames.return_value = mock_frames
        camera = RealSenseCamera()
        camera.start()
        
        frames = camera.get_frames()
        self.assertIn('depth', frames)
        self.assertIn('color', frames)
        self.assertIn('ir_left', frames)
        self.assertIn('ir_right', frames)
    
    def test_stop_safety(self):
        camera = RealSenseCamera()
        camera.start()
        camera.stop()
        camera.stop()  # Should not crash on second stop
        self.assertIsNone(camera.pipeline)
        self.assertIsNone(camera.profile)
    
    def test_aligner_caching(self):
        camera = RealSenseCamera()
        camera.start()
        
        # First call creates aligner
        frames1 = camera.get_frames(rs.stream.color)
        self.assertEqual(len(camera._aligner_cache), 1)
        
        # Second call with same align_to uses cached aligner
        frames2 = camera.get_frames(rs.stream.color)
        self.assertEqual(len(camera._aligner_cache), 1)
        
        # Different align_to creates new aligner
        frames3 = camera.get_frames(rs.stream.depth)
        self.assertEqual(len(camera._aligner_cache), 2)
    
    @unittest.skipIf(not hasattr(rs, 'stream'), "Requires real pyrealsense2")
    def test_show_multiview(self):
        camera = RealSenseCamera()
        camera.start()
        
        # Test in non-headless mode
        fig, anim = camera.show_multiview(figsize=(4, 3), align_to=rs.stream.color)
        self.assertIsNotNone(fig)
        if anim:
            self.assertIsInstance(anim, plt.animation.FuncAnimation)
        
        camera.stop()

if __name__ == '__main__':
    unittest.main()