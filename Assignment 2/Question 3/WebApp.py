import os, glob, io
import numpy as np
import cv2 as cv
from PIL import Image
import streamlit as st

st.set_page_config(page_title="Template Matching + Blur", layout="wide")

# ------------------------ Helpers ------------------------
def read_gray_from_bytes(file) -> np.ndarray:
    """Read uploaded image file (bytes) to uint8 grayscale."""
    file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
    img = cv.imdecode(file_bytes, cv.IMREAD_GRAYSCALE)
    return img

def read_gray(path) -> np.ndarray:
    img = cv.imread(path, cv.IMREAD_GRAYSCALE)
    return img

def rotate_keep_all(gray, angle):
    """Rotate image by `angle` degrees, expanding canvas so nothing is clipped."""
    rows, cols = gray.shape[:2]
    M = cv.getRotationMatrix2D((cols/2, rows/2), angle, 1.0)
    cos, sin = abs(M[0,0]), abs(M[0,1])
    nW = int(rows*sin + cols*cos)
    nH = int(rows*cos + cols*sin)
    M[0,2] += (nW/2) - cols/2
    M[1,2] += (nH/2) - rows/2
    return cv.warpAffine(gray, M, (nW, nH), flags=cv.INTER_LINEAR, borderMode=cv.BORDER_REPLICATE)

def nms(boxes, scores, iou_thresh=0.3):
    """Non-maximum suppression over axis-aligned boxes."""
    if not boxes:
        return []
    b = np.array(boxes, dtype=float)
    s = np.array(scores, dtype=float)
    x1, y1 = b[:,0], b[:,1]
    x2, y2 = b[:,0] + b[:,2], b[:,1] + b[:,3]
    areas = (x2 - x1) * (y2 - y1)
    order = s.argsort()[::-1]
    keep = []
    while order.size:
        i = order[0]
        keep.append(i)
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])
        w = np.maximum(0, xx2 - xx1)
        h = np.maximum(0, yy2 - yy1)
        inter = w * h
        union = areas[i] + areas[order[1:]] - inter
        iou = np.where(union > 0, inter / union, 0.0)
        order = order[np.where(iou <= iou_thresh)[0] + 1]
    return keep

def annotate(img_bgr, dets, color_map):
    out = img_bgr.copy()
    for d in dets:
        x,y,w,h = d["x"], d["y"], d["w"], d["h"]
        name, score = d["template"], d["score"]
        color = color_map[d["template"]]
        cv.rectangle(out, (x,y), (x+w,y+h), color, 2)
        cv.putText(out, f"{name} {score:.2f}", (x, max(20, y-6)),
                   cv.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv.LINE_AA)
    return out

def blur_regions(img_bgr, dets, ksize=21, sigma=7, feather=3):
    """Blur only the detected rectangles. Feather edges to avoid seams."""
    blurred = cv.GaussianBlur(img_bgr, (ksize|1, ksize|1), sigma)
    mask = np.zeros(img_bgr.shape[:2], dtype=np.uint8)
    for d in dets:
        x,y,w,h = d["x"], d["y"], d["w"], d["h"]
        cv.rectangle(mask, (x,y), (x+w, y+h), 255, -1)
    if feather > 0:
        mask = cv.GaussianBlur(mask, (feather|1, feather|1), 0)
    mask_3 = cv.merge([mask,mask,mask])
    out = (mask_3/255.0 * blurred + (1 - mask_3/255.0) * img_bgr).astype(np.uint8)
    return out

# ------------------------ UI ------------------------
st.title("🔎 Template Matching (Correlation) + Region Blur")
st.caption("Uploads a scene image, matches all templates from ./templates, then blurs detected regions.")

colL, colR = st.columns([3,2])

