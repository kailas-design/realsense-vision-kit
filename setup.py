from setuptools import setup, find_packages

setup(
    name="realsense_vision_toolkit",
    version="0.3.0",
    description="A modular toolkit for Intel RealSense cameras with computer vision utilities",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Mostafa Saad",
    author_email="mostafa.saad@ejust.edu.eg",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "opencv-python>=4.5.0",
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
        "scipy>=1.7.0",
    ],
    extras_require={
        "realsense": ["pyrealsense2>=2.50.0"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Image Recognition",
    ],
    python_requires=">=3.7",
)