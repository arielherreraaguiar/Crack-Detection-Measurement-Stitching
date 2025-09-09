import os
import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

"""
Batch process a folder of images:
- Canny edges + centroid band filter
- Tip coordinates and total crack length
- Writes results to a txt file
- Optional: save per-image figures (edges + polyline) into outputs/plots/
"""

# Configuration
PATH = "C:/path/to/images/"  # <-- update
OUT_TXT = "C:/path/to/results/crack_growing.txt"  # <-- update
SCALE_PX_PER_UM = 2.134
SAVE_PLOTS = True
SAVE_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'plots')
os.makedirs(SAVE_DIR, exist_ok=True)

files = sorted([f for f in os.listdir(PATH) if f.lower().endswith(('.png','.jpg','.jpeg','.tif','.tiff'))],
               key=lambda x: os.path.getmtime(os.path.join(PATH, x)))

with open(OUT_TXT, 'w') as doc:
    for fname in files:
        fn = os.path.join(PATH, fname)
        img = cv.imread(fn, cv.IMREAD_GRAYSCALE)
        if img is None:
            print("Skip (not an image):", fn)
            continue

        # Edges
        edges = cv.Canny(cv.blur(img,(5,5)), 10, 200, apertureSize=3, L2gradient=True)
        ys, xs = np.where(edges != 0)
        if len(xs) == 0:
            doc.write("0 0 0\n")
            continue

        # Band around centroid (vertical)
        pts = np.column_stack((xs, ys))
        cx = np.mean(xs)
        band = 100
        sel = pts[np.abs(pts[:,0] - cx) <= band]
        fx, fy = sel[:,0], sel[:,1]

        # Tip (x,y)
        y_min, y_max = fy.min(), fy.max()
        x_min, x_max = fx[fy.argmin()], fx[fy.argmax()]
        tip_x_um = abs(x_max - x_min) / SCALE_PX_PER_UM
        tip_y_um = abs(y_max - y_min) / SCALE_PX_PER_UM

        # Polyline & length
        data = np.column_stack((fx, fy))
        x_m, y_u = [], []
        for v in np.unique(fy):
            col = data[data[:,1]==v][:,0]
            x_m.append(col.mean())
            y_u.append(v)
        length_px = 0.0
        for i in range(len(x_m)-1):
            dx = x_m[i+1]-x_m[i]; dy = y_u[i+1]-y_u[i]
            length_px += (dx*dx+dy*dy)**0.5
        length_um = length_px / SCALE_PX_PER_UM

        # Write result
        doc.write(f"{tip_x_um:.2f} {tip_y_um:.2f} {length_um:.2f}\n")

        # Save plots
        if SAVE_PLOTS:
            base = os.path.splitext(os.path.basename(fname))[0]
            # (A) Edges overlay
            plt.figure()
            plt.imshow(img, cmap='gray')
            plt.scatter(xs, ys, s=0.05)
            plt.title(f'Edges overlay: {base}')
            plt.axis('off')
            plt.tight_layout()
            plt.savefig(os.path.join(SAVE_DIR, f"{base}_edges.png"), dpi=200)
            plt.close()

            # (B) Polyline overlay
            plt.figure()
            plt.imshow(img, cmap='gray')
            plt.plot(x_m, y_u, linewidth=1.0)
            plt.title(f'Crack polyline: {base}')
            plt.axis('off')
            plt.tight_layout()
            plt.savefig(os.path.join(SAVE_DIR, f"{base}_polyline.png"), dpi=200)
            plt.close()
