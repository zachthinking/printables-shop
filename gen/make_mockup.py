#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pymupdf>=1.24", "pillow>=10.0"]
# ///
"""生成 Etsy/Gumroad 主图：把 bundle 内产品首页渲染后拼成一张浅色场景图。

用法: uv run gen/make_mockup.py --bundle minimalist|meal
要点：sheet 用 RGBA + 透明填充旋转，阴影从 alpha 通道生成，避免黑边。
"""
import argparse
import os
import pymupdf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

DIST = os.path.join(os.path.dirname(__file__), "..", "dist")

BUNDLES = {
    "minimalist": {
        "names": ["daily-planner", "weekly-planner", "habit-tracker", "monthly-budget", "focus-session"],
        "title": "MINIMALIST PLANNER BUNDLE",
        "sub": "5 Printable Templates  ·  A4 + US Letter  ·  Instant Download",
        "bg": (247, 244, 238),
        "out": "mockup-main.png",
    },
    "meal": {
        "names": ["weekly-meal-planner", "grocery-list", "recipe-card", "fridge-pantry-inventory"],
        "title": "MEAL PLANNER BUNDLE",
        "sub": "4 Printable Templates  ·  A4 + US Letter  ·  Instant Download",
        "bg": (238, 243, 236),
        "out": "mockup-meal.png",
    },
}

W, H = 2400, 1800

# (中心x比例, 中心y比例, 旋转角度, 高度占画布比例)
# 扇形排开，全部位于标题文字下方；按张数选布局
LAYOUTS = {
    5: ([(0.145, 0.60, -8, 0.54),
         (0.315, 0.62, -4, 0.58),
         (0.50, 0.64, 0, 0.63),
         (0.685, 0.62, 4, 0.58),
         (0.855, 0.60, 8, 0.54)],
        [0, 4, 1, 3, 2]),
    4: ([(0.17, 0.60, -7, 0.56),
         (0.39, 0.62, -2, 0.61),
         (0.61, 0.62, 2, 0.61),
         (0.83, 0.60, 7, 0.56)],
        [0, 3, 1, 2]),
}


def render_pdf(name):
    doc = pymupdf.open(os.path.join(DIST, f"{name}-A4.pdf"))
    pix = doc[0].get_pixmap(dpi=110)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    border = 14
    framed = Image.new("RGB", (img.width + border * 2, img.height + border * 2), (255, 255, 255))
    framed.paste(img, (border, border))
    return framed.convert("RGBA")


def paste_with_shadow(canvas_img, sheet, cx, cy, angle, target_h):
    ratio = target_h / sheet.height
    sheet = sheet.resize((int(sheet.width * ratio), target_h), Image.LANCZOS)
    sheet = sheet.rotate(angle, expand=True, resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0))

    # 阴影：取 alpha 通道涂黑再模糊
    alpha = sheet.split()[3]
    shadow = Image.new("RGBA", sheet.size, (0, 0, 0, 0))
    shadow.putalpha(alpha.point(lambda a: int(a * 0.28)))
    black = Image.new("RGBA", sheet.size, (30, 30, 30, 255))
    black.putalpha(shadow.split()[3])
    shadow = black.filter(ImageFilter.GaussianBlur(16))

    x = int(cx - sheet.width / 2)
    y = int(cy - sheet.height / 2)
    canvas_img.paste(shadow, (x + 10, y + 18), shadow)
    canvas_img.paste(sheet, (x, y), sheet)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", choices=sorted(BUNDLES), default="minimalist")
    args = ap.parse_args()
    cfg = BUNDLES[args.bundle]
    out = os.path.join(os.path.dirname(__file__), "..", "listings", cfg["out"])
    layout, order = LAYOUTS[len(cfg["names"])]

    img = Image.new("RGBA", (W, H), cfg["bg"] + (255,))
    sheets = [render_pdf(n) for n in cfg["names"]]

    for i in order:
        fx, fy, ang, fh = layout[i]
        paste_with_shadow(img, sheets[i], W * fx, H * fy, ang, int(H * fh))

    draw = ImageDraw.Draw(img)
    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 88)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
    except OSError:
        font_big = ImageFont.load_default()
        font_small = font_big
    tw = draw.textlength(cfg["title"], font=font_big)
    draw.text(((W - tw) / 2, 110), cfg["title"], fill=(40, 40, 40), font=font_big)
    sw = draw.textlength(cfg["sub"], font=font_small)
    draw.text(((W - sw) / 2, 230), cfg["sub"], fill=(120, 115, 105), font=font_small)

    os.makedirs(os.path.dirname(out), exist_ok=True)
    img.convert("RGB").save(out, quality=92)
    print(f"✓ {out}")


if __name__ == "__main__":
    main()
