# Computer Vision Assignments - Unified Web Application

This repository contains all Computer Vision assignments (1-7) integrated into a single unified web application.

## Video Demonstrations

| Module | Description | Video Link |
|--------|-------------|------------|
| Module 1 | Camera Calibration & Dimension Measurement | [Watch Video](https://drive.google.com/file/d/1cvrgNp7YoITegDZFKveEFbhqQga37B3K/view?usp=sharing) |
| Module 2 | Template Matching & Deblurring | [Watch Video](https://drive.google.com/file/d/1Jl1ZsdpUTr4e_y0h_fU3hWggZQJ8Svzi/view?usp=sharing) |
| Module 3 | Edge Detection & ArUco Markers | [Watch Video](https://drive.google.com/file/d/10KImFDGFTNXxI9hhYvKuwYkzzq0yYj1c/view?usp=sharing) |
| Module 4 | Panorama Stitching & SIFT | [Watch Video](https://drive.google.com/file/d/1GcjtoDagd7SZoNjO64WZmDhyupkvfuwQ/view?usp=sharing) |
| Module 5-6 | Real-Time Object Tracking | [Watch Video](https://drive.google.com/file/d/1508xl64b-zQVvs7fHTUILZMOXWkQsLPl/view?usp=sharing) |
| Module 7 | Stereo Vision & Pose Tracking | [Watch Video](https://drive.google.com/file/d/1XSQzozKBHpRhBBbFX98lb4JOj9nwJ05Z/view?usp=sharing) |

## Structure

```
.
├── index.html                    # Main hub page
├── assignments/
│   ├── assignment1/              # Camera Calibration & Dimension Measurement
│   ├── assignment2/              # Template Matching & Deblurring
│   ├── assignment3/              # Edge Detection & ArUco Markers
│   ├── assignment4/              # Panorama Stitching & SIFT
│   ├── assignment5-6/            # Real-Time Object Tracking
│   └── assignment7/              # Stereo Vision & Pose Tracking
└── README.md
```

## Getting Started

1. **Open the main hub**: Open `index.html` in your web browser
2. **Navigate to assignments**: Click on any assignment card to open that assignment
3. **Backend requirements**: 
   - Assignment 4: Requires Python scripts (run separately)
   - Assignment 7: Requires Flask backend (run `python task1_backend.py`)

## Assignment Details

### Assignment 1: Camera Calibration & Dimension Measurement
- Real-world dimension measurement from images
- Supports image upload and webcam capture
- Uses camera intrinsics for perspective projection

### Assignment 2: Template Matching & Deblurring
- Template matching using correlation methods
- Multi-scale and rotation support
- Fourier-based deblurring and region blurring

### Assignment 3: Edge Detection & ArUco Markers
- Edge and corner detection
- Gradient magnitude/angle, LoG, Harris corners
- ArUco marker segmentation
- Boundary detection and SAM2 comparison

### Assignment 4: Panorama Stitching & SIFT
- Panorama stitching using OpenCV
- Custom SIFT implementation from scratch
- Requires Python backend for full functionality

### Assignment 5-6: Real-Time Object Tracking
- Marker-based tracking (ArUco/QR)
- Marker-less region tracking
- SAM2 segmentation-based tracking

### Assignment 7: Stereo Vision & Pose Tracking
- Stereo camera calibration and 3D measurement
- Real-time pose and hand tracking using MediaPipe
- Requires Flask backend for stereo calibration

## Requirements

### Browser Requirements
- Modern browser with JavaScript enabled
- Webcam access (for assignments with camera features)
- OpenCV.js (loaded from CDN for most assignments)

### Python Requirements (for Assignment 4 & 7)
- Python 3.7+
- OpenCV
- NumPy
- Flask (for Assignment 7)
- See `assignments/assignment4/requirements.txt` and `assignments/assignment7/requirements.txt`

## Running Backend Services

### Assignment 7 Backend
```bash
cd assignments/assignment7
python task1_backend.py
```
The backend will run on `http://localhost:5001`

## Notes

- All assignments are self-contained and can run independently
- Some assignments require external dependencies (OpenCV.js, MediaPipe, etc.) loaded from CDN
- Image/data files should be placed in the respective assignment folders if needed
- The original assignment folders are preserved for reference

## Browser Compatibility

- Chrome/Edge (recommended)
- Firefox
- Safari

## License

This is an academic project for Computer Vision coursework.
