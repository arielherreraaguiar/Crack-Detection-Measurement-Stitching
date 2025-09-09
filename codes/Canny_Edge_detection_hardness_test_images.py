import os
import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

"""
Detect up to four cracks on a hardness-test image:
- Estimate scale from a green reference line (100 µm)
- Mask indentation area to avoid false edges
- Canny edges + centroid-bands (N/S/E/W) and lengths
- Saves Matplotlib figures (edges + polylines) into outputs/plots/
"""

# Configuration
FILE = '02_Images_For_Test/hardness_cracks.jpg'   # <-- update
SAVE_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'plots')
os.makedirs(SAVE_DIR, exist_ok=True)

def measure_green_line(file):
    image = cv.imread(file)
    if image is None:
        return None
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    lower, upper = np.array([50,100,100]), np.array([70,255,255])
    mask = cv.inRange(hsv, lower, upper)
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if not contours: return None
    c = max(contours, key=lambda cnt: cv.arcLength(cnt, False))
    x,y,w,h = cv.boundingRect(c)
    scale_px_per_um = w / 100.0  # assume 100 µm reference line
    return scale_px_per_um

# Scale
scale = measure_green_line(FILE) or 1.0

# Load & mask indentation (circle)
img = cv.imread(FILE, cv.IMREAD_GRAYSCALE)
if img is None:
    raise FileNotFoundError(f"Image not found: {FILE}")
h,w = img.shape
mask = np.zeros_like(img)
cv.circle(mask, (w//2, h//2), 129, (255,255,255), -1)  # adjust radius as needed
mask = cv.bitwise_not(mask)
img_masked = cv.bitwise_and(img, img, mask=mask)

# Edges
edges = cv.Canny(cv.blur(img_masked,(5,5)), 10, 200, apertureSize=3, L2gradient=True)
ys, xs = np.where(edges != 0)
pts = np.column_stack((xs, ys))

# Helper to compute polyline length along preferred axis
def polyline_length(pts, axis=0, band=10):
    c = np.mean(pts[:,axis])
    sel = pts[np.abs(pts[:,axis] - c) <= band]
    a, b = (sel[:,0], sel[:,1]) if axis==0 else (sel[:,1], sel[:,0])
    data = np.column_stack((a,b))
    x_m, y_u = [], []
    for v in np.unique(b):
        col = data[data[:,1]==v][:,0]
        if len(col)==0: continue
        x_m.append(col.mean()); y_u.append(v)
    length_px = 0.0
    for i in range(len(x_m)-1):
        dx = x_m[i+1]-x_m[i]; dy = y_u[i+1]-y_u[i]
        length_px += (dx*dx+dy*dy)**0.5
    return (x_m, y_u, length_px/scale if scale>0 else length_px)

# Compute N/S and E/W polylines
xm_ns, yu_ns, len_ns_um = polyline_length(pts, axis=0, band=10)
xm_ew, yu_ew, len_ew_um = polyline_length(pts, axis=1, band=10)

print("Radial length (N/S) [µm]:", round(len_ns_um,2))
print("Radial length (E/W) [µm]:", round(len_ew_um,2))

# ---- Matplotlib figures ----
# (A) Edges overlay
plt.figure()
plt.imshow(img_masked, cmap='gray')
plt.scatter(xs, ys, s=0.05)
plt.title('Hardness test: edges overlay')
plt.axis('off')
plt.tight_layout()
plt.savefig(os.path.join(SAVE_DIR, 'hardness_edges_overlay.png'), dpi=200)

# (B) Polylines overlay (N/S in red, E/W in blue)
plt.figure()
plt.imshow(img_masked, cmap='gray')
if xm_ns and yu_ns:
    plt.plot(xm_ns, yu_ns, linewidth=1.0, label='N/S polyline')
if xm_ew and yu_ew:
    # to overlay correctly, swap axes: polyline_length(axis=1) returns (x along Y, Y unique)
    plt.plot(xm_ew, yu_ew, linewidth=1.0, label='E/W polyline')
plt.legend(loc='lower right', fontsize=8)
plt.title('Hardness test: radial polylines')
plt.axis('off')
plt.tight_layout()
plt.savefig(os.path.join(SAVE_DIR, 'hardness_polylines.png'), dpi=200)
