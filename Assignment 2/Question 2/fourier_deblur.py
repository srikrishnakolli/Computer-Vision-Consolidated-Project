# #!/usr/bin/env python3
# """
# Gaussian blur + Fourier-domain deblurring (Inverse & Wiener)

# USAGE (on your own photo L):
#   python fourier_deblur.py --input L.jpg --sigma 2.0 --outdir out

# Optional flags:
#   --ksize 13            # odd; defaults to ~6*sigma+1
#   --K 1e-3              # Wiener param (noise-to-signal power)
#   --eps 1e-3            # Inverse-filter stabilizer
#   --demo                 # run a synthetic demo if you don't have an image yet
# """
# import argparse, os, math, numpy as np, cv2

# # ---------- helpers ----------
# def gaussian_kernel(ksize, sigma):
#     ax = np.arange(-ksize//2 + 1., ksize//2 + 1.)
#     xx, yy = np.meshgrid(ax, ax)
#     kernel = np.exp(-(xx**2 + yy**2) / (2. * sigma**2))
#     kernel /= np.sum(kernel)
#     return kernel.astype(np.float32)

# def psf2otf(psf, shape):
#     """
#     Convert spatial PSF (small kernel) to OTF of size 'shape':
#     zero-pad + circular shift so PSF center is at (0,0) before FFT.
#     """
#     psf_pad = np.zeros(shape, dtype=np.float32)
#     kh, kw = psf.shape[:2]
#     psf_pad[:kh, :kw] = psf
#     psf_pad = np.roll(psf_pad, -kh//2, axis=0)
#     psf_pad = np.roll(psf_pad, -kw//2, axis=1)
#     return np.fft.fft2(psf_pad)

# def inverse_filter_fft(blur_bgr, psf, eps=1e-3):
#     """Inverse filter in Fourier domain with small stabilization eps."""
#     H, W = blur_bgr.shape[:2]
#     otf = psf2otf(psf, (H, W))
#     out = np.zeros_like(blur_bgr)
#     denom = (np.abs(otf)**2 + eps)
#     H_conj = np.conj(otf)
#     for c in range(3):
#         G = np.fft.fft2(blur_bgr[...,c])
#         Fhat = G * H_conj / denom    # = G / (otf + eps) but numerically safer
#         f = np.fft.ifft2(Fhat).real
#         out[...,c] = np.clip(f, 0, 255)
#     return out.astype(np.uint8)

# def wiener_filter_fft(blur_bgr, psf, K=1e-3):
#     """Wiener deconvolution: F = H* / (|H|^2 + K) * G."""
#     Hh, Ww = blur_bgr.shape[:2]
#     otf = psf2otf(psf, (Hh, Ww))
#     out = np.zeros_like(blur_bgr)
#     H_conj = np.conj(otf)
#     denom = (np.abs(otf)**2 + K)
#     for c in range(3):
#         G = np.fft.fft2(blur_bgr[...,c])
#         Fhat = (H_conj / denom) * G
#         f = np.fft.ifft2(Fhat).real
#         out[...,c] = np.clip(f, 0, 255)
#     return out.astype(np.uint8)

# def psnr(img, ref):
#     img = img.astype(np.float32); ref = ref.astype(np.float32)
#     mse = np.mean((img - ref) ** 2)
#     if mse <= 1e-12: return 99.0
#     return 10.0 * math.log10((255.0*255.0)/mse)

# # ---------- optional demo image ----------
# # def make_demo_image(W=960, H=640):
# #     img = np.full((H, W, 3), 255, np.uint8)
# #     cv2.rectangle(img, (20, 20), (W-20, H-20), (0,0,0), 3)
# #     cv2.line(img, (0,0), (W,H), (0,0,0), 1)
# #     cv2.line(img, (W,0), (0,H), (0,0,0), 1)
# #     cv2.circle(img, (W//3, H//2), 60, (40,40,40), 3)
# #     cv2.putText(img, "Fourier Deblur Demo", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,0), 2, cv2.LINE_AA)
# #     cv2.putText(img, "Gaussian PSF known", (30, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2, cv2.LINE_AA)
# #     tile = 16
# #     for y in range(200, H-40, tile):
# #         for x in range(40, W-40, tile):
# #             if ((x//tile)+(y//tile))%2==0:
# #                 img[y:y+tile, x:x+tile]=200
# #     return img

