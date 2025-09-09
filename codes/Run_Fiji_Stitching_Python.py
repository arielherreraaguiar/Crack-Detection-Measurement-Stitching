from ij import IJ
import os

"""
Pairwise stitching through Fiji/ImageJ from Python (Jython).
Iteratively fuses consecutive pairs until one image remains.
"""

image_directory = "C:/path/to/images/"
files = sorted([f for f in os.listdir(image_directory) if f.lower().endswith(('png','jpg','jpeg','tiff'))],
               key=lambda x: os.path.getmtime(os.path.join(image_directory,x)))
if len(files)<2: raise SystemExit("Need at least two images.")

i=1
while len(files)>1:
    img1 = os.path.join(image_directory, files[0])
    img2 = os.path.join(image_directory, files[1])
    imp1, imp2 = IJ.openImage(img1), IJ.openImage(img2)
    if imp1 is None or imp2 is None: break
    out_name = f"stitched_{i}.png"; out_path = os.path.join(image_directory,out_name)
    IJ.run("Pairwise stitching",
           f"first_image={img1} second_image={img2} fusion_method=[Linear Blending] "
           f"fused_image={out_path} check_peaks=5 compute_overlap=True "
           f"registration_channel_image_1=[Average all channels] "
           f"registration_channel_image_2=[Average all channels]")
    IJ.saveAs("PNG", out_path)
    imp1.close(); imp2.close()
    files = [out_name] + files[2:]
    i+=1