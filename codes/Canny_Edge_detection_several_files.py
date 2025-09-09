import numpy as np, os, cv2 as cv

"""
Batch process a folder of images:
- Canny edges + centroid band filter
- Tip coordinates and total crack length
- Writes results to a txt file
"""

path = "C:/path/to/images/"
out_txt = "C:/path/to/results/crack_growing.txt"
scale = 2.134  # pixels/µm

files = sorted([f for f in os.listdir(path)], key=lambda x: os.path.getmtime(os.path.join(path,x)))
with open(out_txt,'w') as doc:
    for f in files:
        fn = os.path.join(path,f)
        img = cv.imread(fn, cv.IMREAD_GRAYSCALE)
        edges = cv.Canny(cv.blur(img,(5,5)),10,200,apertureSize=3,L2gradient=True)
        ys,xs = np.where(edges!=0)
        if len(xs)==0: doc.write("0 0 0\n"); continue
        pts = np.column_stack((xs,ys))
        cx = np.mean(xs); band = 100
        sel = pts[np.abs(pts[:,0]-cx)<=band]
        fx, fy = sel[:,0], sel[:,1]
        y_min, y_max = fy.min(), fy.max()
        x_min, x_max = fx[fy.argmin()], fx[fy.argmax()]
        tip_y, tip_x = (y_max-y_min)/scale, abs(x_max-x_min)/scale
        data = np.column_stack((fx,fy))
        x_m, y_u = [], []
        for v in np.unique(fy):
            col = data[data[:,1]==v][:,0]
            x_m.append(col.mean()); y_u.append(v)
        length = 0.0
        for i in range(len(x_m)-1):
            dx = x_m[i+1]-x_m[i]; dy = y_u[i+1]-y_u[i]
            length += (dx*dx+dy*dy)**0.5
        doc.write(f"{tip_x:.2f} {tip_y:.2f} {length/scale:.2f}\n")