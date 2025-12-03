# camera_calib_best.py
# Best-practice calibration for a 9x6 chessboard (8x5 inner corners)

import os
import glob
import numpy as np
import cv2 as cv

# ---- Settings ----
IMAGES_DIR   = "Calibration Pictures"         # folder with your images
PATTERNS     = ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG")
INNER_COLS, INNER_ROWS = 8, 5                 # inner corners (9x6 squares -> 8x5)
SQUARE_SIZE  = 0.025                           # meters (any consistent unit)
SAVE_FILE    = "calibration_best.npz"
PREVIEW_IMG  = "undistorted_best.jpg"
SHOW         = False                           # True -> visualize detections
MIN_GOOD     = 10                              # min images with good corners
# ------------------

# Corner refinement criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

def here():
    """Directory of this script."""
    return os.path.dirname(os.path.abspath(__file__))

def load_paths():
    """Collect all image paths matching PATTERNS under IMAGES_DIR."""
    folder = os.path.join(here(), IMAGES_DIR)
    paths = []
    for pat in PATTERNS:
        paths.extend(glob.glob(os.path.join(folder, pat)))
    paths = sorted(set(paths))
    if not paths:
        raise SystemExit(f"[ERROR] No images found in: {os.path.abspath(folder)}")
    print(f"[INFO] Found {len(paths)} image(s) in {os.path.abspath(folder)}")
    return paths

def main():
    # Prepare object points for an INNER_COLS x INNER_ROWS grid
    # (0,0,0), (1,0,0), ..., scaled by SQUARE_SIZE
    objp = np.zeros((INNER_ROWS * INNER_COLS, 3), np.float32)
    objp[:, :2] = np.mgrid[0:INNER_COLS, 0:INNER_ROWS].T.reshape(-1, 2)
    objp *= SQUARE_SIZE

    objpoints = []   # 3D points in world coords
    imgpoints = []   # 2D points in image plane
    img_size = None

    paths = load_paths()
    for p in paths:
        img = cv.imread(p)
        if img is None:
            print(f"[WARN] Could not read: {p}")
            continue

        if img_size is None:
            img_size = (img.shape[1], img.shape[0])  # (width, height)
            print(f"[INFO] Image size: {img_size}")

        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # Detect inner chessboard corners
        ret, corners = cv.findChessboardCorners(
            gray, (INNER_COLS, INNER_ROWS),
            flags=cv.CALIB_CB_ADAPTIVE_THRESH + cv.CALIB_CB_NORMALIZE_IMAGE + cv.CALIB_CB_FAST_CHECK
        )

        if ret:
            # Refine corner locations to subpixel accuracy
            corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            objpoints.append(objp.copy())
            imgpoints.append(corners2)

            if SHOW:
                vis = img.copy()
                cv.drawChessboardCorners(vis, (INNER_COLS, INNER_ROWS), corners2, ret)
                cv.imshow("Detections", vis)
                cv.waitKey(100)
        else:
            print(f"[INFO] No corners found in {os.path.basename(p)}")

    if SHOW:
        cv.destroyAllWindows()

    good = len(objpoints)
    if good < MIN_GOOD:
        raise SystemExit(f"[ERROR] Only {good} usable image(s). Need at least {MIN_GOOD}.")

    # ---- Calibration (classic 5-parameter distortion model) ----
    # flags = 0 -> let OpenCV estimate fx, fy, cx, cy and [k1 k2 p1 p2 k3]
    flags = 0
    rms, K, dist, rvecs, tvecs = cv.calibrateCamera(
        objpoints, imgpoints, img_size, None, None, flags=flags, criteria=criteria
    )

    # Per-view reprojection errors
    per_view_errors = []
    for i in range(good):
        proj, _ = cv.projectPoints(objpoints[i], rvecs[i], tvecs[i], K, dist)
        err = cv.norm(imgpoints[i], proj, cv.NORM_L2) / len(proj)
        per_view_errors.append(float(err))
    mean_error = float(np.mean(per_view_errors))

    print("\n[RESULT] RMS (OpenCV): {:.6f}".format(rms))
    print("[RESULT] Mean reprojection error: {:.6f} px".format(mean_error))
    print("[RESULT] Camera matrix K:\n{}".format(K))
    print("[RESULT] Distortion coeffs [k1 k2 p1 p2 k3]:\n{}".format(dist.ravel()))

    # Save calibration
    np.savez(
        SAVE_FILE,
        K=K, dist=dist, rvecs=rvecs, tvecs=tvecs,
        rms=rms, per_view_errors=np.array(per_view_errors, dtype=np.float32),
        img_size=np.array(img_size), inner_cols=INNER_COLS, inner_rows=INNER_ROWS,
        square_size=SQUARE_SIZE
    )
    print(f"[SAVED] {SAVE_FILE}")

    # Undistort preview using the first image
    sample = cv.imread(paths[0])
    if sample is not None:
        newK, roi = cv.getOptimalNewCameraMatrix(K, dist, img_size, alpha=0.0)
        und = cv.undistort(sample, K, dist, None, newK)
        x, y, w, h = roi
        if w > 0 and h > 0:
            und = und[y:y+h, x:x+w]
        cv.imwrite(PREVIEW_IMG, und)
        print(f"[SAVED] {PREVIEW_IMG}")
    else:
        print("[WARN] Could not read first image again for undistort preview.")

if __name__ == "__main__":
    main()
