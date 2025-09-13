# RealSense Vision Toolkit

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org/)

A modular toolkit for Intel RealSense cameras with computer vision utilities. Designed for easy integration into computer vision applications with clear separation of concerns and robust error handling.

## Features

- ✅ Modular OOP design with clear separation of concerns
- ✅ Configurable camera streaming with error handling
- ✅ Blue cube detection with customizable color thresholds
- ✅ Coordinate transformation between camera and world spaces
- ✅ Sample bag file generation for testing
- ✅ Comprehensive unit tests with CI integration
- ✅ Headless-friendly visualization

## Installation

### Standard Installation (without RealSense hardware dependencies)
```bash
git clone https://github.com/Mostafasaad1/RealSense-Vision-Toolkit.git
cd RealSense-Vision-Toolkit
pip install -r requirements.txt
```

### Full Installation (with RealSense hardware support)
```bash
pip install "realsense_vision_toolkit[realsense]"
```

For development installation:
```bash
pip install -e .
```

## Getting Started

### Basic Usage

```python
from realsense_vision_toolkit import RealSenseCamera, BlueCubeDetector

# Initialize camera
camera = RealSenseCamera()
camera.start()

# Get frames
frames = camera.get_frames(align_to=rs.stream.color)

# Detect blue cube
detector = BlueCubeDetector()
success, position, vertices = detector.detect(frames['color'], frames['depth'])

if success:
    print(f"Cube detected at position: {position}")
    # Draw on image
    color_img = frame_to_array(frames['color'])
    intrinsics = camera.get_intrinsics(frames['color'])
    detector.draw_cube(color_img, vertices, intrinsics)
    cv2.imshow('Detection', color_img)
    cv2.waitKey(0)

camera.stop()
```

### Sample Data Generation

Generate a sample bag file for testing:

```bash
python samples/record_sample_bag.py
```

This will record 5 seconds of camera data to `sample.bag` in the current directory.

## Examples

### Multi-Stream Visualization

```bash
python examples/multi_stream_demo.py
```

Shows real-time visualization of depth, color, and infrared streams.

### Object Detection Demo

```bash
python examples/object_detection_demo.py
```

Detects blue cubes in real-time with 3D visualization.

### Coordinate Transformation Demo

```bash
python examples/coordinate_transform_demo.py
```

Click on objects in the color stream to see their 3D coordinates in camera and world spaces.

## API Documentation

See [API_REFERENCE.md](docs/API_REFERENCE.md) for detailed documentation of all classes and methods.
