import os
import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

"""
Detect a (small/large) crack on a tensile-test image:
- Optional notch-based scale estimation (e.g., 500 µm)
- Canny edges + centroid filter
- Tip coordinates and total length
- Saves Matplotlib figures (edges overlay, polyline overlay) into outputs/plots/
"""

# Configuration
FILE = '02_Images_For_Test/saved_pypylon_img_368_20231218_091619_883.png'  # <-- update
SCALE_PX_PER_UM = 2.134  # fallback scale (pixels per micron) if no notch reference
SAVE_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'plots')
os.makedirs(SAVE_DIR, exist_ok=True)

# Load image (grayscale)
img = cv.imread(FILE, cv.IMREAD_GRAYSCALE)
if img is None:
    raise FileNotFoundError(f"Image not found: {FILE}")

# Edge detection
edges_blur = cv.Canny(cv.blur(img,(5,5)), 10, 200, apertureSize=3, L2gradient=True)

# Select crack points around centroid (vertical band)
ys, xs = np.where(edges_blur != 0)
pts = np.column_stack((xs, ys))
cx = np.mean(xs)
band = 100  # tune: 50 (small cracks) to 100 (large cracks)
sel = pts[np.abs(pts[:,0] - cx) <= band]
fx, fy = sel[:,0], sel[:,1]

# Crack tip (x,y) using min/max in Y
ymin, ymax = fy.min(), fy.max()
xmin, xmax = fx[fy.argmin()], fx[fy.argmax()]
tip_x_um = abs(xmax - xmin) / SCALE_PX_PER_UM
tip_y_um = abs(ymax - ymin) / SCALE_PX_PER_UM

# Polyline along the crack (mean X per unique Y), length in µm
data = np.column_stack((fx, fy))
x_m, y_u = [], []
for v in np.unique(fy):
    col = data[data[:,1] == v][:,0]
    x_m.append(col.mean())
    y_u.append(v)

length_px = 0.0
for i in range(len(x_m)-1):
    dx = x_m[i+1] - x_m[i]
    dy = y_u[i+1] - y_u[i]
    length_px += (dx*dx + dy*dy)**0.5
length_um = length_px / SCALE_PX_PER_UM

print("Crack tip (x,y) [µm]:", (round(tip_x_um,2), round(tip_y_um,2)))
print("Total crack length [µm]:", round(length_um,2))

# ---- Matplotlib figures ----
# (A) Edges overlay
plt.figure()
plt.imshow(img, cmap='gray')
plt.scatter(xs, ys, s=0.05)
plt.title('Edges overlay (Canny)')
plt.axis('off')
plt.tight_layout()
plt.savefig(os.path.join(SAVE_DIR, 'tensile_edges_overlay.png'), dpi=200)
# plt.show()

# (B) Polyline overlay
plt.figure()
plt.imshow(img, cmap='gray')
plt.plot(x_m, y_u, linewidth=1.0)
plt.title('Crack polyline over image')
plt.axis('off')
plt.tight_layout()
plt.savefig(os.path.join(SAVE_DIR, 'tensile_crack_polyline.png'), dpi=200)
# plt.show()
