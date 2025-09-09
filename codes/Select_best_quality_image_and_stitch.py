import os, cv2, numpy as np, shutil, pandas as pd, time
from stitching import Stitcher
from skimage.metrics import structural_similarity as ssim

"""
Read a list of directories from Excel, pick the sharpest image (edge count) in each,
remove near-duplicates (SSIM), and stitch the selected set (Open Stitching).
"""

def edge_count(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    e = cv2.Canny(cv2.blur(img,(5,5)),10,150,apertureSize=3,L2gradient=True)
    return int(np.count_nonzero(e))

def best_image_in_dir(d):
    cands = [os.path.join(d,f) for f in os.listdir(d) if f.lower().endswith(('.png','.jpg','.jpeg'))]
    if not cands: return None
    cands.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    cands = cands[:4]
    return max(cands, key=edge_count)

def remove_similar_images(folder, thr=0.9, max_images=30):
    files = [os.path.join(folder,f) for f in os.listdir(folder) if f.lower().endswith(('.png','.jpg','.jpeg'))]
    files.sort(key=os.path.getmtime)
    uniq=[]
    def prep(p): return cv2.cvtColor(cv2.resize(cv2.imread(p),(300,300)), cv2.COLOR_BGR2GRAY)
    for f in files:
        imgf = prep(f); keep=True
        for u in uniq:
            if ssim(imgf, prep(u))>thr: keep=False; break
        if keep: uniq.append(f)
        if len(uniq)>=max_images: break
    for f in files:
        if f not in uniq:
            try: os.remove(f)
            except: pass

# Example Excel-driven selection (adapt paths/sheet/range)
excel_file = r"C:/path/to/calculations.xlsx"
sheet = "CTE50M-6"
# User picks a column/range; here we assume a single column of folder IDs:
# df = pd.read_excel(excel_file, sheet_name=sheet, usecols='F', skiprows=227, nrows=93, dtype=str)
# directory_numbers = df.iloc[::3, 0].dropna().tolist()

# Example:
directory_numbers = ["001","002"]  # <- replace with values from your Excel
main_dir = r"D:/path/to/main/folder"
stitching_dir = r"C:/path/to/stitching"
os.makedirs(stitching_dir, exist_ok=True)

# Collect best images
for num in directory_numbers:
    d = os.path.join(main_dir, f"Images Test{num}")
    bi = best_image_in_dir(d)
    if bi: shutil.copy(bi, stitching_dir)

# Remove duplicates, then stitch
remove_similar_images(stitching_dir)
imgs = [os.path.join(stitching_dir,f) for f in os.listdir(stitching_dir) if f.lower().endswith(('.png','.jpg','.jpeg'))]
imgs.sort(key=os.path.getmtime)
stitcher = Stitcher(nfeatures=1000, wave_correct_kind='no', warper_type='plane', crop=False)
panorama = stitcher.stitch(imgs)
cv2.imwrite(os.path.join(stitching_dir,'results_panorama.png'), panorama)