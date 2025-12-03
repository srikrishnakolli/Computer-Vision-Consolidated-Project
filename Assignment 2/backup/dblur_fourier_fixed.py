# # deblur_fourier_fixed.py
# #Assignment 2 - Qestion 2
# import os, glob
# import numpy as np
# import cv2 as cv
# from matplotlib import pyplot as plt

# # ---- SETTINGS ----
# PREFERRED_NAME = "IMG_4309.JPG"   # what you intend to use
# SIGMA = 3.0
# KERNEL_SIZE = 19           # keep odd; ~6*sigma+1 is a good rule
# MODE = "wiener"            # "wiener" or "inverse"
# K_WIENER = 0.01
# # -------------------

# def read_bgr_robust(path_candidates):
#     """Try OpenCV first, then Pillow (EXIF/HEIC). Return BGR np.uint8 or None."""
#     for p in path_candidates:
#         if not os.path.exists(p):
#             continue
#         img = cv.imread(p, cv.IMREAD_COLOR)
#         if img is not None:
#             print(f"[load] OpenCV: {p}")
#             return img
#         # Pillow fallback (HEIC/EXIF)
#         try:
#             from PIL import Image, ImageOps
#             try:
#                 import pillow_heif  # enables HEIC if installed
#                 pillow_heif.register_heif_opener()
#             except Exception:
#                 pass
#             pil = Image.open(p)
#             pil = ImageOps.exif_transpose(pil).convert("RGB")
#             arr = np.array(pil)                  # RGB uint8
#             img = cv.cvtColor(arr, cv.COLOR_RGB2BGR)
#             print(f"[load] Pillow:  {p}")
#             return img
#         except Exception:
#             pass
#     return None

# def gaussian_psf(ksize, sigma):
#     ax = np.arange(ksize) - (ksize - 1)/2.0
#     xx, yy = np.meshgrid(ax, ax)
#     psf = np.exp(-(xx**2 + yy**2)/(2.0*sigma**2)).astype(np.float32)
#     psf /= psf.sum()
#     return psf

# def psf_to_otf(psf, shapeHW):
#     H, W = shapeHW
#     pad = np.zeros((H, W), np.float32)
#     pad[:psf.shape[0], :psf.shape[1]] = np.fft.ifftshift(psf)
#     return np.fft.fft2(pad)

# def wiener_deconv(G, H, K): return (np.conj(H)/(np.abs(H)**2 + K)) * G
# def inverse_deconv(G, H, eps=1e-6): return G / (H + eps)

# def to_float01(img): return img.astype(np.float32)/255.0
# def to_uint8(x): return np.clip(x*255.0, 0, 255).astype(np.uint8)
# def ensure_odd(k): return int(k) if int(k)%2==1 else int(k)+1

# def main():
#     script_dir = os.path.dirname(os.path.abspath(__file__))

#     # Build candidate paths for L.*
#     exts = [".png",".PNG",".jpg",".JPG",".jpeg",".JPEG",".heic",".HEIC"]
#     candidates = [os.path.join(script_dir, PREFERRED_NAME)]
#     candidates += [os.path.join(script_dir, "L"+e) for e in exts]
#     # last resort: any L.* in the folder
#     candidates += sorted(glob.glob(os.path.join(script_dir, "L.*")))

#     L_bgr = read_bgr_robust(candidates)
#     if L_bgr is None:
#         print("[error] Could not read any of these:\n  " + "\n  ".join(candidates))
#         print("[hint] Put your image next to this script as 'L.png' (or .jpg/.jpeg/.heic).")
#         return

#     L = to_float01(L_bgr)

#     # Blur -> L_b
#     ksize = ensure_odd(KERNEL_SIZE)
#     psf = gaussian_psf(ksize, SIGMA)
#     L_b = np.stack([cv.filter2D(L[:,:,c], -1, psf, borderType=cv.BORDER_REFLECT)
#                     for c in range(3)], axis=2)

#     # Fourier deconvolution -> recover L
#     Hh, Ww = L.shape[:2]
#     OTF = psf_to_otf(psf, (Hh, Ww))
#     L_rec = np.zeros_like(L)
#     for c in range(3):
#         G = np.fft.fft2(L_b[:,:,c])
#         Fhat = wiener_deconv(G, OTF, K_WIENER) if MODE=="wiener" else inverse_deconv(G, OTF, 1e-6)
#         L_rec[:,:,c] = np.clip(np.fft.ifft2(Fhat).real, 0.0, 1.0)

#     cv.imwrite("Lb_blur.png", to_uint8(L_b))
#     cv.imwrite("L_recovered.png", to_uint8(L_rec))
#     print("[save] Lb_blur.png")
#     print("[save] L_recovered.png")

#     # Quick visualization
#     plt.figure(figsize=(12,5))
#     plt.subplot(1,3,1); plt.imshow(cv.cvtColor(to_uint8(L), cv.COLOR_BGR2RGB)); plt.title("Original L"); plt.axis('off')
#     plt.subplot(1,3,2); plt.imshow(cv.cvtColor(to_uint8(L_b), cv.COLOR_BGR2RGB)); plt.title(f"L_b (σ={SIGMA}, k={ksize})"); plt.axis('off')
#     plt.subplot(1,3,3); plt.imshow(cv.cvtColor(to_uint8(L_rec), cv.COLOR_BGR2RGB)); plt.title(f"Recovered (Fourier {MODE})"); plt.axis('off')
#     plt.tight_layout(); plt.show()

