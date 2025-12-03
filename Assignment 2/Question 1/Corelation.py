
#Working But Detection app is super zoomed in
# working and later gave error
## ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# import cv2 as cv
# import numpy as np
# from matplotlib import pyplot as plt
# import glob, os

# # --- read test image ---
# img = cv.imread('Temp.JPG', cv.IMREAD_GRAYSCALE)
# assert img is not None, "Could not read realobj.JPG"
# img = cv.GaussianBlur(img, (3,3), 0)

# # --- gather templates (all .JPG in folder 'template') ---
# template_paths = sorted(glob.glob('templates/*.JPG'))
# assert len(template_paths) > 0, "No templates found in template/*.JPG"
# print("Templates:", template_paths)

# METHOD = cv.TM_CCOEFF_NORMED
# SCALES = np.linspace(0.5, 1.4, 19)  # +/- ~40% (keep exactly as you had)
# ANGLES = [0, 180]                   # keep as you had
# SCORE_THRESH = 0.40                 # draw only if at least this confident

# def rotate_keep_all(tpl, angle):
#     rows, cols = tpl.shape[:2]
#     M = cv.getRotationMatrix2D((cols/2, rows/2), angle, 1.0)
#     cos, sin = abs(M[0,0]), abs(M[0,1])
#     nW = int(rows*sin + cols*cos)
#     nH = int(rows*cos + cols*sin)
#     M[0,2] += (nW/2) - cols/2
#     M[1,2] += (nH/2) - rows/2
#     return cv.warpAffine(tpl, M, (nW, nH), flags=cv.INTER_LINEAR, borderMode=cv.BORDER_REPLICATE)

# vis = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
# colors = [(0,255,0),(0,180,255),(255,160,0),(255,0,120),(120,255,120),(160,120,255),(200,200,0),(0,220,180)]

# for idx, tpath in enumerate(template_paths):
#     tpl = cv.imread(tpath, cv.IMREAD_GRAYSCALE)
#     if tpl is None:
#         print(f"[skip] Can't read template: {tpath}")
#         continue
#     tpl = cv.GaussianBlur(tpl, (3,3), 0)

#     best_score, best = -1.0, None
#     for ang in ANGLES:
#         tpl_rot = rotate_keep_all(tpl, ang)
#         for s in SCALES:
#             tw = max(5, int(tpl_rot.shape[1]*s))
#             th = max(5, int(tpl_rot.shape[0]*s))
#             if tw >= img.shape[1] or th >= img.shape[0]:
#                 continue
#             tpl_scaled = cv.resize(tpl_rot, (tw, th), interpolation=cv.INTER_AREA)
#             res = cv.matchTemplate(img, tpl_scaled, METHOD)
#             _, max_val, _, max_loc = cv.minMaxLoc(res)
#             if max_val > best_score:
#                 best_score = max_val
#                 best = (max_loc, (tw, th), s, ang)

#     # name = os.path.basename(tpath)
#     # if best is None:
#     #     print(f"[warn] No valid scales for {name} (template larger than image).")
#     #     continue
#     # (x,y), (w,h), s, ang = best
#     # print(f"Detected '{os.path.splitext(name)[0]}' at {x},{y} (score={best_score:.2f}, scale={s:.2f}, angle={ang}°)")

#     # if best_score >= SCORE_THRESH:
#     #     color = colors[idx % len(colors)]
#     #     cv.rectangle(vis, (x,y), (x+w, y+h), color, 2)
#     #     cv.putText(vis, f"{os.path.splitext(name)[0]}  {best_score:.2f}@{s:.2f}x,{ang}d",
#     #                (x, max(15, y-6)), cv.FONT_HERSHEY_SIMPLEX, 0.55, color, 1, cv.LINE_AA)

# # Drwaing box around object fix -code
#     name = os.path.basename(tpath)
#     if best is None:
#         print(f"[warn] No valid scales for {name} (template larger than image).")
#         continue

#     (x, y), (w, h), s, ang = best

#     # Print with more precision and show threshold explicitly
#     print(f"Detected '{os.path.splitext(name)[0]}' at {x},{y} "f"(score={best_score:.4f}, thresh={SCORE_THRESH:.4f}, scale={s:.2f}, angle={ang}°)")

