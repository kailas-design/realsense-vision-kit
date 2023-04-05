import pyrealsense2 as rs
import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from typing import Dict, Optional, Union, Tuple, TYPE_CHECKING
from .utils import frame_to_array, get_intrinsics, deproject_pixel_to_point

if TYPE_CHECKING:
    from .utils import rs

class CameraConnectionError(Exception):
    """Custom exception for camera connection issues"""
    pass

class RealSenseCamera:
    """Handles RealSense camera streaming and frame processing"""
    
    def __init__(self, config: Optional[Union[dict, rs.config]] = None):
        """
        Initialize RealSense camera with custom configuration
        
        Args:
            config: Either a dictionary of stream parameters or a pre-configured rs.config object
                Example dict: {
                    'depth': (640, 480, rs.format.z16, 30),
                    'color': (640, 480, rs.format.bgr8, 30),
                    'ir': (640, 480, rs.format.y8, 30)
                }
        """
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.profile = None
        self.depth_scale = None
        self._aligner_cache = {}
        
        if config is None:
            self._setup_default_config()
        elif isinstance(config, rs.config):
            self.config = config
        else:
            self._setup_config_from_dict(config)
    
    def _setup_default_config(self):
        """Setup default camera configuration"""
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.config.enable_stream(rs.stream.infrared, 1, 640, 480, rs.format.y8, 30)
        self.config.enable_stream(rs.stream.infrared, 2, 640, 480, rs.format.y8, 30)
    
    def _setup_config_from_dict(self, config_dict: dict):
        """Setup configuration from dictionary"""
        if 'depth' in config_dict:
            self.config.enable_stream(rs.stream.depth, *config_dict['depth'])
        if 'color' in config_dict:
            self.config.enable_stream(rs.stream.color, *config_dict['color'])
        if 'ir' in config_dict:
            self.config.enable_stream(rs.stream.infrared, 1, *config_dict['ir'])
            self.config.enable_stream(rs.stream.infrared, 2, *config_dict['ir'])
    
    def start(self):
        """Start camera pipeline with error handling"""
        try:
            self.profile = self.pipeline.start(self.config)
            depth_sensor = self.profile.get_device().first_depth_sensor()
            self.depth_scale = depth_sensor.get_depth_scale()
        except RuntimeError as e:
            raise CameraConnectionError(
                "Failed to connect to RealSense camera. "
                "Check if camera is connected and not in use by another process."
            ) from e
    
    def stop(self):
        """Stop camera pipeline safely"""
        if self.pipeline is None:
            return
            
        try:
            self.pipeline.stop()
        except Exception as e:
            # Log warning but don't fail
            print(f"Warning: Error stopping pipeline: {e}")
        finally:
            self.profile = None
            self.pipeline = None
    
    def get_frames(self, align_to: Optional[rs.stream] = None) -> Dict[str, rs.frame]:
        """
        Get aligned frames from camera
        
        Args:
            align_to: Stream to align frames to (e.g., rs.stream.color)
        
        Returns:
            Dictionary of frames with keys: 'depth', 'color', 'ir_left', 'ir_right'
        """
        frames = self.pipeline.wait_for_frames()
        
        if align_to is not None:
            if align_to not in self._aligner_cache:
                self._aligner_cache[align_to] = rs.align(align_to)
            align = self._aligner_cache[align_to]
            frames = align.process(frames)
        
        return {
            'depth': frames.get_depth_frame(),
            'color': frames.get_color_frame(),
            'ir_left': frames.get_infrared_frame(1),
            'ir_right': frames.get_infrared_frame(2)
        }
    
    def show_multiview(self, figsize: Tuple[int, int] = (12, 8), 
                      align_to: Optional[rs.stream] = rs.stream.color) -> Tuple[plt.Figure, FuncAnimation]:
        """
        Display multi-view visualization of all streams
        
        Args:
            figsize: Figure size (width, height)
            align_to: Stream to align frames to
            
        Returns:
            Tuple of (figure, animation) for further control
        """
        # Handle headless environments
        if plt.get_backend() == 'Agg':
            # Return without showing in headless environment
            fig, axes = plt.subplots(2, 2, figsize=figsize)
            for ax in axes.flat:
                ax.axis('off')
            return fig, None
        
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        img_plots = []
        
        for ax in axes.flat:
            img_plot = ax.imshow(np.zeros((480, 640, 3), dtype=np.uint8))
            ax.axis('off')
            img_plots.append(img_plot)
        
        plt.tight_layout()
        
        def update(frame):
            frames = self.get_frames(align_to)
            if not all(frames.values()):
                return img_plots
            
            # Convert frames to arrays
            color_img = frame_to_array(frames['color'])
            depth_img = frame_to_array(frames['depth'])
            ir_left = frame_to_array(frames['ir_left'])
            ir_right = frame_to_array(frames['ir_right'])
            
            # Process images for display
            if color_img is not None:
                color_img = cv2.cvtColor(color_img, cv2.COLOR_BGR2RGB)
            else:
                color_img = np.zeros((480, 640, 3), dtype=np.uint8)
            
            if depth_img is not None:
                depth_colormap = cv2.applyColorMap(
                    cv2.convertScaleAbs(depth_img, alpha=0.03), 
                    cv2.COLORMAP_JET
                )
            else:
                depth_colormap = np.zeros((480, 640, 3), dtype=np.uint8)
            
            if ir_left is not None:
                ir_left_bgr = cv2.cvtColor(ir_left, cv2.COLOR_GRAY2BGR)
            else:
                ir_left_bgr = np.zeros((480, 640, 3), dtype=np.uint8)
            
            if ir_right is not None:
                ir_right_bgr = cv2.cvtColor(ir_right, cv2.COLOR_GRAY2BGR)
            else:
                ir_right_bgr = np.zeros((480, 640, 3), dtype=np.uint8)
            
            # Update plots
            img_plots[0].set_data(color_img)
            img_plots[1].set_data(depth_colormap)
            img_plots[2].set_data(ir_left_bgr)
            img_plots[3].set_data(ir_right_bgr)
            
            return img_plots
        
        animation = FuncAnimation(fig, update, frames=None, blit=True, interval=50)
        plt.show()
        return fig, animation
    
    def get_intrinsics(self, frame: rs.frame) -> rs.intrinsics:
        """Get camera intrinsics from a frame"""
        return get_intrinsics(frame)
    
    def deproject_pixel_to_point(self, intrinsics: rs.intrinsics, 
                               pixel: list, depth: float) -> list:
        """Deproject a pixel to a 3D point"""
        return deproject_pixel_to_point(intrinsics, pixel, depth)