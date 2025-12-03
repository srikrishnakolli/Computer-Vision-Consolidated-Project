# Computer Vision Assignment 4

This project contains two main tasks:

1. **Task 1**: Panorama stitching utility using OpenCV's high-level Stitcher API
2. **Task 2**: SIFT feature extraction from scratch with RANSAC-based homography estimation

Both tasks can stitch overlapping photos and compare results with reference implementations.

## Project Structure

```
Assignment 4/
├── images/                    # Input images folder
│   ├── 00.JPG                # Image sequence (must be in order)
│   ├── 01.JPG
│   ├── 02.JPG
│   ├── 03.JPG
│   ├── 04.JPG
│   ├── 05.JPG
│   ├── 06.JPG
│   └── landscape/            # Additional landscape images
├── comparisons/              # Reference panoramas for comparison
│   └── IMG_1257.JPG
├── output/                   # Output folder for generated panoramas
│   ├── task1_panorama1.jpg  # Task 1 output
│   └── task2/               # Task 2 output directory
├── task1_stitch.py          # Task 1: Panorama stitching script
├── task2_sift.py            # Task 2: SIFT feature extraction script
└── requirements.txt          # Python dependencies
```

## Prerequisites

- **Python 3.9 or higher** (Python 3.10+ recommended)
- **pip** (Python package installer)

## Installation Steps

### Step 1: Verify Python Installation

Open your terminal/command prompt and check if Python is installed:

```bash
python --version
```

or

```bash
python3 --version
```

