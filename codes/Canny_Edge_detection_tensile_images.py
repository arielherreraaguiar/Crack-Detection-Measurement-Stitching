import numpy as np, cv2 as cv
from matplotlib import pyplot as plt

"""
Detect a (small/large) crack on a tensile-test image:
- Optional notch-based scale estimation (e.g., 500 µm)
- Canny edges + centroid filter
- Tip coordinates and total length
"""

file = '02_Images_For_Test/saved_pypylon_img_368_20231218_091619_883.png'
img = cv.imread(file, cv.IMREAD_GRAYSCALE)
scale = 2.134  # pixels/µm (fallback)

edges = cv.Canny(img,10,200)
edges_blur = cv.Canny(cv.blur(img,(5,5)),10,200,apertureSize=3,L2gradient=True)

ys,xs = np.where(edges_blur!=0)
pts = np.column_stack((xs,ys))
cx = np.mean(xs)
sel = pts[np.abs(pts[:,0]-cx)<=100]
fx,fy = sel[:,0], sel[:,1]

ymin,ymax = fy.min(), fy.max()
xmin,xmax = fx[fy.argmin()], fx[fy.argmax()]
tip = (abs(xmax-xmin)/scale, abs(ymax-ymin)/scale)

data = np.column_stack((fx,fy))
x_m,y_u=[],[]
for v in np.unique(fy):
    col = data[data[:,1]==v][:,0]
    x_m.append(col.mean()); y_u.append(v)

length = 0.0
for i in range(len(x_m)-1):
    dx = x_m[i+1]-x_m[i]; dy = y_u[i+1]-y_u[i]
    length += (dx*dx+dy*dy)**0.5
print("Crack tip (x,y) µm:", (round(tip[0],2), round(tip[1],2)))
print("Total crack length (µm):", round(length/scale,2))