#     EPS = 1e-6
#     if best_score + EPS >= SCORE_THRESH:
#     # draw a green box when passing threshold
#         color = colors[idx % len(colors)]
#         cv.rectangle(vis, (x, y), (x + w, y + h), color, 2)
#         cv.putText(vis, f"{os.path.splitext(name)[0]}  {best_score:.4f}@{s:.2f}x,{ang}d",
#                (x, max(15, y - 6)), cv.FONT_HERSHEY_SIMPLEX, 0.55, color, 1, cv.LINE_AA)
#     else:
#     # optional: show the best location anyway (thin orange box) to help tuning
#         below_color = (0, 165, 255)  # orange
#         cv.rectangle(vis, (x, y), (x + w, y + h), below_color, 1)
#         cv.putText(vis, f"{os.path.splitext(name)[0]}  {best_score:.4f} < {SCORE_THRESH:.4f}",
#                (x, max(15, y - 6)), cv.FONT_HERSHEY_SIMPLEX, 0.5, below_color, 1, cv.LINE_AA)


# # --- save + display (both) ---
# out_path = "multi_match_result.png"
# cv.imwrite(out_path, vis)
# print(f"Saved annotated image -> {out_path}")


# #Zoomed in code- fix 

# DISPLAY_MAX_W, DISPLAY_MAX_H = 1400, 900   # change if you like

# def make_display(img_bgr, max_w=DISPLAY_MAX_W, max_h=DISPLAY_MAX_H, allow_upscale=False):
#     """Return a copy scaled to fit in max_w x max_h (preserves aspect)."""
#     h, w = img_bgr.shape[:2]
#     s = min(max_w / w, max_h / h)
#     if not allow_upscale:
#         s = min(s, 1.0)
#     if s < 1.0 or (allow_upscale and s != 1.0):
#         interp = cv.INTER_AREA if s < 1.0 else cv.INTER_CUBIC
#         disp = cv.resize(img_bgr, (int(w*s), int(h*s)), interpolation=interp)
#     else:
#         disp = img_bgr.copy()
#     return disp, s

# def show_with_zoom(img_bgr, initial_zoom=None):
#     """Interactive viewer: +/- to zoom, q/ESC to quit."""
#     cv.namedWindow("Detections", cv.WINDOW_NORMAL | cv.WINDOW_KEEPRATIO)
#     # initial fit-to-screen zoom
#     fit_disp, fit_s = make_display(img_bgr, allow_upscale=False)
#     zoom = fit_s if initial_zoom is None else initial_zoom

#     def draw():
#         h, w = img_bgr.shape[:2]
#         z = max(0.05, min(5.0, zoom))  # clamp
#         interp = cv.INTER_AREA if z < 1.0 else cv.INTER_LINEAR
#         disp = cv.resize(img_bgr, (int(w*z), int(h*z)), interpolation=interp)
#         cv.imshow("Detections", disp)
#         cv.resizeWindow("Detections", min(disp.shape[1], DISPLAY_MAX_W), min(disp.shape[0], DISPLAY_MAX_H))

#     draw()
#     while True:
#         k = cv.waitKey(0) & 0xFF
#         if k in (27, ord('q')):      # ESC or q
#             break
#         elif k in (ord('+'), ord('=')):
#             zoom *= 1.25
#             draw()
#         elif k in (ord('-'), ord('_')):
#             zoom /= 1.25
#             draw()
#     cv.destroyAllWindows()

# # --- prefer OpenCV interactive window; fall back to matplotlib if needed ---
# try:
#     show_with_zoom(vis)
# except Exception as e:
#     print("[INFO] OpenCV GUI not available, falling back to matplotlib:", e)
#     try:
#         import matplotlib.pyplot as plt
#         disp, _ = make_display(vis, allow_upscale=False)
#         plt.figure(figsize=(10, 8))
#         plt.imshow(cv.cvtColor(disp, cv.COLOR_BGR2RGB))
#         plt.title("Best match per template (scaled to fit)"); plt.axis('off')
#         plt.tight_layout(); plt.show()
#     except Exception as e2:
#         print("[WARN] Matplotlib not available either:", e2)
#         print("Open the saved file directly:", out_path)
# # Try OpenCV window first; fall back to matplotlib if GUI not available
# try:
#     cv.imshow("Detections", vis)
#     cv.waitKey(0)
#     cv.destroyAllWindows()
# except Exception:
#     plt.figure(figsize=(8,10))
#     plt.imshow(cv.cvtColor(vis, cv.COLOR_BGR2RGB))
#     plt.title("Best match per template")
#     plt.axis('off')
#     plt.show()




## ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## NEW CODE 
# import cv2 as cv
# import numpy as np
# from pathlib import Path
# import argparse, glob, os, sys

# # ------------------------- CLI -------------------------
# ap = argparse.ArgumentParser(description="Template matching by correlation (Q1)")
# ap.add_argument("--image", "-i", help="Path to scene image (e.g., OriginalIMG.JPG)")
# ap.add_argument("--templates", "-t", help="Glob for templates (e.g., templates\\*.JPG or templates/*.jpg)")
# ap.add_argument("--method", choices=["ccorr","ccoeff"], default="ccoeff",
#                help="TM_CCORR_NORMED (ccorr) or TM_CCOEFF_NORMED (ccoeff)")
# ap.add_argument("--thresh", type=float, default=0.60, help="Score threshold for drawing a box")
# ap.add_argument("--scale_start", type=float, default=0.7)
# ap.add_argument("--scale_stop",  type=float, default=1.3)
# ap.add_argument("--scale_step",  type=float, default=0.1)
# ap.add_argument("--angles", nargs="*", type=float, default=[0], help="Angles to try (deg). e.g., --angles 0 180")
# ap.add_argument("--blur", action="store_true", help="(Q3) Blur detected ROI(s) in output")
# ap.add_argument("--sigma", type=float, default=12.0, help="Blur sigma if --blur")
# ap.add_argument("--ksize", type=int, default=0, help="Blur kernel (odd). 0 => auto ≈ 6*sigma+1")
# ap.add_argument("--out", default="result_q1.png", help="Output annotated image")
# args = ap.parse_args()

# SCRIPT_DIR = Path(__file__).resolve().parent

# # Defaults if not provided
# scene_path = Path(args.image) if args.image else (SCRIPT_DIR / "OriginalIMG.JPG")
# tpl_glob   = args.templates if args.templates else str(SCRIPT_DIR / "templates" / "*.JPG")

# # ------------------------- Load inputs safely -------------------------
# def die(msg):
#     print(msg, file=sys.stderr)
#     sys.exit(2)

# if not scene_path.exists():
#     # Help user see where we looked and what files exist nearby
#     die(f"[ERR] Scene not found at:\n  {scene_path}\n\n"
#         f"Tip 1: use --image \"C:\MS-CS25\Fall 25\Computer Vison\Assignment 2\Question 1\OrginalIMG.JPG\".\n"
#         f"Tip 2: put the image next to the script and name it 'OriginalIMG.JPG'.")

# tpl_paths = sorted(glob.glob(tpl_glob))
# if len(tpl_paths) == 0:
#     die(f"[ERR] No templates matched the pattern:\n  {tpl_glob}\n\n"
#         f"Tip: check extension case (.jpg vs .JPG) or pass --templates \"C:\\...\\templates\\*.jpg\"")

# img = cv.imread(str(scene_path), cv.IMREAD_GRAYSCALE)
# if img is None:
#     die(f"[ERR] OpenCV could not read the scene:\n  {scene_path}\n"
#         f"Check file integrity/extension; try re-saving as .jpg or .png.")

# print(f"[OK] Scene: {scene_path}  size={img.shape[1]}x{img.shape[0]}")
# print("[OK] Templates:", len(tpl_paths))

# # ------------------------- Params -------------------------
# METHOD = cv.TM_CCORR_NORMED if args.method == "ccorr" else cv.TM_CCOEFF_NORMED
# SCALES = np.arange(args.scale_start, args.scale_stop + 1e-9, args.scale_step)
# ANGLES = args.angles
# THRESH = args.thresh

# # ------------------------- Helpers -------------------------
# def rotate_keep_all(tpl, angle):
#     rows, cols = tpl.shape[:2]
#     M = cv.getRotationMatrix2D((cols/2, rows/2), angle, 1.0)
#     cos, sin = abs(M[0,0]), abs(M[0,1])
#     nW = int(rows*sin + cols*cos)
#     nH = int(rows*cos + cols*sin)
#     M[0,2] += (nW/2) - cols/2
#     M[1,2] += (nH/2) - rows/2
#     return cv.warpAffine(tpl, M, (nW, nH), flags=cv.INTER_LINEAR, borderMode=cv.BORDER_REPLICATE)