# if __name__ == "__main__":
#     main()




##-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# FOR DISPLAYING ALL 3 FUNCTIONALITY AT ONCE


# deblur_fourier_fixed.py
#Assignment 2 - Qestion 2
import os, glob
import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

# ---- SETTINGS ----
PREFERRED_NAME = "L_input.jpg"   # updated preferred filename
SIGMA = 7.0                      # updated blur strength
KERNEL_SIZE = 43                 # updated kernel (odd; ~6*SIGMA+1)
MODE = "wiener"                  # unchanged: "wiener" or "inverse"
K_WIENER = 0.0045                # updated Wiener K
# -------------------

def read_bgr_robust(path_candidates):
    """Try OpenCV first, then Pillow (EXIF/HEIC). Return BGR np.uint8 or None."""
    for p in path_candidates:
        if not os.path.exists(p):
            continue
        img = cv.imread(p, cv.IMREAD_COLOR)
        if img is not None:
            print(f"[load] OpenCV: {p}")
            return img
        # Pillow fallback (HEIC/EXIF)
        try:
            from PIL import Image, ImageOps
            try:
                import pillow_heif  # enables HEIC if installed
                pillow_heif.register_heif_opener()
            except Exception:
                pass
            pil = Image.open(p)
            pil = ImageOps.exif_transpose(pil).convert("RGB")
            arr = np.array(pil)                  # RGB uint8
            img = cv.cvtColor(arr, cv.COLOR_RGB2BGR)
            print(f"[load] Pillow:  {p}")
            return img
        except Exception:
            pass
    return None

def gaussian_psf(ksize, sigma):
    ax = np.arange(ksize) - (ksize - 1)/2.0
    xx, yy = np.meshgrid(ax, ax)
    psf = np.exp(-(xx**2 + yy**2)/(2.0*sigma**2)).astype(np.float32)
    psf /= psf.sum()
    return psf

def psf_to_otf(psf, shapeHW):
    H, W = shapeHW
    pad = np.zeros((H, W), np.float32)
    pad[:psf.shape[0], :psf.shape[1]] = np.fft.ifftshift(psf)
    return np.fft.fft2(pad)

def wiener_deconv(G, H, K): return (np.conj(H)/(np.abs(H)**2 + K)) * G
def inverse_deconv(G, H, eps=1e-6): return G / (H + eps)

def to_float01(img): return img.astype(np.float32)/255.0
def to_uint8(x): return np.clip(x*255.0, 0, 255).astype(np.uint8)
def ensure_odd(k): return int(k) if int(k)%2==1 else int(k)+1

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Build candidate paths for L.*
    exts = [".png",".PNG",".jpg",".JPG",".jpeg",".JPEG",".heic",".HEIC"]
    candidates = [os.path.join(script_dir, PREFERRED_NAME)]
    candidates += [os.path.join(script_dir, "L"+e) for e in exts]
    # last resort: any L.* in the folder
    candidates += sorted(glob.glob(os.path.join(script_dir, "L.*")))

    L_bgr = read_bgr_robust(candidates)
    if L_bgr is None:
        print("[error] Could not read any of these:\n  " + "\n  ".join(candidates))
        print("[hint] Put your image next to this script as 'L.png' (or .jpg/.jpeg/.heic).")
        return

    L = to_float01(L_bgr)

    # Blur -> L_b
    ksize = ensure_odd(KERNEL_SIZE)
    psf = gaussian_psf(ksize, SIGMA)
    L_b = np.stack([cv.filter2D(L[:,:,c], -1, psf, borderType=cv.BORDER_REFLECT)
                    for c in range(3)], axis=2)

    # Fourier deconvolution -> recover L
    Hh, Ww = L.shape[:2]
    OTF = psf_to_otf(psf, (Hh, Ww))
    L_rec = np.zeros_like(L)
    for c in range(3):
        G = np.fft.fft2(L_b[:,:,c])
        Fhat = wiener_deconv(G, OTF, K_WIENER) if MODE=="wiener" else inverse_deconv(G, OTF, 1e-6)
        L_rec[:,:,c] = np.clip(np.fft.ifft2(Fhat).real, 0.0, 1.0)

    cv.imwrite("Lb_blur.png", to_uint8(L_b))
    cv.imwrite("L_recovered.png", to_uint8(L_rec))
    print("[save] Lb_blur.png")
    print("[save] L_recovered.png")

    # Quick visualization
    plt.figure(figsize=(12,5))
    plt.subplot(1,3,1); plt.imshow(cv.cvtColor(to_uint8(L), cv.COLOR_BGR2RGB)); plt.title("Original L"); plt.axis('off')
    plt.subplot(1,3,2); plt.imshow(cv.cvtColor(to_uint8(L_b), cv.COLOR_BGR2RGB)); plt.title(f"L_b (σ={SIGMA}, k={ksize})"); plt.axis('off')
    plt.subplot(1,3,3); plt.imshow(cv.cvtColor(to_uint8(L_rec), cv.COLOR_BGR2RGB)); plt.title(f"Recovered (Fourier {MODE})"); plt.axis('off')
    plt.tight_layout(); plt.show()

if __name__ == "__main__":
    main()
