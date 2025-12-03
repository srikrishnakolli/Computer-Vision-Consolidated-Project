# Real-Time Object Tracker

A web-based real-time object tracking application that implements multiple computer vision tracking techniques using OpenCV.js. This project demonstrates three distinct tracking modes: marker-based tracking, marker-less tracking, and SAM2 segmentation-based tracking.

##  Project Overview

This application provides a browser-based interface for real-time object tracking using your webcam. It leverages OpenCV.js for computer vision processing and supports multiple tracking methodologies suitable for different use cases.

### Key Features

- **Three Tracking Modes:**
  1. **Marker-Based Tracking**: Detects and tracks ArUco markers and QR codes
  2. **Marker-Less Tracking**: Track any object by selecting a region of interest
  3. **SAM2 Segmentation**: Load pre-computed segmentation masks from NPZ files

- **Real-Time Processing**: Live video feed processing with low latency
- **Visual Feedback**: Color-coded overlays, bounding boxes, and centroids
- **User-Friendly Interface**: Modern, responsive design with intuitive controls
- **Cross-Platform**: Runs in any modern web browser

##  Requirements and Dependencies

### Required Dependencies

#### 1. **Web Browser**
- Chrome, Firefox, Safari, or Edge (latest versions recommended)
- WebRTC support for camera access
- JavaScript enabled

#### 2. **CDN Libraries (Automatically Loaded)**
The following libraries are loaded via CDN in the HTML file:
- **OpenCV.js v4.8.0**: Computer vision library
  - URL: `https://docs.opencv.org/4.8.0/opencv.js`
- **JSZip v3.10.1**: NPZ file parsing
  - URL: `https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js`

#### 3. **Python (Optional - For Creating Test NPZ Files)**
- Python 3.6 or higher
- NumPy library: `pip install numpy`

### No Installation Required!

This project runs entirely in the browser. Simply open `index.html` in a web browser to get started.

##  Getting Started

