import os
import io
import base64
from PIL import Image
import customtkinter as ctk
from icon_b64 import (
    ICON_DELETE, ICON_PASTE, ICON_IMPORT, ICON_CLEAR, ICON_SEND,
    ICON_DOWN, ICON_DEVELOPER, ICON_SOURCE
)

colbg = "#000000"
colpanel = "#000000"
colpanel2 = "#08080a"
colfield = "#0c0c0e"
colline = "#222226"
collineactive = "#333338"
colbrand = "#e60023"
colbrandh = "#cc001f"
colgreen = "#30d158"
colred = "#ff453a"
colmuted = "#8e8e93"
coltext = "#ffffff"
colsub = "#aeaeb2"


def makelogo(size=(28, 28)):
    path = os.path.join(os.path.dirname(__file__), "images", "logo.png")
    if not os.path.exists(path):
        path = os.path.join(os.path.dirname(__file__), "logo.png")
    img = Image.open(path).convert("RGBA")
    return ctk.CTkImage(light_image=img, dark_image=img, size=size)

def makeicon(name, size=(16, 16)):
    path = os.path.join(os.path.dirname(__file__), "images", f"icon_{name}.png")
    if not os.path.exists(path):
        path = os.path.join(os.path.dirname(__file__), f"icon_{name}.png")
    if os.path.exists(path):
        img = Image.open(path).convert("RGBA")
    else:
        bmap = {
            "delete": ICON_DELETE,
            "paste": ICON_PASTE,
            "import": ICON_IMPORT,
            "clear": ICON_CLEAR,
            "send": ICON_SEND,
            "down": ICON_DOWN,
            "developer": ICON_DEVELOPER,
            "source": ICON_SOURCE
        }
        img = Image.open(io.BytesIO(base64.b64decode(bmap[name]))).convert("RGBA")
    return ctk.CTkImage(light_image=img, dark_image=img, size=size)
