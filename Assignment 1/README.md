# Camera Calibration and Real-World Dimension Measurement

## Project Overview

This project implements camera calibration using a checkerboard pattern from **calibdb.net** and develops a measurement system to calculate real-world dimensions of objects using perspective projection equations. The system converts pixel coordinates to physical measurements through the pinhole camera model.

---

<img width="2716" height="1876" alt="image" src="https://github.com/user-attachments/assets/d6053b54-dfab-48e5-9cee-41d41613e128" />

---

## Objectives

1. Calibrate a camera using checkerboard pattern from calibdb.net
2. Extract camera intrinsic parameters (fx, fy, cx, cy) and distortion coefficients (k1, k2, k3, p1, p2)
3. Implement pixel coordinate retrieval through mouse clicks
4. Calculate real-world dimensions of objects using perspective projection
5. Validate measurements with known object dimensions

---

## Prerequisites

- Python 3.x
- OpenCV library
- NumPy library
- Camera (webcam or external)
- Printer or computer screen for displaying calibration board
- Calibration board from calibdb.net

### Installation

Install the required Python packages:

```bash
pip install opencv-python numpy
```

Or if you prefer using conda:

```bash
conda install opencv numpy
```

---

## Project Structure

```
Assignment 1/
│
├── Calibration Pictures/          # Folder containing calibration board images
│   ├── IMG_0816.jpg
│   ├── IMG_0817.jpg
│   ├── ... (more calibration images)
│   └── board.png
│
├── Question 1/
│   └── Assign.py                  # Main script for dimension measurement
│
├── Question2/
│   └── index2.html               # Web-based measurement tool
│
├── backup/
│   ├── cv.py                      # Camera calibration script
│   ├── click.py                   # Pixel coordinate retrieval script
│   ├── Assignment1.py            # Alternative dimension measurement script
│   ├── calibration_best.npz      # Saved calibration parameters (NumPy format)
│   ├── calibration.txt           # Saved calibration parameters (text format)
│   └── ObjectImage.JPG           # Sample object image for testing
│
└── README.md                      # This file
```

---

## Project Steps

### Step 1: Prepare Calibration Board

