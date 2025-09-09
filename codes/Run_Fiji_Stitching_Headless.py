import subprocess

"""
Run the Fiji stitching script headlessly.
Adapt 'fiji_path', 'fiji_script_path' and 'image_directory' to your machine.
"""

fiji_path = r"D:/Fiji.app/ImageJ-win64.exe"
fiji_script_path = r"C:/path/to/Run_Fiji_Stitching_Python.py"
image_directory = r"C:/path/to/images/"

cmd = [fiji_path,"--headless","--run",fiji_script_path,f"image_directory='{image_directory}'"]
res = subprocess.run(cmd, capture_output=True, text=True)
print("RC:", res.returncode)
print(res.stdout if res.returncode==0 else res.stderr)