You should see Python 3.9 or higher. If not, download and install Python from [python.org](https://www.python.org/downloads/).

### Step 2: Navigate to Project Directory

Open your terminal/command prompt and navigate to the project folder:

**On Windows (PowerShell or Command Prompt):**
```bash
cd "C:\MS-CS25\Fall 25\Computer Vison\Assignment 4"
```

**On Mac/Linux:**
```bash
cd "/path/to/Assignment 4"
```

### Step 3: Create Virtual Environment (Recommended)

Creating a virtual environment isolates your project dependencies:

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the beginning of your command prompt, indicating the virtual environment is active.

### Step 4: Install Dependencies

Install all required packages:

```bash
pip install -r requirements.txt
```

This will install:
- `opencv-contrib-python` (OpenCV with contrib modules including Stitcher API)
- `numpy` (Numerical computing library)

**Note:** If you encounter any installation errors, try:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Verify Installation

Verify that OpenCV is installed correctly:

```bash
python -c "import cv2; print(cv2.__version__)"
```

You should see the OpenCV version number (e.g., 4.12.0.88).

## Usage Instructions

## Task 1: Panorama Stitching

### Basic Panorama Stitching

The simplest way to create a panorama from images in the `images/` folder:

```bash
python task1_stitch.py
```

This will:
- Load all `*.JPG` files from the `images/` folder (00.JPG, 01.JPG, 02.JPG, etc.)
- Stitch them together in sorted order
- Save the result to `output/task1_panorama1.jpg`

### Custom Image Directory

To use images from a different folder:

```bash
python task1_stitch.py --images ./images/landscape
```

### Custom Output Location

To specify a different output file:

```bash
python task1_stitch.py --output ./output/my_panorama.jpg
```

### With Reference Comparison

To compare your stitched panorama with a reference image:

```bash
python task1_stitch.py --reference ./comparisons/IMG_1257.JPG --comparison-output ./output/comparison.jpg
```

This creates a side-by-side comparison showing the reference panorama on the left and your stitched panorama on the right.

### Full Example with All Options

```bash
python task1_stitch.py ^
    --images ./images ^
    --pattern "*.JPG" ^
    --output ./output/task1_panorama1.jpg ^
    --resize-max-width 1800 ^
    --reference ./comparisons/IMG_1257.JPG ^
    --comparison-output ./output/task1_vs_mobi.jpg ^
    --exposure-compensation gain_blocks
```

**Note:** On Windows, use `^` for line continuation. On Mac/Linux, use `\`.

### Command-Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--images` | Directory containing input images | `./images` |
| `--pattern` | Glob pattern to match image files | `*.JPG` |
| `--output` | Output file path for panorama | `./output/task1_panorama1.jpg` |
| `--resize-max-width` | Maximum width for resizing (0 = no resize) | `1800` |
| `--reference` | Optional reference panorama for comparison | `None` |
| `--comparison-output` | Output path for side-by-side comparison | `./output/task1_vs_mobi.jpg` |
| `--exposure-compensation` | Exposure compensation strategy | `gain_blocks` |

**Exposure Compensation Options:**
- `none` - No exposure compensation
- `gain` - Gain compensation
- `gain_blocks` - Gain blocks compensation (default)
- `channel` - Channel compensation
- `channel_blocks` - Channel blocks compensation

---

## Task 2: SIFT Feature Extraction

Task 2 implements SIFT (Scale-Invariant Feature Transform) feature extraction from scratch and compares it with OpenCV's reference implementation. It takes two overlapping images, detects keypoints, computes descriptors, matches them, and estimates a homography using RANSAC.

### Basic Usage

The minimum required arguments are two images:

```bash
python task2_sift.py --image-a ./images/00.JPG --image-b ./images/01.JPG
```

This will:
- Load the two images
- Extract SIFT features using both custom and OpenCV implementations
- Match descriptors using Lowe's ratio test
- Estimate homography using RANSAC
- Save visualization outputs to `output/task2/`

### Example with Consecutive Images

To compare two consecutive images from your panorama sequence:

```bash
python task2_sift.py --image-a ./images/01.JPG --image-b ./images/02.JPG
```

### Custom Output Directory

To specify a different output directory:

```bash
python task2_sift.py --image-a ./images/00.JPG --image-b ./images/01.JPG --output-dir ./output/my_sift_results
```

### Advanced Options

Full example with all customizable parameters:

```bash
python task2_sift.py ^
    --image-a ./images/00.JPG ^
    --image-b ./images/01.JPG ^
    --resize-width 960 ^
    --octaves 4 ^
    --scales 3 ^
    --contrast-threshold 0.04 ^
    --edge-threshold 10.0 ^
    --sigma 1.6 ^
    --ratio-test 0.75 ^
    --ransac-iters 2000 ^
    --ransac-threshold 3.0 ^
    --output-dir ./output/task2
```

**Note:** On Windows, use `^` for line continuation. On Mac/Linux, use `\`.

### Task 2 Command-Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--image-a` | **Required.** First input image path | - |
| `--image-b` | **Required.** Second input image path | - |
| `--resize-width` | Optional width to resize both images (keeps aspect ratio) | `960` |
| `--octaves` | Number of octaves in the SIFT pyramid | `4` |
| `--scales` | Number of scales per octave | `3` |
| `--contrast-threshold` | Contrast threshold to discard weak extrema | `0.04` |
| `--edge-threshold` | R parameter to suppress edge responses | `10.0` |
| `--sigma` | Base blur applied before building pyramid | `1.6` |
| `--ratio-test` | Lowe's ratio test threshold for matching | `0.75` |
| `--ransac-iters` | RANSAC iterations for homography estimation | `2000` |
| `--ransac-threshold` | Inlier threshold (pixels) for RANSAC | `3.0` |
| `--output-dir` | Directory for diagnostic outputs | `./output/task2` |

### Task 2 Output Files

The script generates several visualization files in the output directory:
- Match visualizations comparing custom SIFT vs OpenCV SIFT
- Homography estimation results
- Keypoint detection comparisons

### Task 2 Tips

- **Image Selection:** Choose two images with good overlap (20-30% recommended)
- **Resize Width:** Use `--resize-width` to speed up processing for large images
- **Parameter Tuning:** Adjust thresholds if you're getting too few or too many matches
- **Consecutive Images:** For panorama sequences, use consecutive images (e.g., 00.JPG and 01.JPG)

---

## Image Requirements

### Image Naming Convention

For best results, name your images in sequential order:
- `00.JPG`, `01.JPG`, `02.JPG`, etc. (recommended)
- Or any names that sort alphabetically in the correct order

The script automatically sorts images alphabetically, so ensure your naming reflects the capture order.

### Image Quality Guidelines

1. **Overlap:** Images should have at least 20-30% overlap between consecutive frames
2. **Order:** Images must be captured in left-to-right (or right-to-left) sequence
3. **Stability:** Use a tripod or keep the camera steady for better results
4. **Consistent Height:** Keep the camera at the same height for all shots
5. **Format:** Supported formats: JPG, JPEG, PNG (use `--pattern` to change)

### Current Image Setup

Your project currently has:
- **Main images folder:** `images/` with 7 images (00.JPG through 06.JPG)
- **Landscape folder:** `images/landscape/` with additional images
- **Reference panorama:** `comparisons/IMG_1257.JPG`

## Troubleshooting

### Common Issues

**1. "No input files matched" error**
- **Solution:** Check that your images folder exists and contains files matching the pattern (default: `*.JPG`)
- Verify the file extensions match (case-sensitive: `.JPG` vs `.jpg`)

**2. "Stitching failed with status code X"**
- **Status Code 1:** Need more input images (minimum 2 required)
- **Status Code 2:** Not enough features detected (images may not overlap enough)
- **Status Code 3:** Homography estimation failed
- **Status Code 4:** Camera parameters adjustment failed
- **Solutions:**
  - Ensure images have sufficient overlap (20-30%)
  - Try reducing image size with `--resize-max-width`
  - Check that images are in the correct order
  - Ensure images are not too blurry or too similar

**3. "Failed to read image" error**
- **Solution:** Check that image files are not corrupted and are in a supported format

**4. ModuleNotFoundError: No module named 'cv2'**
- **Solution:** 
  ```bash
  pip install opencv-contrib-python
  ```
  Make sure you're using `opencv-contrib-python` (not just `opencv-python`) for the Stitcher API.

**5. Images not in correct order**
- **Solution:** Rename images to ensure alphabetical sorting matches capture order (e.g., 00.JPG, 01.JPG, 02.JPG)

**6. Task 2: "the following arguments are required: --image-a, --image-b"**
- **Solution:** Task 2 requires two image paths. Use:
  ```bash
  python task2_sift.py --image-a ./images/00.JPG --image-b ./images/01.JPG
  ```

**7. Task 2: Too few matches found**
- **Solution:** 
  - Ensure images have sufficient overlap (20-30%)
  - Try lowering `--contrast-threshold` (e.g., 0.02)
  - Try lowering `--edge-threshold` (e.g., 5.0)
  - Increase `--resize-width` if images are too small

**8. Task 2: Too many false matches**
- **Solution:**
  - Increase `--ratio-test` threshold (e.g., 0.8)
  - Increase `--contrast-threshold` (e.g., 0.06)
  - Increase `--edge-threshold` (e.g., 15.0)

### Performance Tips

- **Large Images:** Use `--resize-max-width 1800` (or lower) to speed up processing
- **Processing Time:** Larger images take more time; be patient
- **Memory:** Very large images may require significant RAM

## Example Workflows

### Task 1 Workflow

Here's a complete example workflow for Task 1:

1. **Prepare your images:**
   - Place overlapping images in the `images/` folder
   - Name them sequentially (00.JPG, 01.JPG, 02.JPG, etc.)

2. **Run the stitching:**
   ```bash
   python task1_stitch.py
   ```

3. **Check the output:**
   - Open `output/task1_panorama1.jpg` to view your panorama

4. **Compare with reference (optional):**
   ```bash
   python task1_stitch.py --reference ./comparisons/IMG_1257.JPG
   ```

5. **View comparison:**
   - Open `output/task1_vs_mobi.jpg` to see the side-by-side comparison

### Task 2 Workflow

Here's a complete example workflow for Task 2:

1. **Select two overlapping images:**
   - Choose two consecutive images from your sequence (e.g., 00.JPG and 01.JPG)

2. **Run SIFT feature extraction:**
   ```bash
   python task2_sift.py --image-a ./images/00.JPG --image-b ./images/01.JPG
   ```

3. **Check the output:**
   - Navigate to `output/task2/` to view the generated visualizations
   - Compare custom SIFT vs OpenCV SIFT results

4. **Try different image pairs:**
   ```bash
   python task2_sift.py --image-a ./images/02.JPG --image-b ./images/03.JPG
   ```

## Output Files

### Task 1 Outputs
- **Panorama:** `output/task1_panorama1.jpg` - Your stitched panorama
- **Comparison:** `output/task1_vs_mobi.jpg` - Side-by-side comparison (if reference provided)

### Task 2 Outputs
- **Diagnostic Files:** `output/task2/` - Contains match visualizations and comparison results

## Additional Notes

- The script automatically creates the `output/` directory if it doesn't exist
- Images are processed in alphabetical order, so naming is important
- The default resize width (1800px) balances quality and processing speed
- The stitcher uses automatic feature detection and matching

## Getting Help

If you encounter issues:
1. Check that all dependencies are installed correctly
2. Verify your images meet the requirements (overlap, order, quality)
3. Try reducing image size with `--resize-max-width`
4. Check the error messages for specific status codes

## License

This project is for educational purposes as part of a Computer Vision course assignment.