# # ---------- main ----------
# def main():
#     ap = argparse.ArgumentParser(description="Gaussian blur + Fourier deblurring (inverse & Wiener)")
#     ap.add_argument("--input", help="Path to your image L (color ok)")
#     ap.add_argument("--sigma", type=float, default=2.0, help="Gaussian sigma")
#     ap.add_argument("--ksize", type=int, default=None, help="Odd kernel size (defaults to ~6*sigma+1)")
#     ap.add_argument("--outdir", default="fourier_out", help="Output folder")
#     ap.add_argument("--K", type=float, default=1e-3, help="Wiener noise-to-signal ratio")
#     ap.add_argument("--eps", type=float, default=1e-3, help="Inverse-filter stabilizer")
#     ap.add_argument("--demo", action="store_true", help="Run a synthetic demo instead of using --input")
#     args = ap.parse_args()

#     os.makedirs(args.outdir, exist_ok=True)
#     if args.ksize is None:
#         args.ksize = int(2*round(3*args.sigma)+1)

#     if args.demo:
#         L = make_demo_image()
#     else:
#         if not args.input:
#             raise SystemExit("Provide --input L.jpg (or use --demo).")
#         L = cv2.imread(args.input, cv2.IMREAD_COLOR)
#         if L is None:
#             raise FileNotFoundError(f"Could not read {args.input}")

#     # Blur to create L_b (the “forward” step you control)
#     psf = gaussian_kernel(args.ksize, args.sigma)
#     L_b = cv2.GaussianBlur(L, (args.ksize, args.ksize), args.sigma, args.sigma,
#                            borderType=cv2.BORDER_REPLICATE)

#     # Deblur (Fourier domain)
#     L_inv = inverse_filter_fft(L_b, psf, eps=args.eps)   # inverse filter
#     L_wi  = wiener_filter_fft(L_b, psf, K=args.K)        # Wiener

#     # Save
#     cv2.imwrite(os.path.join(args.outdir, "L.png"), L)
#     cv2.imwrite(os.path.join(args.outdir, "L_b_blurred.png"), L_b)
#     cv2.imwrite(os.path.join(args.outdir, "L_inv_inverse.png"), L_inv)
#     cv2.imwrite(os.path.join(args.outdir, "L_wiener.png"), L_wi)

#     # If demo, report PSNR
#     if args.demo:
#         print(f"PSNR(inverse) = {psnr(L_inv, L):.2f} dB | PSNR(wiener) = {psnr(L_wi, L):.2f} dB")

#     print(f"[OK] Wrote results to: {args.outdir}")
#     print("Tip: tune --K (Wiener) and --eps (inverse). If you see edge ringing, crop borders or reduce K/eps.")

# if __name__ == "__main__":
#     main()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# """
# Convolution & Fourier Transform — Gaussian blur + Fourier deblurring (Inverse & Wiener)
# Runs with a hard-coded image path so you don't need any CLI arguments.

# HOW TO USE:
# 1) Set HARDCODED_INPUT below to your actual L.JPG path.
#    - On Windows, prefer r"C:\path\to\L.JPG" (note the 'r' for a raw string), or use forward slashes.
# 2) (Optional) Tweak SIGMA / KSIZE / K / EPS if you want.
# 3) Run:  python fourier_deblur_hardcoded.py
# Outputs will be written under ./out_L/
# """

# import os, math
# from pathlib import Path
# import numpy as np
# import cv2

# # -------------------- EDIT THIS LINE ONLY --------------------
# HARDCODED_INPUT = r"C:\MS-CS25\Fall 25\Computer Vison\Assignment 2\Question 2\L.JPG"
# # -------------------------------------------------------------

# # You can tweak these if you want:
# SIGMA   = 6.0           # Gaussian sigma used to blur (controls blur strength)
# KSIZE   = None          # If None -> computed as ~6*sigma+1 ; else set an odd int (e.g., 13)
# K       = 3e-3          # Wiener noise-to-signal power ratio (higher -> smoother/less ringing)
# EPS     = 3e-3          # Stabilizer for inverse filter (prevents blow-up at small |H|)
# OUTDIR  = "out_L"       # Where to save results

# # -------------------- helpers --------------------
# def gaussian_kernel(ksize, sigma):
#     ax = np.arange(-ksize//2 + 1., ksize//2 + 1.)
#     xx, yy = np.meshgrid(ax, ax)
#     kernel = np.exp(-(xx**2 + yy**2) / (2. * sigma**2))
#     kernel /= np.sum(kernel)
#     return kernel.astype(np.float32)

