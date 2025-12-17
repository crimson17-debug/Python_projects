#  Computer Vision & Sensor Fusion Repository

Welcome to my Computer Vision repository! This project documents my journey and development in Python and OpenCV, ranging from fundamental image processing techniques to advanced applications for autonomous vehicle systems like Lane Detection and Sensor Fusion.

## 📂 Repository Structure

The repository is organized into learning modules and project implementations:

```text
├──  1_readimg_photos/        # Resources (Images/Videos) for testing
├──  opencv/
│   ├── python_oops/         # Object-Oriented Programming concepts in Python
│   ├── cameracode.py        # Script for accessing and handling camera feeds
│   ├── fusion_system.py     # Data fusion logic (likely multi-camera or sensor integration)
│   ├── first.py             
│   └── ...
├── 1_read.py                # Basics: Reading images and video streams
├── 2_reshape.py             # Basics: Resizing and rescaling frames
├── 3_draw.py                # Basics: Drawing shapes and putting text on images
├── 4_draw_multiple_innerboxes.py # Logic:exercise for drawing in cv
└── .gitignore               # Configuration to ignore virtual environments/cache
```

## Key Features

### 1. Fundamentals of OpenCV
* **Image & Video Processing:** Scripts to read, display, and manipulate media formats (`1_read.py`).
* **Frame Transformation:** Logic for resizing, rescaling, and cropping video frames to different resolutions (`2_reshape.py`).
* **Geometric Annotation:** drawing shapes (rectangles, circles, lines) and overlaying text on images (`3_draw.py`).
* **Algorithmic Logic:** Exercises like `4_draw_multiple_innerboxes.py` demonstrate how to control coordinate systems and loops within a visual context.

### 2. Autonomous Systems & Sensor Logic
* **Sensor Fusion:** The `fusion_system.py` module contains logic for integrating data, designed for applications like multi-camera setups or combining sensor inputs for vehicle perception.
* **Camera Integration:** `cameracode.py` handles real-time video capture and stream management.
* **Lane Detection:** (In progress) Algorithms for identifying road boundaries and lanes for self-driving car simulations.

### 3. Object-Oriented Design
* The `python_oops/` directory demonstrates how to structure computer vision code using classes and objects, making the system modular and scalable.

## Tech Stack

* **Language:** Python 3.12.11
* **Core Libraries:**
    * `opencv-python` (cv2) - For all image processing tasks.
    * `numpy` - For matrix operations and array handling.

## Getting Started

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Navya/Python_projects.git](https://github.com/Navya/Python_projects.git)
    ```
2.  **Install dependencies:**
    Ensure you have Python installed, then run:
    ```bash
    pip install opencv-python numpy
    ```
3.  **Run a script:**
    To test the basic drawing logic:
    ```bash
    python 4_draw_multiple_innerboxes.py
    ```
    To run the fusion system logic:
    ```bash
    python opencv/fusion_system.py
    ```

## Future Scope

* **Advanced Lane Finding:** Implementing curved lane detection using perspective transformation.
* **Object Detection:** Integrating YOLO or SSD models for real-time obstacle detection.
* **Hardware Integration:** Testing the fusion system on Raspberry Pi or Jetson Nano with physical cameras.

---
*Maintained by Navya*
