# RealSense Vision Toolkit API Reference

## Overview

The RealSense Vision Toolkit provides modular components for working with Intel RealSense cameras. The toolkit is structured to follow best practices in OOP design with clear separation of concerns.

## Core Components

### `RealSenseCamera`

Handles camera streaming and frame processing.

#### `__init__(config=None)`

Initialize camera with custom configuration.

**Parameters:**
- `config`: Either a dictionary of stream parameters or a pre-configured `rs.config` object
  - Example dictionary format:
    ```python
    {
        'depth': (640, 480, rs.format.z16, 30),
        'color': (640, 480, rs.format.bgr8, 30),
        'ir': (640, 480, rs.format.y8, 30)
    }
    ```

#### `start()`

Start camera pipeline with error handling.

**Raises:**
- `CameraConnectionError`: If camera fails to connect

#### `stop()`

Stop camera pipeline safely.

#### `get_frames(align_to=None)`

Get aligned frames from camera.

**Parameters:**
- `align_to`: Stream to align frames to (e.g., `rs.stream.color`)

**Returns:**
- Dictionary with keys: `'depth'`, `'color'`, `'ir_left'`, `'ir_right'`

#### `show_multiview(figsize=(12, 8), align_to=rs.stream.color)`

Display multi-view visualization of all streams.

**Parameters:**
- `figsize`: Figure size (width, height)
- `align_to`: Stream to align frames to

**Returns:**
- Tuple of (figure, animation) for further control

#### `get_intrinsics(frame)`

Get camera intrinsics from a frame.

**Parameters:**
- `frame`: Frame to extract intrinsics from

**Returns:**
- `rs.intrinsics` object

#### `deproject_pixel_to_point(intrinsics, pixel, depth)`

Deproject a pixel to a 3D point.

**Parameters:**
- `intrinsics`: Camera intrinsics
- `pixel`: Pixel coordinates [x, y]
- `depth`: Depth value at the pixel

**Returns:**
- 3D point coordinates [x, y, z]

---

### `BlueCubeDetector`

Detects blue cubes in RealSense camera streams.

#### `__init__(lower_blue=np.array([110, 50, 50]), upper_blue=np.array([130, 255, 255]), cube_size=0.1, min_contour_area=100, max_aspect_ratio=2.0)`

Initialize blue cube detector.

**Parameters:**
- `lower_blue`: Lower HSV threshold for blue color
- `upper_blue`: Upper HSV threshold for blue color
- `cube_size`: Size of the cube in meters (default 0.1m)
- `min_contour_area`: Minimum contour area to consider
- `max_aspect_ratio`: Maximum aspect ratio for contours (width/height)

#### `detect(color_frame, depth_frame)`

Detect blue cubes in the color frame and return their 3D position.

**Parameters:**
- `color_frame`: Color frame from camera
- `depth_frame`: Depth frame from camera

**Returns:**
- Tuple containing:
  - `success` (bool): Whether detection was successful
  - `position` (list or None): 3D position of detected object
  - `vertices` (numpy.ndarray or None): Object vertices for visualization

#### `draw_cube(image, vertices, intrinsics, color=(0, 255, 0), thickness=2)`

Draw a cube on the image by projecting 3D vertices to 2D.

**Parameters:**
- `image`: Image to draw on
- `vertices`: 8x3 array of cube vertices
- `intrinsics`: Camera intrinsics
- `color`: Color of the cube edges
- `thickness`: Thickness of the cube edges

**Returns:**
- Image with cube drawn

---

### `CoordinateTransformer`

Handles coordinate transformations between camera and world spaces.

#### `__init__(camera_pose=None)`

Initialize coordinate transformer.

**Parameters:**
- `camera_pose`: 4x4 transformation matrix from world to camera coordinates. 
  If None, assumes camera is at world origin.

#### `camera_to_world(point)`

Transform a point from camera coordinates to world coordinates.

**Parameters:**
- `point`: 3D point in camera coordinates (x, y, z)

**Returns:**
- 3D point in world coordinates

#### `world_to_camera(point)`

Transform a point from world coordinates to camera coordinates.

**Parameters:**
- `point`: 3D point in world coordinates (x, y, z)

**Returns:**
- 3D point in camera coordinates

#### `transform_point(point, from_frame, to_frame)`

Transform a point between different coordinate frames.

**Parameters:**
- `point`: 3D point to transform
- `from_frame`: Source frame ('camera' or 'world')
- `to_frame`: Target frame ('camera' or 'world')

**Returns:**
- Transformed point in target frame

---

### Utility Functions

#### `frame_to_array(frame)`

Convert a RealSense frame to a numpy array.

**Parameters:**
- `frame`: RealSense frame to convert

**Returns:**
- Numpy array representation of the frame or None if frame is invalid

#### `get_intrinsics(frame)`

Get camera intrinsics from a frame.

**Parameters:**
- `frame`: Frame to extract intrinsics from

**Returns:**
- `rs.intrinsics` object or None if frame is invalid

#### `deproject_pixel_to_point(intrinsics, pixel, depth)`

Deproject a pixel to a 3D point.

**Parameters:**
- `intrinsics`: Camera intrinsics
- `pixel`: Pixel coordinates [x, y]
- `depth`: Depth value at the pixel

**Returns:**
- 3D point coordinates [x, y, z]