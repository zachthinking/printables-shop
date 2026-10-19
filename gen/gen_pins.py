#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pymupdf>=1.24", "pillow>=10.0"]
# ///
"""批量生成 Pinterest pin 图（1000×1500，2:3）。

每个产品 2 个标题变体，输出到 ../listings/pins/。
背景浅色系：productivity 系列米白，meal 系列浅鼠尾草绿。
"""
import os
import pymupdf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

DIST = os.path.join(os.path.dirname(__file__), "..", "dist")
OUT = os.path.join(os.path.dirname(__file__), "..", "listings", "pins")

W, H = 1000, 1500
SHOP_URL = "zachmindset.gumroad.com"

# (产品, pin标题, 副标题, 背景色)
PINS = [
    # —— productivity bundle —— 米白
    ("daily-planner", "Daily Planner Printable", "Schedule · Priorities · To-Do", (247, 244, 238)),
    ("daily-planner", "Minimal Daily Planner PDF", "Plan Your Day in Minutes", (242, 239, 232)),
    ("weekly-planner", "Weekly Planner Printable", "7-Day Overview · Undated", (247, 244, 238)),
    ("weekly-planner", "Simple Weekly Planner", "See Your Whole Week at a Glance", (242, 239, 232)),
    ("habit-tracker", "Habit Tracker Printable", "14 Habits × 31 Days", (247, 244, 238)),
    ("habit-tracker", "Monthly Habit Tracker PDF", "Build Better Habits Daily", (242, 239, 232)),
    ("monthly-budget", "Budget Planner Printable", "Income · Expenses · Savings", (247, 244, 238)),
    ("monthly-budget", "Monthly Budget Template", "Take Control of Your Money", (242, 239, 232)),
    ("focus-session", "Focus Session Planner", "Pomodoro Task Tracker", (247, 244, 238)),
    ("focus-session", "Productivity Planner PDF", "Beat Distractions, Get Deep Work Done", (242, 239, 232)),
    # —— meal bundle —— 浅鼠尾草绿
    ("weekly-meal-planner", "Weekly Meal Planner", "Breakfast · Lunch · Dinner Grid", (238, 243, 236)),
    ("weekly-meal-planner", "Meal Planner Printable", "Plan a Week of Meals in 5 Minutes", (233, 239, 231)),
    ("grocery-list", "Grocery List Printable", "Organized by Store Section", (238, 243, 236)),
    ("grocery-list", "Printable Shopping List", "Never Forget an Item Again", (233, 239, 231)),
    ("recipe-card", "Recipe Card Printable", "Ingredients + Steps + Timing", (238, 243, 236)),
    ("recipe-card", "Minimal Recipe Card PDF", "Save Your Favorite Recipes", (233, 239, 231)),
    ("fridge-pantry-inventory", "Fridge Inventory Printable", "Stop Wasting Food", (238, 243, 236)),
    ("fridge-pantry-inventory", "Pantry Inventory Template", "Know What You Have, Buy What You Need", (233, 239, 231)),
]


def render_pdf(name):
    doc = pymupdf.open(os.path.join(DIST, f"{name}-A4.pdf"))
    pix = doc[0].get_pixmap(dpi=72)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    border = 10
    framed = Image.new("RGB", (img.width + border * 2, img.height + border * 2), (255, 255, 255))
    framed.paste(img, (border, border))
    return framed.convert("RGBA")


def fonts():
    base = "/usr/share/fonts/truetype/dejavu/"
    return (ImageFont.truetype(base + "DejaVuSans-Bold.ttf", 64),
            ImageFont.truetype(base + "DejaVuSans.ttf", 34),
            ImageFont.truetype(base + "DejaVuSans-Bold.ttf", 26),
            ImageFont.truetype(base + "DejaVuSans.ttf", 28))


def make_pin(sheet, title, sub, bg, out_path):
    img = Image.new("RGBA", (W, H), bg + (255,))
    f_big, f_sub, f_tag, f_url = fonts()
    draw = ImageDraw.Draw(img)

    # 顶部标签
    tag = "PRINTABLE · INSTANT DOWNLOAD"
    tw = draw.textlength(tag, font=f_tag)
    tx = (W - tw) / 2
    draw.rounded_rectangle([tx - 18, 70, tx + tw + 18, 112], 21,
                           outline=(120, 115, 105), width=2)
    draw.text((tx, 79), tag, fill=(110, 105, 95), font=f_tag)

    # 标题（可能两行：太长时从中间断行）
    words = title.split()
    if draw.textlength(title, font=f_big) > W - 120:
        mid = len(words) // 2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]
    else:
        lines = [title]
    ty = 160
    for line in lines:
        lw = draw.textlength(line, font=f_big)
        draw.text(((W - lw) / 2, ty), line, fill=(40, 40, 40), font=f_big)
        ty += 78

    # 副标题
    sw = draw.textlength(sub, font=f_sub)
    draw.text(((W - sw) / 2, ty + 8), sub, fill=(120, 115, 105), font=f_sub)

    # 产品图：下方居中，轻微旋转 + 阴影
    target_h = 830
    ratio = target_h / sheet.height
    sh = sheet.resize((int(sheet.width * ratio), target_h), Image.LANCZOS)
    sh = sh.rotate(-3, expand=True, resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0))
    alpha = sh.split()[3]
    shadow = Image.new("RGBA", sh.size, (30, 30, 30, 255))
    shadow.putalpha(alpha.point(lambda a: int(a * 0.25)))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    sx = int((W - sh.width) / 2)
    sy = H - sh.height - 150
    img.paste(shadow, (sx + 9, sy + 16), shadow)
    img.paste(sh, (sx, sy), sh)

    # 底部 URL
    uw = draw.textlength(SHOP_URL, font=f_url)
    draw.text(((W - uw) / 2, H - 84), SHOP_URL, fill=(140, 135, 125), font=f_url)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.convert("RGB").save(out_path, quality=92)


def main():
    cache = {}
    seen = {}
    for name, title, sub, bg in PINS:
        if name not in cache:
            cache[name] = render_pdf(name)
        seen[name] = seen.get(name, 0) + 1
        out = os.path.join(OUT, f"pin-{name}-{seen[name]}.png")
        make_pin(cache[name], title, sub, bg, out)
        print(f"✓ {out}")


if __name__ == "__main__":
    main()