# def psf2otf(psf, shape):
#     """
#     Convert spatial PSF (small kernel) to OTF (same size as image):
#       - zero-pad PSF to 'shape'
#       - circular shift so the PSF center is at (0,0)
#       - FFT -> OTF
#     """
#     psf_pad = np.zeros(shape, dtype=np.float32)
#     kh, kw = psf.shape[:2]
#     psf_pad[:kh, :kw] = psf
#     psf_pad = np.roll(psf_pad, -kh//2, axis=0)
#     psf_pad = np.roll(psf_pad, -kw//2, axis=1)
#     return np.fft.fft2(psf_pad)

# def inverse_filter_fft(blur_bgr, psf, eps=1e-3):
#     """Inverse filter (frequency domain) with small stabilization eps."""
#     H, W = blur_bgr.shape[:2]
#     otf = psf2otf(psf, (H, W))
#     out = np.zeros_like(blur_bgr)
#     denom = (np.abs(otf)**2 + eps)
#     H_conj = np.conj(otf)
#     for c in range(3):
#         G = np.fft.fft2(blur_bgr[..., c])
#         Fhat = G * H_conj / denom
#         f = np.fft.ifft2(Fhat).real
#         out[..., c] = np.clip(f, 0, 255)
#     return out.astype(np.uint8)

# def wiener_filter_fft(blur_bgr, psf, K=1e-3):
#     """Wiener deconvolution: F = H* / (|H|^2 + K) * G"""
#     Hh, Ww = blur_bgr.shape[:2]
#     otf = psf2otf(psf, (Hh, Ww))
#     out = np.zeros_like(blur_bgr)
#     H_conj = np.conj(otf)
#     denom = (np.abs(otf)**2 + K)
#     for c in range(3):
#         G = np.fft.fft2(blur_bgr[..., c])
#         Fhat = (H_conj / denom) * G
#         f = np.fft.ifft2(Fhat).real
#         out[..., c] = np.clip(f, 0, 255)
#     return out.astype(np.uint8)

# # -------------------- main pipeline --------------------
# def main():
#     os.makedirs(OUTDIR, exist_ok=True)

#     img_path = str(Path(HARDCODED_INPUT))
#     L = cv2.imread(img_path, cv2.IMREAD_COLOR)
#     if L is None:
#         raise FileNotFoundError(f"Could not read image at: {img_path}")
#     print(f"[INFO] Loaded L from: {img_path}")

#     # Decide kernel size if not given
#     ksize = KSIZE if (KSIZE is not None) else int(2 * round(3 * SIGMA) + 1)
#     if ksize % 2 == 0:
#         ksize += 1  # ensure odd
#     print(f"[INFO] Using Gaussian blur with sigma={SIGMA}, ksize={ksize}")

#     # Build PSF for deconvolution (must match the blur you apply)
#     psf = gaussian_kernel(ksize, SIGMA)

#     # --- Forward step: blur to get L_b ---
#     L_b = cv2.GaussianBlur(L, (ksize, ksize), SIGMA, SIGMA, borderType=cv2.BORDER_REPLICATE)

#     # --- Deblur (frequency domain) ---
#     L_inv = inverse_filter_fft(L_b, psf, eps=EPS)
#     L_wi  = wiener_filter_fft(L_b, psf, K=K)

#     # Save all results
#     cv2.imwrite(os.path.join(OUTDIR, "L.png"), L)
#     cv2.imwrite(os.path.join(OUTDIR, "L_b_blurred.png"), L_b)
#     cv2.imwrite(os.path.join(OUTDIR, "L_inv_inverse.png"), L_inv)
#     cv2.imwrite(os.path.join(OUTDIR, "L_wiener.png"), L_wi)

#     print(f"[OK] Wrote results to: {OUTDIR}")
#     print("Tip: If you see ringing/noise, try increasing K (Wiener) to 0.002–0.005, or EPS to 0.002.")

# if __name__ == "__main__":
#     main()





###############################################################################################################################################################################
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------










import os, glob
import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

# ---- SETTINGS ----
PREFERRED_NAME = "L_input.jpg"   # updated preferred filename
SIGMA = 2.0                      # updated blur strength
KERNEL_SIZE = 13                # updated kernel (odd; ~6*SIGMA+1)
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