1. Visit [calibdb.net](https://calibdb.net) and download/print the calibration board
2. Alternatively, display the board directly on a computer screen
3. Ensure the board is flat and clearly visible

**Note:** The calibration board should have a known pattern (e.g., 9x6 squares = 8x5 inner corners). The default script uses an 8x5 inner corner pattern.

### Step 2: Capture Calibration Images

1. Take at least 10 images of the calibration board using your camera
2. Maintain the same camera orientation throughout
3. Vary the distance and angles between the camera and board
4. Ensure the entire board is visible in each image
5. Use different perspectives for better calibration accuracy

**Save all calibration images in the `Calibration Pictures/` folder.**

### Step 3: Camera Calibration

Run the camera calibration script to extract intrinsic parameters:

```bash
python backup/cv.py
```

**Script Configuration:**
- The script automatically looks for images in the `Calibration Pictures/` folder
- Default pattern: 8x5 inner corners (for a 9x6 checkerboard)
- Square size: 0.025 meters (25mm) - adjust this in the script if your board has different dimensions
- Output files:
  - `calibration_best.npz` - NumPy format with all calibration data
  - `undistorted_best.jpg` - Sample undistorted image for verification
  - Console output with camera matrix and distortion coefficients

**To modify calibration settings, edit these variables in `backup/cv.py`:**
```python
INNER_COLS, INNER_ROWS = 8, 5    # Adjust based on your checkerboard
SQUARE_SIZE  = 0.025              # Size of each square in meters
SHOW         = False              # Set to True to visualize corner detection
```

**Expected Output:**
```
[INFO] Found X image(s) in ...
[INFO] Image size: (width, height)
[RESULT] RMS (OpenCV): X.XXXXXX
[RESULT] Mean reprojection error: X.XXXXXX px
[RESULT] Camera matrix K:
[[fx   0  cx]
 [ 0  fy  cy]
 [ 0   0   1]]
[RESULT] Distortion coeffs [k1 k2 p1 p2 k3]:
[...]
[SAVED] calibration_best.npz
[SAVED] undistorted_best.jpg
```

### Step 4: Save Calibration Parameters

After calibration, the parameters are automatically saved. You can also manually note them down in a text file:

**From console output, record:**
- **Camera Matrix Parameters:**
  - fx (focal length x)
  - fy (focal length y)
  - cx (optical center x)
  - cy (optical center y)
- **Distortion Coefficients:**
  - k1, k2, k3 (radial distortion)
  - p1, p2 (tangential distortion)

**Example calibration parameters (from `backup/calibration.txt`):**
```
fx: 4124.85217000
fy: 4126.41606000
cx: 2774.74600000
cy: 2302.01489000
k1: -0.00898340
k2: -0.56108969
p1:  0.01006218
p2:  0.00449114
k3:  1.13245558
```

### Step 5: Pixel Coordinate Retrieval

To interactively select points on an image and retrieve their pixel coordinates:

```bash
python backup/click.py
```

**Usage:**
- The script loads all images from the `Calibration Pictures/` folder
- Left-click on the image to add points (green circles)
- Press `'u'` to undo the last point
- Press `'s'` to save points to a CSV file
- Press `'n'` to move to the next image
- Press `Esc` to quit

**Output:** CSV files with pixel coordinates (e.g., `IMG_0816_points.csv`)

**To use with a different folder, edit the `FOLDER` variable in `backup/click.py`:**
```python
FOLDER = r"Calibration Pictures"  # Change to your image folder path
```

### Step 6: Real-World Dimension Measurement

**Task:** Calculate the real-world dimensions of an object using perspective projection equations.

#### Method 1: Using Python Script (Recommended)

**Option A: Using the main script (`Question 1/Assign.py`):**

```bash
python "Question 1/Assign.py"
```

**Option B: Using the backup script (`backup/Assignment1.py`):**

```bash
python backup/Assignment1.py
```

**Before running, update the script with:**
1. **Image path:** Set the `image_path` variable to your object image
   ```python
   image_path = r"ObjectImage.JPG"  # or path to your image
   ```
2. **Camera parameters:** Update the intrinsic parameters (fx, fy, cx, cy)
   ```python
   FX = 4124.85217000  # Your fx value
   FY = 4126.41606000  # Your fy value
   cx = 2774.74600000  # Your cx value
   cy = 2302.01489000  # Your cy value
   ```
3. **Distance to object:** Set the measured distance (Z) in millimeters
   ```python
   Z = 300  # Distance from camera to object plane in mm (e.g., 30cm = 300mm)
   ```

**Usage:**
1. Run the script
2. A window will open showing your image
3. Draw a rectangle (ROI) around the object you want to measure
4. Press `ENTER` or `SPACE` to confirm, or `'c'` to cancel
5. The script will calculate and display:
   - Real-world width (mm and inches)
   - Real-world height (mm and inches)
6. An annotated image will be saved as `annotated_image.png`

**Output Example:**
```
Loaded image: 4284 x 5712px
Selected ROI (original image coords): x=1000, y=1500, w=500, h=400
Calculated Real-World Width : 36.45 mm (1.43 in)
Calculated Real-World Height: 29.16 mm (1.15 in)
Annotated image saved to: annotated_image.png
```

#### Method 2: Using Web-Based Tool

Open the HTML file in a web browser:

```bash
# On Windows
start "Question2/index2.html"

# On macOS
open "Question2/index2.html"

# On Linux
xdg-open "Question2/index2.html"
```

Or simply double-click `Question2/index2.html` in your file explorer.

**Usage:**
1. Load an image using the file input or capture from webcam
2. Enter your camera parameters (fx, fy, cx, cy) and object distance (Z)
3. Select measurement mode:
   - **Rectangle mode (R):** Click and drag to select a rectangular region
   - **Line mode (L):** Click two points to measure a straight-line distance
4. View results in the output panel
5. Save the annotated image using the "Save annotated image" button

**Features:**
- Interactive point/region selection
- Real-time dimension calculation
- Settings persistence (saved in browser)
- Support for loading calibration parameters from JSON file
- Webcam support for live measurement

---

## Implementation Details

### Perspective Projection Equations

The real-world dimensions are calculated using the pinhole camera model:

```
X = (u - cx) * Z / fx
Y = (v - cy) * Z / fy
```

Where:
- `(u, v)` = pixel coordinates
- `(X, Y)` = real-world coordinates (mm)
- `Z` = distance from camera to object plane (mm)
- `fx, fy` = focal lengths in pixels
- `cx, cy` = principal point coordinates

### For a Ball: Calculate Diameter
- Select a circular ROI or two points across the diameter
- The calculated width gives the diameter

### For a Cube: Calculate Side Length
- Select a square ROI on one face
- The calculated width/height gives the side length

---

## Troubleshooting

### Calibration Issues

**Problem:** "No corners found in [image]"
- **Solution:** Ensure the entire checkerboard is visible, well-lit, and in focus
- Try adjusting the pattern size (INNER_COLS, INNER_ROWS) if your board is different

**Problem:** "Only X usable image(s). Need at least 10."
- **Solution:** Capture more calibration images with different angles and distances

**Problem:** High reprojection error (> 2.0 pixels)
- **Solution:** Use more calibration images, ensure board is flat, check for motion blur

### Measurement Issues

**Problem:** "Error: Failed to read the image"
- **Solution:** Check that the image path is correct and the file exists

**Problem:** Measurements seem incorrect
- **Solution:** 
  - Verify the distance (Z) is accurately measured
  - Ensure the object plane is approximately fronto-parallel (perpendicular to camera)
  - Check that camera parameters are correctly entered
  - Verify the image is undistorted (or apply undistortion first)

**Problem:** ROI selection window is too large
- **Solution:** The script automatically scales to fit your screen. If issues persist, resize the window manually.

---

## Results Images

<table>
  <tr>
    <td> <img width="1037" height="751" alt="image" src="https://github.com/user-attachments/assets/96be2d3e-f3bd-4515-873a-28cdbbbddfa5" />
 </td>
    <td> <img width="875" height="532" alt="image" src="https://github.com/user-attachments/assets/a09cac9c-6c74-4816-931b-38395a4ab3a8" />
 </td>
  </tr>
</table>

---

## Quick Reference Commands

```bash
# Install dependencies
pip install opencv-python numpy

# Run camera calibration
python backup/cv.py

# Get pixel coordinates from images
python backup/click.py

# Measure object dimensions (Method 1)
python "Question 1/Assign.py"

# Measure object dimensions (Method 2 - Alternative)
python backup/Assignment1.py

# Open web-based measurement tool
# (Double-click Question2/index2.html or use browser)
```

---

## Additional Notes

- **Image Formats:** Supported formats include JPG, JPEG, PNG, BMP, TIFF
- **Distance Measurement:** Use a ruler or measuring tape to accurately measure the distance from camera to object
- **Accuracy:** Measurement accuracy depends on:
  - Calibration quality (more images = better calibration)
  - Accurate distance measurement (Z)
  - Object plane being approximately fronto-parallel
  - Image resolution and focus
- **Undistortion:** For best results, undistort images before measurement if distortion coefficients are significant

---

## License

This project is for educational purposes as part of Computer Vision coursework.

---

## References

- [calibdb.net](https://calibdb.net) - Checkerboard pattern generator
- OpenCV Camera Calibration Documentation
- Pinhole Camera Model - Computer Vision: Algorithms and Applications (Szeliski)