with colR:
    st.subheader("Detection Settings")
    method_name = st.selectbox("OpenCV Method", [
        "TM_CCOEFF_NORMED", "TM_CCORR_NORMED", "TM_SQDIFF_NORMED"
    ], index=0)
    METHOD = getattr(cv, method_name)

    scale_min = st.number_input("Scale min", 0.05, 5.0, 0.4, 0.05)
    scale_max = st.number_input("Scale max", 0.10, 6.0, 1.8, 0.05)
    scale_steps = st.slider("Scale steps", 5, 50, 21, 1)

    angle_mode = st.selectbox("Angles", ["0° only", "0° and 180°", "−45°…+45° (step 15°)"], index=1)
    if angle_mode == "0° only":
        ANGLES = [0]
    elif angle_mode == "0° and 180°":
        ANGLES = [0, 180]
    else:
        ANGLES = list(range(-45, 46, 15))

    conf_thresh = st.slider("Draw threshold (score ≥)", 0.0, 1.0, 0.70, 0.01)
    nms_iou = st.slider("NMS IoU", 0.1, 0.9, 0.30, 0.05)

    down_max_long = st.slider("Downscale long edge (speed)", 400, 2000, 1200, 50)
    blur_ksize = st.slider("Blur kernel size", 3, 61, 25, 2)
    blur_sigma = st.slider("Blur sigma", 0, 25, 7, 1)
    feather = st.slider("Feather mask", 0, 21, 3, 1)

with colL:
    st.subheader("Scene Image")
    upl = st.file_uploader("Upload scene (JPG/PNG)", type=["jpg","jpeg","png","JPG","JPEG","PNG"])

# Load templates from ./templates/*.JPG (case-insensitive handling)
template_paths = sorted(sum([glob.glob(os.path.join("templates", pat)) for pat in
                             ("*.JPG","*.jpg","*.JPEG","*.jpeg","*.PNG","*.png")], []))
if len(template_paths) == 0:
    st.warning("Put your 10 template images in `./templates/` (e.g., templates/water.JPG).")
else:
    st.write(f"📦 Found {len(template_paths)} templates:")
    st.code("\n".join(os.path.basename(p) for p in template_paths), language="text")

run = st.button("🚀 Run detection & blur", type="primary", use_container_width=True)

# ------------------------ Core pipeline ------------------------
def resize_long_edge(gray, max_long):
    h, w = gray.shape[:2]
    long_side = max(h, w)
    if long_side <= max_long:
        return gray, 1.0
    s = max_long / float(long_side)
    small = cv.resize(gray, (int(w*s), int(h*s)), interpolation=cv.INTER_AREA)
    return small, 1.0 / s

def match_all_templates(scene_gray, templates, METHOD, scales, angles, nms_iou, draw_thresh):
    H, W = scene_gray.shape[:2]
    all_dets = []  # list of dicts: {template, x,y,w,h, score}
    for name, tpl in templates:
        best_dets = []
        for ang in angles:
            tpl_rot = rotate_keep_all(tpl, ang)
            for s in scales:
                tw = max(5, int(tpl_rot.shape[1] * s))
                th = max(5, int(tpl_rot.shape[0] * s))
                if tw >= W or th >= H:
                    continue
                tpl_scaled = cv.resize(tpl_rot, (tw, th), interpolation=cv.INTER_AREA)
                res = cv.matchTemplate(scene_gray, tpl_scaled, METHOD)
                # Depending on method, higher is better (CCOEFF/CCORR) or lower is better (SQDIFF)
                min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
                if METHOD in (cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED):
                    score = 1.0 - float(min_val)
                    loc = min_loc
                else:
                    score = float(max_val)
                    loc = max_loc
                x, y = loc
                best_dets.append({"template": name, "x": x, "y": y, "w": tw, "h": th,
                                  "score": score, "angle": ang, "scale": float(s)})

        # NMS per template to consolidate scale/angle duplicates
        if not best_dets:
            continue
        boxes = [(d["x"], d["y"], d["w"], d["h"]) for d in best_dets]
        scores = [d["score"] for d in best_dets]
        keep_idx = nms(boxes, scores, iou_thresh=nms_iou)
        kept = [best_dets[i] for i in keep_idx]
        # Keep only those above threshold
        kept = [d for d in kept if d["score"] >= draw_thresh]
        all_dets.extend(kept)
    return all_dets