# def draw_fit_window(win_name, image_bgr):
#     # Show in a resizable window that fits typical screens
#     h, w = image_bgr.shape[:2]
#     scale = 1.0
#     maxw, maxh = 1300, 900
#     if w > maxw or h > maxh:
#         scale = min(maxw / w, maxh / h)
#     disp = image_bgr if abs(scale-1.0) < 1e-3 else cv.resize(image_bgr, (int(w*scale), int(h*scale)))
#     cv.imshow(win_name, disp)

# # ------------------------- Matching -------------------------
# vis = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
# out_for_blur = vis.copy()
# colors = [(0,255,0),(0,180,255),(255,160,0),(255,0,120),(120,255,120),(160,120,255),(200,200,0),(0,220,180)]

# detections = []

# for idx, tpath in enumerate(tpl_paths):
#     tpl = cv.imread(tpath, cv.IMREAD_GRAYSCALE)
#     if tpl is None:
#         print(f"[WARN] Skipping unreadable template: {tpath}")
#         continue

#     best_score, best = -1.0, None
#     for ang in ANGLES:
#         tpl_rot = rotate_keep_all(tpl, ang) if abs(ang) > 1e-6 else tpl
#         for s in SCALES:
#             tw = max(5, int(tpl_rot.shape[1]*s))
#             th = max(5, int(tpl_rot.shape[0]*s))
#             if tw >= img.shape[1] or th >= img.shape[0]:
#                 continue
#             tpl_scaled = cv.resize(tpl_rot, (tw, th), interpolation=cv.INTER_AREA if s<1.0 else cv.INTER_CUBIC)
#             res = cv.matchTemplate(img, tpl_scaled, METHOD)
#             _, max_val, _, max_loc = cv.minMaxLoc(res)
#             if max_val > best_score:
#                 best_score = max_val
#                 best = (max_loc, (tw, th), s, ang)

#     name = Path(tpath).name
#     if best is None:
#         print(f"[WARN] No valid scales for {name} (template larger than image).")
#         continue

#     (x,y), (w,h), s, ang = best
#     print(f"[INFO] {name}: score={best_score:.4f}, pos=({x},{y}), wh=({w},{h}), scale={s:.2f}, angle={ang}°)")

#     if best_score >= THRESH:
#         detections.append((x,y,w,h, best_score, name))
#         color = colors[idx % len(colors)]
#         cv.rectangle(vis, (x,y), (x+w, y+h), color, 2)
#         cv.putText(vis, f"{Path(name).stem} {best_score:.2f}", (x, max(15, y-6)),
#                    cv.FONT_HERSHEY_SIMPLEX, 0.55, color, 1, cv.LINE_AA)

# # ------------------------- (Q3 optional) Blur ROI(s) -------------------------
# if args.blur and len(detections) > 0:
#     sigma = float(args.sigma)
#     ksize = int(args.ksize) if args.ksize > 0 else int(2 * round(3 * sigma) + 1)
#     if ksize % 2 == 0: ksize += 1
#     for (x,y,w,h,score,name) in detections:
#         roi = out_for_blur[y:y+h, x:x+w]
#         cv.GaussianBlur(roi, (ksize, ksize), sigma, sigma, dst=roi, borderType=cv.BORDER_DEFAULT)
#     print(f"[OK] Applied blur to {len(detections)} detection(s) with sigma={sigma}, ksize={ksize}")
# else:
#     if args.blur:
#         print("[INFO] No detections above threshold; nothing to blur.")

# # ------------------------- Save + show -------------------------
# cv.imwrite(args.out, vis)
# print(f"[OK] Saved annotated image -> {args.out}")

# cv.namedWindow("Detections", cv.WINDOW_NORMAL)
# draw_fit_window("Detections", vis)

# if args.blur:
#     cv.namedWindow("Blurred-ROIs", cv.WINDOW_NORMAL)
#     draw_fit_window("Blurred-ROIs", out_for_blur)

# print("[INFO] Press any key on an image window to close.")
# cv.waitKey(0)
# cv.destroyAllWindows()



