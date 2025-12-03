# Setup Guide - Unified Computer Vision Web Application

## Quick Start

1. **Open the main application**: Simply open `index.html` in your web browser
2. **Navigate**: Click on any assignment card to access that assignment
3. **Backend setup** (if needed): See below for assignments requiring Python backends

## Assignment-Specific Setup

### Assignment 1: Camera Calibration & Dimension Measurement
- **Status**: ✅ Ready to use
- **Requirements**: Modern web browser
- **Features**: Works with image uploads or webcam

### Assignment 2: Template Matching & Deblurring
- **Status**: ✅ Ready to use
- **Requirements**: Modern web browser, OpenCV.js (loaded from CDN)
- **Usage**: Upload scene image and template images

### Assignment 3: Edge Detection & ArUco Markers
- **Status**: ✅ Ready to use
- **Requirements**: Modern web browser, OpenCV.js (local build included)
- **Note**: Uses local OpenCV.js build with ArUco support

### Assignment 4: Panorama Stitching & SIFT
- **Status**: ⚠️ Requires Python backend
- **Setup**:
  ```bash
  cd assignments/assignment4
  pip install -r requirements.txt
  ```
- **Usage**: Run Python scripts as shown in the web interface
- **Output**: Generated panoramas will appear in `output/` folder

### Assignment 5-6: Real-Time Object Tracking
- **Status**: ✅ Ready to use
- **Requirements**: Modern web browser, webcam access
- **NPZ File Generation**: 
  ```bash
  cd assignments/assignment5-6
  python make_test_npz.py
  ```
  This creates a test NPZ file for SAM2 segmentation mode

### Assignment 7: Stereo Vision & Pose Tracking
- **Status**: ⚠️ Task 1 requires Flask backend, Task 3 works standalone
- **Backend Setup**:
  ```bash
  cd assignments/assignment7
  pip install -r requirements.txt
  python task1_backend.py
  ```
- **Backend URL**: http://localhost:5001
- **Task 3**: Works without backend (uses MediaPipe in browser)

## Generating NPZ Files (Assignment 5-6)

To generate test NPZ files for SAM2 segmentation:

1. Navigate to `assignments/assignment5-6/`
2. Run: `python make_test_npz.py`
3. This creates `test_sam2_segmentation.npz` with sample segmentation masks

You can modify `make_test_npz.py` to create custom segmentation masks for your use case.

## File Structure

```
.
├── index.html                          # Main hub
├── assignments/
│   ├── assignment1/
│   │   └── index.html                 # Dimension measurement
│   ├── assignment2/
│   │   └── index.html                 # Template matching
│   ├── assignment3/
│   │   ├── index.html
│   │   ├── app.js
│   │   ├── styles.css
│   │   └── build_wasm/                # OpenCV.js build
│   ├── assignment4/
│   │   ├── index.html
│   │   ├── task1_stitch.py
│   │   ├── task2_sift.py
│   │   └── requirements.txt
│   ├── assignment5-6/
│   │   ├── index.html
│   │   ├── app.js
│   │   ├── make_test_npz.py          # NPZ generator
│   │   └── ...
│   └── assignment7/
│       ├── index.html
│       ├── task1_backend.py
│       └── requirements.txt
└── README.md
```

## Troubleshooting

### OpenCV.js not loading
- Check browser console for errors
- Ensure internet connection (for CDN-loaded OpenCV.js)
- For Assignment 3, ensure `build_wasm/` folder is present

### Backend not connecting (Assignment 7)
- Ensure Flask backend is running: `python task1_backend.py`
- Check that port 5001 is not in use
- Verify CORS is enabled in backend

### Webcam not working
- Grant camera permissions in browser
- Check browser compatibility (Chrome/Edge recommended)
- Ensure no other application is using the camera

### NPZ file not loading
- Ensure file is in correct format
- Check browser console for parsing errors
- Verify JSZip library is loaded (Assignment 5-6)

## Browser Recommendations

- **Chrome/Edge**: Full support, recommended
- **Firefox**: Full support
- **Safari**: Most features work, some limitations with WebAssembly

## Notes

- All assignments are self-contained
- Original assignment folders are preserved for reference
- Some assignments may require additional data files (images, etc.) - place them in the respective assignment folders

