import numpy as np
from typing import Optional

class FakeIntrinsics:
    """Mock intrinsics for testing without real pyrealsense2"""
    def __init__(self, width=640, height=480, fx=600, fy=600, ppx=320, ppy=240, model=0):
        self.width = width
        self.height = height
        self.fx = fx
        self.fy = fy
        self.ppx = ppx
        self.ppy = ppy
        self.model = model

class FakeFrame:
    """Mock frame for testing without real pyrealsense2"""
    def __init__(self, width=640, height=480, is_depth=False, data=None):
        self._width = width
        self._height = height
        self._is_depth = is_depth
        self._data = data if data is not None else np.zeros((height, width), dtype=np.uint16)
    
    def get_data(self):
        return self._data
    
    def is_depth_frame(self):
        return self._is_depth
    
    def is_video_frame(self):
        return not self._is_depth
    
    def get_distance(self, x, y):
        # Return a fixed depth value for simplicity
        return 1.0
    
    def profile(self):
        class Profile:
            def as_video_stream_profile(self):
                return self
            def intrinsics(self):
                return FakeIntrinsics()
        return Profile()