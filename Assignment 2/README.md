# Computer Vision Assignment 2

This repository contains implementations for three computer vision tasks:
1. **Template Matching** using normalized cross-correlation
2. **Fourier Transform Deconvolution** for image deblurring
3. **Web Application** for template matching with region blurring

---

## QUESTION 1: Template Matching

### Methodology
Template matching uses normalized cross-correlation to find the location of a template image within a larger scene image.

**Correlation Method:**
- Uses `cv2.matchTemplate()` with `cv2.TM_CCOEFF_NORMED`
- Normalized correlation coefficient ranges from 0 to 1
- Higher values indicate better matches
- Locates the template by finding maximum correlation value

### Implementation Steps
1. Load template image from templates folder
2. Load scene image to search for the object
3. Convert both images to grayscale
4. Apply template matching using correlation
5. Find location with maximum correlation coefficient
6. Draw bounding box around detected object
7. Save output image with detection visualization

### Actual Object

<img width="1233" height="920" alt="image" src="https://github.com/user-attachments/assets/77e918b1-40e6-463e-9624-c1657c5fdd88" />

### Template Images
The following 10 objects were used as templates:
1. Object 1: <img width="608" height="221" alt="Bot" src="https://github.com/user-attachments/assets/ad94d710-0b30-4136-8d63-2fbcaf4c0a50" />
2. Object 2: <img width="182" height="304" alt="Car" src="https://github.com/user-attachments/assets/44f24e26-6d7b-4b0d-8c0d-8fe6188b70ee" />
3. Object 3: <img width="540" height="298" alt="Ketch" src="https://github.com/user-attachments/assets/840ca005-3968-4ec9-9f98-b6700eee57f7" />
4. Object 4: <img width="218" height="199" alt="Wat" src="https://github.com/user-attachments/assets/048ae299-d0bd-4929-94e8-cb722bbc874f" />

### Detection Results
<img width="1197" height="925" alt="image" src="https://github.com/user-attachments/assets/10753879-61bd-4759-bf8f-6d96a19a2082" />

### How to Run Question 1

**Prerequisites:**
```bash
pip install opencv-python numpy matplotlib
```

**Run the script:**
```bash
cd "Question 1"
python Corelation.py
```

**Expected Output:**
- The script will process `realObj.JPG` as the scene image
- It will search for all templates in the `Templates/` folder
- Results will be saved as `multi_match_result.png`
- A window will display the detection results with bounding boxes

**Configuration:**
You can modify the following parameters in `Corelation.py`:
- `SCENE_PATH`: Path to the scene image (default: `"realObj.JPG"`)
- `TEMPLATE_GLOB`: Glob pattern for templates (default: `"templates/*.JPG"`)
- `SCORE_THRESH`: Minimum correlation score to draw bounding box (default: `0.60`)
- `SCALES`: Scale range for template matching (default: `np.linspace(0.5, 1.4, 19)`)
- `ANGLES`: Rotation angles to try (default: `[0, 180]`)

---

## QUESTION 2: Fourier Transform Deconvolution

### Theory
Gaussian blur in spatial domain is equivalent to multiplication in frequency domain.

**Mathematical Representation:**
- Spatial Domain: L_b(x,y) = L(x,y) * G(x,y)
- Frequency Domain: F{L_b} = F{L} × F{G}
- Deconvolution: F{L} = F{L_b} / F{G}

Where:
- L: Original image
- L_b: Blurred image
- G: Gaussian kernel
- *: Convolution operation
- F{}: Fourier transform

### Implementation Process
1. Capture original image L
2. Apply Gaussian blur to create L_b
3. Compute Fourier transform of L_b
4. Apply deconvolution in frequency domain
5. Compute inverse Fourier transform to retrieve L

### Results

#### Original Image (L)
<img width="689" height="907" alt="image" src="https://github.com/user-attachments/assets/6b8eaf26-8de2-415a-ab4e-7d7e998495e1" />

#### Blurred Image (L_b)
<img width="661" height="886" alt="image" src="https://github.com/user-attachments/assets/d969d90c-f63d-4bfa-9675-4b8c02b03e15" />

#### Retrieved Image (L reconstructed)
<img width="656" height="885" alt="image" src="https://github.com/user-attachments/assets/c8113a54-8909-44a4-8b31-1e388a979281" />

### How to Run Question 2

**Prerequisites:**
```bash
pip install opencv-python numpy matplotlib
```

**Run the script:**
```bash
cd "Question 2"
python fourier_deblur.py
```

**Expected Output:**
- The script will load `L.JPG` (or `L.png`, `L.jpg`, etc.) from the current directory
- It will apply Gaussian blur to create the blurred version
- It will perform Fourier domain deconvolution using Wiener filtering
- Results will be saved as:
  - `Lb_blur.png`: The blurred image
  - `L_recovered.png`: The deblurred/recovered image
- A matplotlib window will display all three images side by side

**Configuration:**
You can modify the following parameters in `fourier_deblur.py`:
- `PREFERRED_NAME`: Input image filename (default: `"L_input.jpg"`)
- `SIGMA`: Gaussian blur strength (default: `2.0`)
- `KERNEL_SIZE`: Blur kernel size, should be odd (default: `13`)
- `MODE`: Deconvolution method - `"wiener"` or `"inverse"` (default: `"wiener"`)
- `K_WIENER`: Wiener filter noise-to-signal ratio (default: `0.0045`)

**Note:** The script automatically searches for image files named `L.*` in the current directory if the preferred name is not found.

---

## QUESTION 3: Web Application Implementation

