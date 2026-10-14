import atexit
import os
import shutil
import tempfile
import time
from PIL import Image, ImageGrab, ImageOps
import customtkinter as ctk

clipdir = tempfile.mkdtemp(prefix=f"pinbatch_img_{os.getpid()}_")
atexit.register(shutil.rmtree, clipdir, True)

def makethumb(path, size=(160, 160)):
    try:
        im = Image.open(path)
        im = ImageOps.exif_transpose(im)
        im.thumbnail(size, Image.Resampling.LANCZOS)
        return ctk.CTkImage(light_image=im, dark_image=im, size=im.size)
    except Exception:
        return None

def getclip():
    try:
        data = ImageGrab.grabclipboard()
    except Exception:
        return []

    if isinstance(data, Image.Image):
        dest = os.path.join(clipdir, f"clip_{int(time.time() * 1000)}.png")
        data.save(dest, "PNG")
        return [dest]

    if isinstance(data, list):
        return [p for p in data if os.path.isfile(p)]

    return []