##----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



# Try 3 code

import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
from pathlib import Path
import glob, os, sys

# -------------------- INPUTS --------------------
SCENE_PATH = "realObj.JPG"                     # scene image
TEMPLATE_GLOB = "templates/*.JPG"           # templates folder
METHOD = cv.TM_CCOEFF_NORMED                # correlation coefficient (Q1-friendly)
SCALES = np.linspace(0.5, 1.4, 19)          # +/- ~40%
ANGLES = [0, 180]                           # angles to evaluate
SCORE_THRESH = 0.60                         # draw only if >= this

# --- Angle handling ---
FORCE_ZERO_ANGLE = False     # True => ignore 180 entirely
PREFER_ANGLE_0 = True        # prefer 0° if it's close to 180°
ANGLE_MARGIN = 0.03          # "close" means score_0 >= score_180 - ANGLE_MARGIN

# --- Display sizes ---
DISPLAY_MAX_W, DISPLAY_MAX_H = 1400, 900

# -------------------- helpers --------------------
def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)

def rotate_keep_all(tpl, angle):
    rows, cols = tpl.shape[:2]
    M = cv.getRotationMatrix2D((cols/2, rows/2), angle, 1.0)
    cos, sin = abs(M[0,0]), abs(M[0,1])
    nW = int(rows*sin + cols*cos)
    nH = int(rows*cos + cols*sin)
    M[0,2] += (nW/2) - cols/2
    M[1,2] += (nH/2) - rows/2
    return cv.warpAffine(tpl, M, (nW, nH), flags=cv.INTER_LINEAR, borderMode=cv.BORDER_REPLICATE)

def make_display(img_bgr, max_w=DISPLAY_MAX_W, max_h=DISPLAY_MAX_H, allow_upscale=False):
    h, w = img_bgr.shape[:2]
    s = min(max_w / w, max_h / h)
    if not allow_upscale:
        s = min(s, 1.0)
    if s < 1.0 or (allow_upscale and s != 1.0):
        interp = cv.INTER_AREA if s < 1.0 else cv.INTER_CUBIC
        disp = cv.resize(img_bgr, (int(w*s), int(h*s)), interpolation=interp)
    else:
        disp = img_bgr.copy()
    return disp, s

def show_with_zoom(img_bgr, title="Detections", initial_zoom=None):
    cv.namedWindow(title, cv.WINDOW_NORMAL | cv.WINDOW_KEEPRATIO)
    fit_disp, fit_s = make_display(img_bgr, allow_upscale=False)
    zoom = fit_s if initial_zoom is None else initial_zoom

    def draw():
        h, w = img_bgr.shape[:2]
        z = max(0.05, min(5.0, zoom))
        interp = cv.INTER_AREA if z < 1.0 else cv.INTER_LINEAR
        disp = cv.resize(img_bgr, (int(w*z), int(h*z)), interpolation=interp)
        cv.imshow(title, disp)
        cv.resizeWindow(title, min(disp.shape[1], DISPLAY_MAX_W), min(disp.shape[0], DISPLAY_MAX_H))

    draw()
    while True:
        k = cv.waitKey(0) & 0xFF
        if k in (27, ord('q')): break
        elif k in (ord('+'), ord('=')): zoom *= 1.25; draw()
        elif k in (ord('-'), ord('_')): zoom /= 1.25; draw()
    cv.destroyAllWindows()

# -------------------- load inputs --------------------
img = cv.imread(SCENE_PATH, cv.IMREAD_GRAYSCALE)
if img is None:
    die(f"[ERR] Could not read scene image: {SCENE_PATH}")

img = cv.GaussianBlur(img, (3,3), 0)  # mild denoise (keep if it helps your images)

template_paths = sorted(glob.glob(TEMPLATE_GLOB))
if len(template_paths) == 0:
    die(f"[ERR] No templates found with glob: {TEMPLATE_GLOB}")
print("Templates:", template_paths)

# -------------------- main --------------------
vis = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
colors = [(0,255,0),(0,180,255),(255,160,0),(255,0,120),(120,255,120),(160,120,255),(200,200,0),(0,220,180)]

# If forcing 0°, ignore 180 entirely
angles_to_use = [0] if FORCE_ZERO_ANGLE else ANGLES

