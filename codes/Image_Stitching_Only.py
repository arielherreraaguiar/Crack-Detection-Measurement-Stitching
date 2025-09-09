import os, time, cv2
from stitching import Stitcher

"""
Stitch all images in a folder using the Open Stitching library.
Keep plane warper + no wave correction + no crop to preserve scale.
"""

path = "C:/path/to/stitch/"
imgs = [os.path.join(path,f) for f in os.listdir(path) if f.lower().endswith(('.png','.jpg','.jpeg'))]
imgs.sort(key=lambda x: os.path.getmtime(x))
stitcher = Stitcher(nfeatures=1000, wave_correct_kind='no', warper_type='plane', crop=False)
t0 = time.time()
panorama = stitcher.stitch(imgs)
cv2.imwrite(os.path.join(path,'results.png'), panorama)
print("Time (min):", (time.time()-t0)/60)