### Overview
A web application that combines template matching with region blurring functionality. Two implementations are provided:
1. **Streamlit Application** (`WebApp.py`) - Python-based web app
2. **HTML/JavaScript Application** (`index.html`) - Browser-based app using OpenCV.js

### Output
<img width="1569" height="904" alt="image" src="https://github.com/user-attachments/assets/2757e01b-8926-4db9-897d-c02400492545" />

### How to Run Question 3

#### Option 1: Streamlit Application

**Prerequisites:**
```bash
pip install streamlit opencv-python numpy pillow
```

**Run the Streamlit app:**
```bash
cd "Question 3"
streamlit run WebApp.py
```

The application will open in your default web browser at `http://localhost:8501`

**Features:**
- Upload a scene image
- Automatically loads templates from `./templates/` folder
- Adjustable detection parameters (method, scales, angles, threshold)
- Non-maximum suppression (NMS) to remove duplicate detections
- Region blurring with configurable kernel size and sigma
- Download annotated and blurred results

**Usage:**
1. Upload a scene image using the file uploader
2. Adjust detection settings in the right panel
3. Click "🚀 Run detection & blur"
4. View results in three panels: original, detections, and blurred
5. Download the results using the download buttons

#### Option 2: HTML/JavaScript Application

**Prerequisites:**
- A modern web browser (Chrome, Firefox, Edge, Safari)
- No server required - runs entirely in the browser

**Run the HTML app:**
1. Open `index.html` in a web browser
2. Or serve it using a local web server:
   ```bash
   cd "Question 3"
   # Using Python 3
   python -m http.server 8000
   # Then open http://localhost:8000 in your browser
   ```

**Features:**
- Drag-and-drop interface for scene and template images
- Real-time template matching using OpenCV.js
- Configurable detection parameters
- Automatic blurring of detected regions
- Download results as PNG files

**Usage:**
1. Click "Scene" to upload or drag-and-drop a scene image
2. Click "Templates ×10" to upload multiple template images
3. Adjust parameters (method, threshold, scales, angles, blur settings)
4. Click "🚀 Run detection & blur"
5. View results and download using the download buttons

**Note:** The HTML version requires an internet connection to load OpenCV.js from the CDN.

---

## Project Structure

```
Assignment 2/
├── Question 1/
│   ├── Corelation.py          # Main template matching script
│   ├── realObj.JPG            # Scene image
│   ├── Templates/             # Template images folder
│   │   ├── Bot.JPG
│   │   ├── Car.JPG
│   │   ├── Ketch.JPG
│   │   ├── Wat.JPG
│   │   └── extra/             # Additional templates
│   └── multi_match_result.png # Output detection results
│
├── Question 2/
│   ├── fourier_deblur.py      # Fourier deconvolution script
│   ├── L.JPG                  # Input image
│   ├── Lb_blur.png           # Blurred output
│   ├── L_recovered.png       # Deblurred output
│   └── out_L/                # Additional output folder
│
└── Question 3/
    ├── WebApp.py             # Streamlit application
    ├── index.html            # HTML/JavaScript application
    └── templates/            # Template images folder (for web app)
```

---

## Commands to Run This Project

### Quick Start - All Questions

**Question 1 - Template Matching:**
```bash
cd "Question 1"
python Corelation.py
```

**Question 2 - Fourier Deconvolution:**
```bash
cd "Question 2"
python fourier_deblur.py
```

**Question 3 - Web Application (Streamlit):**
```bash
cd "Question 3"
streamlit run WebApp.py
```

**Question 3 - Web Application (HTML):**
```bash
cd "Question 3"
# Open index.html in a web browser, or:
python -m http.server 8000
# Then navigate to http://localhost:8000
```

### Installation

**Install all required dependencies:**
```bash
pip install opencv-python numpy matplotlib streamlit pillow
```

**For Question 3 HTML version:**
- No installation needed, just open `index.html` in a browser
- Requires internet connection for OpenCV.js CDN

---

## Technical Details

### Question 1: Template Matching
- **Method**: Normalized Cross-Correlation (`TM_CCOEFF_NORMED`)
- **Multi-scale**: Tests scales from 0.5x to 1.4x
- **Multi-angle**: Tests 0° and 180° rotations
- **Preprocessing**: Gaussian blur (3x3) for noise reduction
- **Output**: Annotated image with bounding boxes and confidence scores

### Question 2: Fourier Deconvolution
- **Blur Method**: Gaussian blur with configurable sigma
- **Deconvolution**: Wiener filter (default) or Inverse filter
- **Frequency Domain**: Uses FFT for efficient computation
- **PSF to OTF**: Converts point spread function to optical transfer function
- **Output**: Original, blurred, and recovered images

### Question 3: Web Application
- **Backend**: Streamlit (Python) or OpenCV.js (JavaScript)
- **Template Matching**: Same algorithm as Question 1
- **Blurring**: Gaussian blur applied only to detected regions
- **NMS**: Non-maximum suppression to remove duplicate detections
- **Interactive**: Real-time parameter adjustment and visualization

---

## Notes

- Ensure all image paths are correct before running scripts
- Template images should be placed in the `Templates/` or `templates/` folder
- For Question 2, the input image should be named `L.*` (JPG, PNG, etc.)
- Question 3 Streamlit app requires templates to be in `./templates/` relative to the script
- Adjust threshold values if detections are too sensitive or not sensitive enough
- For better deblurring results in Question 2, tune `K_WIENER` parameter (lower = sharper but more noise, higher = smoother but less detail)

---

## References

- OpenCV Documentation: https://docs.opencv.org/
- Streamlit Documentation: https://docs.streamlit.io/
- OpenCV.js: https://docs.opencv.org/4.x/d5/d10/tutorial_js_root.html