if run:
    if upl is None:
        st.error("Please upload a scene image first.")
        st.stop()

    scene_gray = read_gray_from_bytes(upl)
    if scene_gray is None:
        st.error("Failed to read the upload. Try a different image.")
        st.stop()

    # Preprocess scene
    scene_gray = cv.GaussianBlur(scene_gray, (3,3), 0)
    small, back_scale = resize_long_edge(scene_gray, down_max_long)

    # Load templates (grayscale + small blur)
    templates = []
    for p in template_paths:
        g = read_gray(p)
        if g is None:
            continue
        g = cv.GaussianBlur(g, (3,3), 0)
        templates.append((os.path.splitext(os.path.basename(p))[0], g))
    if len(templates) == 0:
        st.error("No readable templates found.")
        st.stop()

    # Scales (linspace as in your scripts)
    scales = np.linspace(float(scale_min), float(scale_max), int(scale_steps))

    # Run detection on the downscaled scene
    dets_small = match_all_templates(small, templates, METHOD, scales, ANGLES, nms_iou, conf_thresh)

    # Map detections back to original resolution
    dets_full = []
    for d in dets_small:
        sb = back_scale
        dets_full.append({
            **d,
            "x": int(d["x"] * sb), "y": int(d["y"] * sb),
            "w": int(d["w"] * sb), "h": int(d["h"] * sb),
        })

    # Prepare color map per template
    palette = [(0,255,0),(0,180,255),(255,160,0),(255,0,120),(120,255,120),
               (160,120,255),(200,200,0),(0,220,180),(255,200,200),(200,255,200)]
    color_map = {}
    for i, (name, _) in enumerate(templates):
        color_map[name] = palette[i % len(palette)]

    # Visuals
    scene_bgr_full = cv.cvtColor(scene_gray, cv.COLOR_GRAY2BGR)
    annotated = annotate(scene_bgr_full, dets_full, color_map)
    blurred = blur_regions(scene_bgr_full, dets_full, ksize=blur_ksize, sigma=blur_sigma, feather=feather)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.image(cv.cvtColor(scene_bgr_full, cv.COLOR_BGR2RGB), caption="Scene (preprocessed)", use_container_width=True)
    with c2:
        st.image(cv.cvtColor(annotated, cv.COLOR_BGR2RGB), caption="Detections (correlation + NMS)", use_container_width=True)
    with c3:
        st.image(cv.cvtColor(blurred, cv.COLOR_BGR2RGB), caption="Blurred regions", use_container_width=True)

    # Downloads
    def to_png_bytes(img_bgr):
        pil = Image.fromarray(cv.cvtColor(img_bgr, cv.COLOR_BGR2RGB))
        buf = io.BytesIO(); pil.save(buf, format="PNG"); buf.seek(0); return buf

    st.download_button("⬇️ Download annotated", data=to_png_bytes(annotated), file_name="annotated.png", mime="image/png")
    st.download_button("⬇️ Download blurred", data=to_png_bytes(blurred), file_name="blurred.png", mime="image/png")

    st.success(f"Found {len(dets_full)} detections ≥ {conf_thresh:.2f}.")
    if len(dets_full):
        st.dataframe([{
            "template": d["template"], "score": round(d["score"],3),
            "angle": d["angle"], "scale": round(d["scale"],2),
            "x": d["x"], "y": d["y"], "w": d["w"], "h": d["h"]
        } for d in dets_full], use_container_width=True)

# ------------------------ Notes ------------------------
with st.expander("Notes / Tips"):
    st.markdown("""
- This uses **OpenCV correlation** (`matchTemplate`) with your choice of method (default `TM_CCOEFF_NORMED`).
- It checks **multiple scales** and **angles** per template, then runs **NMS** so only distinct peaks remain.
- The **blur** is a Gaussian applied only to the union of detected rectangles (with optional feathering to soften box edges).
- For speed/robustness on phone photos:
  - Increase **Downscale long edge** (e.g., 1000–1400).
  - Use **Angles: −45°…+45°** if objects are tilted (or `0° only` if always upright).
  - Widen **Scale min/max** if templates are very different in size vs the scene.
  - Raise **Draw threshold** (e.g., 0.8–0.9) to reduce false positives.
- Put your 10+ templates in `./templates/` before running.
""")