### Quick Start Guide

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd "Assignment 5-6"
   ```

2. **Open the application**
   - Simply open `index.html` in your web browser
   - Or use a local web server (recommended for testing):
     ```bash
     # Using Python 3
     python -m http.server 8000
     
     # Then open: http://localhost:8000
     ```

3. **Allow camera access**
   - When prompted, grant the browser permission to access your webcam

4. **Start tracking!**
   - Click "Start Camera" to begin
   - Select a tracking mode from the dropdown
   - Follow mode-specific instructions below

##  How to Use

### Mode 1: Marker-Based Tracking (ArUco/QR)

**Best for**: Tracking printed markers with high accuracy

1. Select "Marker-Based (ArUco/QR)" from the dropdown
2. Click "Start Camera"
3. Show an ArUco marker or QR code to the camera
4. The system will automatically detect and track the marker with:
   - **Green overlay**: Detected marker region
   - **Green border**: Bounding box
   - **Yellow corners**: Corner points
   - **Magenta center**: Centroid with crosshair

**Tips:**
- Print a QR code or use a digital marker on another screen
- Ensure good lighting for better detection
- Keep the marker flat and clearly visible

### Mode 2: Marker-Less Tracking

**Best for**: Tracking any object without special markers

1. Select "Marker-Less" from the dropdown
2. Click "Start Camera"
3. Click "Select Region" button
4. Click and drag on the video to select the object you want to track
5. Release to confirm selection
6. The system will track the selected region using template matching

**Visual Indicators:**
- **Yellow dashed box**: Selection in progress
- **Green overlay**: Tracked object
- **Lime green corners**: Tracking points
- **Green crosshair**: Object center

**Tips:**
- Choose objects with distinct features
- Avoid highly textured backgrounds
- Select a reasonably sized region (not too small)

### Mode 3: SAM2 Segmentation

**Best for**: Using pre-computed segmentation masks

1. Select "SAM2 Segmentation" from the dropdown
2. Click "Start Camera"
3. Click "Choose File" and select an NPZ file containing segmentation masks
4. Click "Load Segmentation"
5. The system will display the segmented objects with:
   - **Magenta overlay**: Segmentation masks
   - **Magenta borders**: Object boundaries
   - **Magenta markers**: Centroids

**Creating Test NPZ Files:**

Use the included Python script to generate test segmentation data:

```bash
python make_test_npz.py
```

This creates `test_sam2_segmentation.npz` with two dummy masks for testing.

**NPZ File Format:**
Your NPZ file should contain:
- `masks`: NumPy array of shape (N, H, W) where N is number of objects
- `centroids`: (Optional) Array of shape (N, 2) with (x, y) coordinates

## 📁 Project Structure

```
Assignment 5-6/
│
├── index.html                          # Main HTML page
├── styles.css                          # Styling and layout
├── app.js                             # Main application logic
├── tracker.js                         # Object tracking implementations
├── npz_parser.js                      # NPZ file parser for SAM2 mode
├── sam2_helper.js                     # SAM2 helper utilities
├── make_test_npz.py                   # Python script to create test NPZ files
├── test_sam2_segmentation.npz         # Sample NPZ file for testing
└── README.md                          # This file
```

### File Descriptions

#### Core Files

- **`index.html`**: Main webpage with video feed, controls, and UI elements
- **`styles.css`**: Modern, responsive styling with gradient backgrounds and smooth transitions
- **`app.js`**: 
  - Handles camera initialization and video stream
  - UI event handling (buttons, mode selection)
  - Video frame processing loop
  - Region selection for marker-less tracking

#### Tracking Implementation

- **`tracker.js`**: 
  - `ObjectTracker` class with three tracking modes
  - ArUco and QR code detection
  - Template matching for marker-less tracking
  - SAM2 mask rendering and tracking
  - Visual overlay generation

#### Data Processing

- **`npz_parser.js`**:
  - `NPZParser` class for reading NumPy NPZ files
  - Parses .npy format (NumPy array files)
  - Converts NumPy arrays to OpenCV Mat format
  - Handles different data types and shapes

#### Utilities

- **`sam2_helper.js`**: Helper functions for SAM2 integration
- **`make_test_npz.py`**: Python script to generate test segmentation data

## 🛠️ Technical Details

### Technologies Used

1. **OpenCV.js**: 
   - ArUco marker detection
   - QR code detection
   - Template matching (cv.matchTemplate)
   - Contour detection
   - Image processing operations

2. **WebRTC**: 
   - Access camera via `getUserMedia()`
   - Real-time video streaming

3. **Canvas API**: 
   - Video rendering
   - Overlay drawing
   - User interaction (mouse events)

4. **JSZip**: 
   - Parse NPZ (zipped NumPy) files
   - Extract and decompress .npy arrays

### Tracking Algorithms

#### Marker-Based Tracking
- **Primary**: ArUco marker detection using OpenCV's ArUco module
- **Secondary**: QR code detection using QRCodeDetector
- **Fallback**: Contour-based marker detection for square objects

#### Marker-Less Tracking
- **Algorithm**: Template matching with normalized cross-correlation
- **Threshold**: 0.6 confidence for detection
- **Method**: `cv.TM_CCOEFF_NORMED`

#### SAM2 Segmentation
- **Input**: Pre-computed segmentation masks from SAM2 model
- **Processing**: Binary mask overlay with bounding box extraction
- **Visualization**: Mask overlay with transparency blending

### Performance Considerations

- Canvas uses `willReadFrequently` attribute for optimized getImageData
- Efficient memory management with OpenCV Mat cleanup
- RequestAnimationFrame for smooth video processing
- Real-time processing at camera framerate

##  Visual Indicators

The application uses color-coded overlays for different tracking modes:

| Mode | Color | Elements |
|------|-------|----------|
| **Marker-Based** | Green | Border, corners, center |
| **Marker-Less** | Green/Lime | Border, corners, center, overlay |
| **SAM2** | Magenta | Mask overlay, border, center |
| **Selection** | Yellow | Dashed selection box |

All modes display:
- Thick colored borders (3px)
- Corner markers (circles)
- Center point with crosshair
- Semi-transparent mask overlay (30% opacity)

##  Troubleshooting

### Camera Not Working
- **Issue**: "Could not access camera" error
- **Solution**: 
  - Check browser permissions
  - Ensure you're using HTTPS or localhost
  - Try a different browser

### ArUco/QR Detection Failing
- **Issue**: Markers not detected
- **Solution**:
  - Use contour-based fallback (automatic)
  - Improve lighting conditions
  - Use high-contrast markers

### Template Tracking Lost
- **Issue**: Object not tracked consistently
- **Solution**:
  - Reselect the region
  - Choose an object with more distinctive features
  - Avoid rapid movements

### NPZ File Won't Load
- **Issue**: "Error loading SAM2 file"
- **Solution**:
  - Verify NPZ file format (must contain 'masks' array)
  - Check array dimensions match video resolution
  - Try the included `test_sam2_segmentation.npz`

## For Developers

### Extending the Project

1. **Add New Tracking Algorithms**:
   - Modify `tracker.js` to add new tracking methods
   - Implement new case in `processFrame()` switch statement

2. **Custom Marker Detection**:
   - Extend `trackMarker()` or `trackMarkerContours()` methods
   - Add custom marker patterns

3. **SAM2 Integration**:
   - Connect to SAM2 model for real-time segmentation
   - Implement frame-to-frame mask propagation

### Testing

1. **Test Marker Detection**:
   - Generate ArUco markers: https://chev.me/arucogen/
   - Print QR codes from any QR generator

2. **Test NPZ Files**:
   ```bash
   python make_test_npz.py
   ```
   Then load `test_sam2_segmentation.npz` in SAM2 mode

##  Academic Context

This project demonstrates practical applications of computer vision concepts including:
- **Image Processing**: Frame capture, conversion, filtering
- **Feature Detection**: Marker detection, contour finding
- **Template Matching**: Cross-correlation for object tracking
- **Segmentation**: Binary mask processing and visualization
- **Real-Time Processing**: Video stream handling and optimization

### Learning Outcomes

Students working with this project will understand:
1. How marker-based tracking works (ArUco/QR codes)
2. Template matching algorithms for marker-less tracking
3. Segmentation mask processing and visualization
4. Browser-based computer vision with OpenCV.js
5. Real-time video processing techniques

##  Acknowledgments

- OpenCV.js for providing computer vision in the browser
- JSZip for NPZ file parsing
- SAM2 (Segment Anything 2) for segmentation inspiration

## 📄 License

This project is created for educational purposes as part of Computer Vision coursework.



---

**Course**: Computer Vision  
**Semester**: Fall 2025  
**Assignment**: Assignment 5-6  
**Platform**: Web-based (HTML5 + JavaScript + OpenCV.js)

