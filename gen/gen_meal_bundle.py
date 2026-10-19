#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["reportlab>=4.0"]
# ///
"""生成 Meal Planner Bundle：4 个可打印 PDF，各出 A4 + US Letter 双尺寸。

输出到 ../dist/。复用 gen_planners 的绘制 helper 与风格。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_planners import (OUT_DIR, INK, LINE, FAINT, ACCENT, SIZES,
                          new_canvas, title, section_label, hline, rounded_box)


# ---------------------------------------------------------------- 1. 周餐单

def weekly_meal_planner(c, w, h):
    m = 42
    top = title(c, "Weekly Meal Planner", w, h, m)
    y = top - 24

    c.setFont("Helvetica", 9)
    c.setFillColor(ACCENT)
    c.drawString(m, y, "WEEK OF")
    hline(c, m + 52, m + 200, y - 2, LINE, 0.6)
    y -= 24

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    meals = ["Breakfast", "Lunch", "Dinner"]
    label_w = 64
    col_w = (w - 2 * m - label_w) / 7
    avail_h = y - m - 44
    row_h = avail_h / 3

    # 日期表头
    for i, day in enumerate(days):
        c.setFont("Helvetica-Bold", 6.5)
        c.setFillColor(ACCENT)
        c.drawCentredString(m + label_w + i * col_w + col_w / 2, y, day.upper())
    y -= 8
    hline(c, m, w - m, y, LINE, 0.6)

    for r, meal in enumerate(meals):
        yy = y - r * row_h
        section_label(c, m, yy - row_h / 2, meal)
        for i in range(7):
            x = m + label_w + i * col_w
            c.setStrokeColor(FAINT)
            c.setLineWidth(0.5)
            c.rect(x + 2, yy - row_h + 6, col_w - 4, row_h - 10)
        hline(c, m, w - m, yy - row_h, FAINT, 0.5)

    section_label(c, m, m + 26, "Notes / prep ahead")
    hline(c, m + 105, w - m, m + 24, FAINT, 0.5)


# ---------------------------------------------------------------- 2. 购物清单

def grocery_list(c, w, h):
    m = 42
    top = title(c, "Grocery List", w, h, m)
    y = top - 24

    c.setFont("Helvetica", 9)
    c.setFillColor(ACCENT)
    c.drawString(m, y, "STORE")
    hline(c, m + 36, m + 180, y - 2, LINE, 0.6)
    c.drawString(m + 200, y, "DATE")
    hline(c, m + 228, m + 330, y - 2, LINE, 0.6)
    y -= 26

    cats = ["Produce", "Dairy & Eggs", "Meat & Fish", "Pantry", "Frozen", "Household", "Other"]
    col_w = (w - 2 * m - 16) / 2
    x_cols = [m, m + col_w + 16]
    y_bottom = m + 20

    # 每栏顺序放若干分类，每类 9 行
    per_col = [cats[:4], cats[4:]]
    for col, col_cats in enumerate(per_col):
        x = x_cols[col]
        yy = y
        for cat in col_cats:
            section_label(c, x, yy, cat)
            yy -= 6
            hline(c, x, x + col_w, yy, LINE, 0.5)
            for _ in range(9):
                yy -= 19
                c.setStrokeColor(LINE)
                c.setLineWidth(0.6)
                c.rect(x, yy + 3, 8, 8)
                hline(c, x + 13, x + col_w, yy + 6, FAINT, 0.5)
            yy -= 14
            if yy < y_bottom + 20:
                break


# ---------------------------------------------------------------- 3. 食谱卡

def recipe_card(c, w, h):
    m = 42
    top = title(c, "Recipe Card", w, h, m)
    y = top - 26

    c.setFont("Helvetica", 9)
    c.setFillColor(ACCENT)
    c.drawString(m, y, "RECIPE NAME")
    hline(c, m + 76, w - m, y - 2, LINE, 0.6)
    y -= 24

    # 信息条：prep / cook / servings / rating
    labels = ["PREP TIME", "COOK TIME", "SERVINGS", "RATING"]
    bw = (w - 2 * m - 3 * 14) / 4
    for i, lab in enumerate(labels):
        x = m + i * (bw + 14)
        rounded_box(c, x, y - 30, bw, 30, LINE, 0.7, 3)
        c.setFont("Helvetica-Bold", 6)
        c.setFillColor(ACCENT)
        c.drawCentredString(x + bw / 2, y - 11, lab)
    y -= 48

    col_w = (w - 2 * m - 20) * 0.38
    x_ing, x_dir = m, m + col_w + 20

    section_label(c, x_ing, y, "Ingredients")
    section_label(c, x_dir, y, "Directions")
    y -= 12

    ing_rows = 16
    area_h = y - m - 60
    step = area_h / ing_rows
    yy = y
    for _ in range(ing_rows):
        hline(c, x_ing, x_ing + col_w, yy - step + 5, FAINT, 0.5)
        yy -= step

    yy = y
    for i in range(ing_rows):
        c.setFont("Helvetica", 7)
        c.setFillColor(ACCENT)
        c.drawString(x_dir, yy - step + 8, f"{i + 1:02d}")
        hline(c, x_dir + 18, w - m, yy - step + 5, FAINT, 0.5)
        yy -= step

    section_label(c, m, m + 42, "Notes / source")
    hline(c, m + 78, w - m, m + 40, FAINT, 0.5)
    hline(c, m, w - m, m + 22, FAINT, 0.5)


# ---------------------------------------------------------------- 4. 冰箱/食品柜库存

def inventory_sheet(c, w, h):
    m = 42
    top = title(c, "Fridge & Pantry Inventory", w, h, m)
    y = top - 24

    c.setFont("Helvetica", 9)
    c.setFillColor(ACCENT)
    c.drawString(m, y, "DATE")
    hline(c, m + 28, m + 140, y - 2, LINE, 0.6)
    y -= 26

    col_w = (w - 2 * m - 20) / 2
    x_l, x_r = m, m + col_w + 20
    cols = ["Item", "Qty", "Expires"]

    for x, label in [(x_l, "Fridge & Freezer"), (x_r, "Pantry")]:
        section_label(c, x, y, label)
        yy = y - 14
        cw = [col_w * 0.52, col_w * 0.2, col_w * 0.28]
        for i, cname in enumerate(cols):
            c.setFont("Helvetica-Bold", 6.5)
            c.setFillColor(ACCENT)
            c.drawString(x + sum(cw[:i]) + 2, yy, cname.upper())
        yy -= 6
        hline(c, x, x + col_w, yy, LINE, 0.6)
        rows = int((yy - m - 16) / 19)
        for _ in range(rows):
            yy -= 19
            hline(c, x, x + col_w, yy, FAINT, 0.5)
            xx = x
            for wdt in cw[:-1]:
                xx += wdt
                c.setStrokeColor(FAINT)
                c.setLineWidth(0.4)
                c.line(xx, yy, xx, yy + 19)


PRODUCTS = {
    "weekly-meal-planner": weekly_meal_planner,
    "grocery-list": grocery_list,
    "recipe-card": recipe_card,
    "fridge-pantry-inventory": inventory_sheet,
}


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, fn in PRODUCTS.items():
        for size_name, pagesize in SIZES.items():
            w, h = pagesize
            path = os.path.join(OUT_DIR, f"{name}-{size_name}.pdf")
            c = new_canvas(path, pagesize)
            fn(c, w, h)
            c.showPage()
            c.save()
            print(f"✓ {path}")


if __name__ == "__main__":
    main()
