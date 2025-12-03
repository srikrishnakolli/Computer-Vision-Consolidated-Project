import cv2
import os
import glob
import csv

# === CONFIG ===
FOLDER = r"Calibration Pictures"            # folder containing images
EXTS = ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tif", "*.tiff")
WINDOW = "Image"
RADIUS = 4
THICKNESS = -1  # filled circle

def list_images(folder, exts):
    files = []
    for e in exts:
        files.extend(glob.glob(os.path.join(folder, e)))
    return sorted(files)

def save_points_csv(image_path, points):
    if not points:
        return
    base = os.path.splitext(os.path.basename(image_path))[0]
    out_csv = os.path.join(os.path.dirname(image_path), f"{base}_points.csv")
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["x", "y"])
        w.writerows(points)
    print(f"[saved] {out_csv}")

def main():
    images = list_images(FOLDER, EXTS)
    if not images:
        print(f"No images found in: {os.path.abspath(FOLDER)}")
        return

    cv2.namedWindow(WINDOW, cv2.WINDOW_AUTOSIZE)

    for img_path in images:
        img = cv2.imread(img_path)
        if img is None:
            print(f"[skip] Could not load: {img_path}")
            continue

        print(f"\n=== {os.path.basename(img_path)} ===")
        print("Instructions: Left-click to add a point. Press 'u' to undo last point, 's' to save CSV, 'n' for next image, 'Esc' to quit.")

        points = []
        display = img.copy()

        def on_mouse(event, x, y, flags, param):
            nonlocal display, points
            if event == cv2.EVENT_LBUTTONDOWN:
                points.append((x, y))
                cv2.circle(display, (x, y), RADIUS, (0, 255, 0), THICKNESS)
                cv2.putText(display, f"({x},{y})", (x+6, y-6), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
                print(f"Clicked at: x={x}, y={y}")

        cv2.setMouseCallback(WINDOW, on_mouse)

        while True:
            cv2.imshow(WINDOW, display)
            key = cv2.waitKey(50) & 0xFF

            if key == 27:  # Esc
                cv2.destroyAllWindows()
                return
            elif key in (ord('n'), ord('N')):  # next image
                break
            elif key in (ord('s'), ord('S')):  # save points
                save_points_csv(img_path, points)
            elif key in (ord('u'), ord('U')):  # undo last point
                if points:
                    points.pop()
                    display = img.copy()
                    for (px, py) in points:
                        cv2.circle(display, (px, py), RADIUS, (0, 255, 0), THICKNESS)
                        cv2.putText(display, f"({px},{py})", (px+6, py-6), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

        # auto-save on next if you want:
        # save_points_csv(img_path, points)

    cv2.destroyAllWindows()
    print("Done.")

if __name__ == "__main__":
    main()
