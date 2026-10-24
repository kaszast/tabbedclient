import os
import gi
gi.require_version('Rsvg', '2.0')
from gi.repository import Rsvg
import cairo
from PIL import Image

BASE_DIR = "/home/maci/antigravity/tabbetclient"
SVG_SRC = os.path.join(BASE_DIR, "resources", "icons", "design-5.svg")
ICONS_DIR = os.path.join(BASE_DIR, "src-tauri", "icons")
os.makedirs(ICONS_DIR, exist_ok=True)

with open(SVG_SRC, "r", encoding="utf-8") as f:
    svg_data = f.read()

handle = Rsvg.Handle.new_from_data(svg_data.encode("utf-8"))

SIZES = [16, 24, 32, 48, 64, 128, 256, 512]
pil_images = []

for size in SIZES:
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
    ctx = cairo.Context(surf)
    scale = float(size) / 512.0
    ctx.scale(scale, scale)
    handle.render_cairo(ctx)

    out_name = f"{size}x{size}.png" if size != 512 else "icon.png"
    out_path = os.path.join(ICONS_DIR, out_name)
    surf.write_to_png(out_path)
    print(f"✓ Saved: {out_path} ({size}x{size})")

    # PIL Image for multi-size ICO
    pil_img = Image.open(out_path).convert("RGBA")
    pil_images.append(pil_img)

# Windows .ico generálás több mérettel
ico_path = os.path.join(ICONS_DIR, "icon.ico")
pil_images[-1].save(
    ico_path,
    format="ICO",
    sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
)
print(f"✓ Saved Windows ICO: {ico_path}")

# Hivatalos SVG és másolatok elhelyezése
app_svg_path = os.path.join(ICONS_DIR, "icon.svg")
with open(app_svg_path, "w", encoding="utf-8") as f:
    f.write(svg_data)
with open(os.path.join(ICONS_DIR, "tabbedclient.svg"), "w", encoding="utf-8") as f:
    f.write(svg_data)

# Szabványos tabbedclient.png és tabbedclient-tray.png másolatok
import shutil
shutil.copy2(os.path.join(ICONS_DIR, "icon.png"), os.path.join(ICONS_DIR, "tabbedclient.png"))
shutil.copy2(os.path.join(ICONS_DIR, "32x32.png"), os.path.join(ICONS_DIR, "tabbedclient-tray.png"))
print(f"✓ Saved App SVG: {app_svg_path}")
print(f"✓ Saved tabbedclient.png & tabbedclient-tray.png")
