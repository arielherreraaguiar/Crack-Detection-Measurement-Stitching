import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

"""
Detect up to four cracks on a hardness-test image.
- Estimate scale from a green reference line (100 µm)
- Mask hardness impression (circular)
- Detect edges (Canny) and compute tips/length along N/S/E/W
"""

def measure_green_line(file):
    image = cv.imread(file); hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    lower, upper = np.array([50,100,100]), np.array([70,255,255])
    mask = cv.inRange(hsv, lower, upper)
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if not contours: return None
    c = max(contours, key=lambda cnt: cv.arcLength(cnt, False))
    x,y,w,h = cv.boundingRect(c)
    scale_pixel_um = w/100.0  # 100 µm reference
    rect = image.copy(); cv.rectangle(rect,(x,y),(x+w,y+h),(0,0,255),2)
    return scale_pixel_um, rect

file = '02_Images_For_Test/hardness_cracks.jpg'
res = measure_green_line(file); scale = res[0] if res else 1.0

img = cv.imread(file, cv.IMREAD_GRAYSCALE)
h,w = img.shape; mask = np.zeros_like(img)
cv.circle(mask,(w//2,h//2),129,(255,255,255),-1)
mask = cv.bitwise_not(mask); img = cv.bitwise_and(img,img,mask=mask)

edges = cv.Canny(cv.blur(img,(5,5)),10,200,apertureSize=3,L2gradient=True)
ys,xs = np.where(edges!=0); pts = np.column_stack((xs,ys))

def proj_length(pts, axis=0, band=10):
    centroid = np.mean(pts[:,axis])
    sel = pts[np.abs(pts[:,axis]-centroid)<=band]
    a,b = (sel[:,0], sel[:,1]) if axis==0 else (sel[:,1], sel[:,0])
    data = np.column_stack((a,b))
    length=0.0
    for v in np.unique(b):
        col = data[data[:,1]==v][:,0]
        if len(col)==0: continue
        meanx = np.mean(col)
        if 'path' not in locals(): path=[]
        path.append((meanx,v))
    for i in range(len(path)-1):
        dx = path[i+1][0]-path[i][0]; dy = path[i+1][1]-path[i][1]
        length += (dx*dx+dy*dy)**0.5
    return length/scale if scale>0 else length

north_south = proj_length(pts, axis=0, band=10)
east_west   = proj_length(pts, axis=1, band=10)

print("Crack length Y (µm):", round(north_south,2))
print("Crack length X (µm):", round(east_west,2))