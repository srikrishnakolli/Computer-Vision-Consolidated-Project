import math
import cv2
import numpy as np
import os

# -------- Utility: convert mm -> inches --------
def convert_milli_to_inch(x_mm: float) -> float:
    return x_mm / 25.4

# -------- Utility: get screen size (Windows-safe) --------
def get_screen_size():
    # Fallback defaults if OS query fails
    w, h = 1920, 1080
    try:
        import ctypes
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()  # handle high-DPI scaling
        w, h = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    except Exception:
        pass
    return w, h

def calculate_dimensions_from_image():
    # --- YOUR IMAGE PATH ---
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the project root
    project_root = os.path.dirname(script_dir)
    # Try backup folder first, then root folder
    image_path = os.path.join(project_root, "backup", "ObjectImage.JPG")
    if not os.path.exists(image_path):
        image_path = os.path.join(project_root, "ObjectImage.JPG")
    if not os.path.exists(image_path):
        image_path = r"ObjectImage.JPG"  # fallback to current directory

    # Read image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Failed to read the image from {image_path}. Make sure the file exists.")
        return

    H, W = image.shape[:2]
    print(f"Loaded image: {W} x {H}px")

    # --- Make a display copy that FITS the screen for ROI selection ---
    screen_w, screen_h = get_screen_size()
    # Leave some margin (e.g., 90% of screen)
    max_w = int(screen_w * 0.9)
    max_h = int(screen_h * 0.9)

    # Compute uniform scale to fit within max_w x max_h
    scale = min(max_w / W, max_h / H, 1.0)  # never upscale
    disp_w, disp_h = int(W * scale), int(H * scale)

    display_img = image if scale == 1.0 else cv2.resize(image, (disp_w, disp_h), interpolation=cv2.INTER_AREA)

    # --- Resizable window + ROI selection on the *display* image ---
    cv2.namedWindow("Select ROI", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Select ROI", disp_w, disp_h)

    print("Image ready. Draw ROI on the image (drag a rectangle), press ENTER or SPACE to confirm, or 'c' to cancel.")

    # selectROI returns (x, y, w, h) in the *display* image coordinates
    roi_disp = cv2.selectROI("Select ROI", display_img, showCrosshair=True, fromCenter=False)
    cv2.destroyWindow("Select ROI")

    x_d, y_d, w_d, h_d = roi_disp
    if w_d == 0 or h_d == 0:
        print("No ROI selected. Exiting.")
        return

    # --- Map ROI back to ORIGINAL image coordinates ---
    if scale != 1.0:
        x = int(round(x_d / scale))
        y = int(round(y_d / scale))
        w = int(round(w_d / scale))
        h = int(round(h_d / scale))
    else:
        x, y, w, h = x_d, y_d, w_d, h_d

    # Clamp to image bounds (safety)
    x = max(0, min(x, W - 1))
    y = max(0, min(y, H - 1))
    w = max(1, min(w, W - x))
    h = max(1, min(h, H - y))

    print(f"Selected ROI (original image coords): x={x}, y={y}, w={w}, h={h}")

    # --- Your intrinsics (pixels) ---
    FX = 4124.85217000
    FY = 4126.41606000
    cx = 2774.74600000
    cy = 2302.01489000

    # --- Measured distance to object plane (mm) ---
    Z = 300  # e.g., 300 mm = 30 cm

    # Compute real-world width/height from pinhole model (fronto-parallel assumption)
    # Corners in pixel coords
    u1, v1 = x, y
    u2, v2 = x + w, y + h

    # Real-world coords (mm)
    X1 = (u1 - cx) * Z / FX
    Y1 = (v1 - cy) * Z / FY
    X2 = (u2 - cx) * Z / FX
    Y2 = (v2 - cy) * Z / FY

    real_width_mm = abs(X2 - X1)
    real_height_mm = abs(Y2 - Y1)

    width_inches  = convert_milli_to_inch(real_width_mm)
    height_inches = convert_milli_to_inch(real_height_mm)

    print(f"Calculated Real-World Width : {real_width_mm:.2f} mm ({width_inches:.2f} in)")
    print(f"Calculated Real-World Height: {real_height_mm:.2f} mm ({height_inches:.2f} in)")

    # --- Visualization (on original size image) ---
    vis = image.copy()
    cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 220, 0), 2)
    cv2.putText(vis, f"W: {real_width_mm:.2f} mm", (x, max(0, y - 10)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 220, 0), 2, cv2.LINE_AA)
    cv2.putText(vis, f"H: {real_height_mm:.2f} mm", (x, y + h + 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 220, 0), 2, cv2.LINE_AA)

    # Save full-resolution annotated image
    out_path = os.path.join(project_root, "annotated_image.png")
    cv2.imwrite(out_path, vis)
    print(f"Annotated image saved to: {out_path}")

    # For viewing, show a scaled preview that fits the screen
    preview = vis if scale == 1.0 else cv2.resize(vis, (disp_w, disp_h), interpolation=cv2.INTER_AREA)
    cv2.namedWindow("Annotated Preview", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Annotated Preview", preview.shape[1], preview.shape[0])
    cv2.imshow("Annotated Preview", preview)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    calculate_dimensions_from_image()