for idx, tpath in enumerate(template_paths):
    tpl = cv.imread(tpath, cv.IMREAD_GRAYSCALE)
    if tpl is None:
        print(f"[skip] Can't read template: {tpath}")
        continue
    tpl = cv.GaussianBlur(tpl, (3,3), 0)

    # Track the BEST per angle, then decide which angle to keep (preference for 0°)
    best_per_angle = {}  # angle -> (score, (x,y), (w,h), scale)
    for ang in angles_to_use:
        tpl_rot = rotate_keep_all(tpl, ang) if abs(ang) > 1e-6 else tpl
        angle_best_score = -1.0
        angle_best = None
        for s in SCALES:
            tw = max(5, int(tpl_rot.shape[1]*s))
            th = max(5, int(tpl_rot.shape[0]*s))
            if tw >= img.shape[1] or th >= img.shape[0]:
                continue
            tpl_scaled = cv.resize(tpl_rot, (tw, th),
                                   interpolation=cv.INTER_AREA if s < 1.0 else cv.INTER_CUBIC)
            res = cv.matchTemplate(img, tpl_scaled, METHOD)
            _, max_val, _, max_loc = cv.minMaxLoc(res)
            if max_val > angle_best_score:
                angle_best_score = max_val
                angle_best = (max_loc, (tw, th), s)
        if angle_best is not None:
            best_per_angle[ang] = (angle_best_score, *angle_best)

    name = os.path.basename(tpath)
    if not best_per_angle:
        print(f"[warn] No valid scales for {name} (template larger than image).")
        continue

    # Choose between 0° and 180° with preference for 0° if "close enough"
    chosen_angle = max(best_per_angle, key=lambda a: best_per_angle[a][0])  # highest score by default
    if PREFER_ANGLE_0 and 0 in best_per_angle and 180 in best_per_angle:
        score0 = best_per_angle[0][0]
        score180 = best_per_angle[180][0]
        if score0 >= (score180 - ANGLE_MARGIN):
            chosen_angle = 0  # prefer upright if nearly tied

    best_score, (x,y), (w,h), s = best_per_angle[chosen_angle]

    print(f"Detected '{os.path.splitext(name)[0]}' at {x},{y} "
          f"(score={best_score:.4f}, thresh={SCORE_THRESH:.4f}, "
          f"scale={s:.2f}, angle={chosen_angle}°; "
          f"s0={best_per_angle.get(0,(-1,))[0]:.4f} s180={best_per_angle.get(180,(-1,))[0]:.4f})")

    EPS = 1e-6
    if best_score + EPS >= SCORE_THRESH:
        color = colors[idx % len(colors)]
        cv.rectangle(vis, (x, y), (x + w, y + h), color, 2)
        cv.putText(vis, f"{os.path.splitext(name)[0]}  {best_score:.4f}@{s:.2f}x,{chosen_angle}d",
                   (x, max(15, y - 6)), cv.FONT_HERSHEY_SIMPLEX, 0.55, color, 1, cv.LINE_AA)
    else:
        # Draw thin orange box to help tuning if below threshold
        below_color = (0, 165, 255)
        cv.rectangle(vis, (x, y), (x + w, y + h), below_color, 1)
        cv.putText(vis, f"{os.path.splitext(name)[0]}  {best_score:.4f} < {SCORE_THRESH:.4f}",
                   (x, max(15, y - 6)), cv.FONT_HERSHEY_SIMPLEX, 0.5, below_color, 1, cv.LINE_AA)

# --- save + display (both) ---
out_path = "multi_match_result.png"
cv.imwrite(out_path, vis)
print(f"Saved annotated image -> {out_path}")

# Prefer OpenCV interactive window; fall back to matplotlib if needed
try:
    show_with_zoom(vis, title="Detections")
except Exception as e:
    print("[INFO] OpenCV GUI not available, falling back to matplotlib:", e)
    try:
        disp, _ = make_display(vis, allow_upscale=False)
        plt.figure(figsize=(10, 8))
        plt.imshow(cv.cvtColor(disp, cv.COLOR_BGR2RGB))
        plt.title("Best match per template (scaled to fit)")
        plt.axis('off')
        plt.tight_layout()
        plt.show()
    except Exception as e2:
        print("[WARN] Matplotlib not available either:", e2)
        print("Open the saved file directly:", out_path)
