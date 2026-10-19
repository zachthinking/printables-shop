#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["reportlab>=4.0"]
# ///
"""生成 Minimalist Productivity Planner Bundle：5 个可打印 PDF，各出 A4 + US Letter 双尺寸。

输出到 ../dist/。设计风格：浅灰细线、大留白、省墨，适合家用打印机。
"""
import os
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "dist")

INK = HexColor("#222222")       # 正文墨色
LINE = HexColor("#BBBBBB")      # 分隔线
FAINT = HexColor("#DDDDDD")     # 最浅的线
ACCENT = HexColor("#7A7A7A")    # 次级文字

SIZES = {"A4": A4, "Letter": LETTER}


def new_canvas(path, pagesize):
    c = canvas.Canvas(path, pagesize=pagesize)
    c.setTitle(os.path.splitext(os.path.basename(path))[0])
    return c


def title(c, text, w, h, margin):
    """页首标题：小号大写 + 宽字距 + 下方细线。"""
    y = h - margin
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(margin, y, text.upper())
    # 手写字距
    c.setFont("Helvetica", 7.5)
    c.setFillColor(ACCENT)
    c.drawRightString(w - margin, y + 2, "MINIMALIST PLANNER")
    c.setStrokeColor(INK)
    c.setLineWidth(1.2)
    c.line(margin, y - 8, w - margin, y - 8)
    return y - 8


def section_label(c, x, y, text):
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(ACCENT)
    c.drawString(x, y, text.upper())


def hline(c, x1, x2, y, color=FAINT, width=0.5):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1, y, x2, y)


def rounded_box(c, x, y, w, h, color=LINE, width=0.7, r=3):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.roundRect(x, y, w, h, r)


# ---------------------------------------------------------------- 1. 日计划表

def daily_planner(c, w, h):
    m = 42
    top = title(c, "Daily Planner", w, h, m)
    y = top - 26

    # 日期 + 星期
    c.setFont("Helvetica", 9)
    c.setFillColor(ACCENT)
    c.drawString(m, y, "DATE")
    hline(c, m + 28, m + 150, y - 2, LINE, 0.6)
    c.drawString(m + 170, y, "DAY")
    hline(c, m + 195, w - m, y - 2, LINE, 0.6)
    y -= 30

    # Top 3 priorities
    section_label(c, m, y, "Top 3 Priorities")
    y -= 16
    for _ in range(3):
        c.setStrokeColor(LINE)
        c.setLineWidth(0.7)
        c.rect(m, y - 3, 9, 9)
        hline(c, m + 16, w - m, y, FAINT, 0.6)
        y -= 22
    y -= 10

    # 左：时间表 6:00-22:00；右：to-do + notes
    col_w = (w - 2 * m - 20) * 0.46
    x_time = m
    x_todo = m + col_w + 20

    section_label(c, x_time, y, "Schedule")
    section_label(c, x_todo, y, "To Do")
    y -= 14
    row_h = (y - m - 70) / 17  # 17 个时段
    y0 = y
    for i in range(17):
        hr = 6 + i
        label = f"{hr:02d}:00"
        c.setFont("Helvetica", 7)
        c.setFillColor(ACCENT)
        c.drawString(x_time, y - row_h + 4, label)
        hline(c, x_time + 28, x_time + col_w, y - row_h, FAINT, 0.5)
        y -= row_h
    hline(c, x_time + 28, x_time + col_w, y, FAINT, 0.5)

    y = y0
    for _ in range(17):
        c.setStrokeColor(LINE)
        c.setLineWidth(0.6)
        c.rect(x_todo, y - row_h + 2, 8, 8)
        hline(c, x_todo + 14, w - m, y - row_h + 6, FAINT, 0.5)
        y -= row_h

    # 底部：water + notes
    yb = m + 46
    section_label(c, m, yb, "Water")
    for i in range(8):
        c.setStrokeColor(LINE)
        c.setLineWidth(0.7)
        c.circle(m + 42 + i * 16, yb + 3, 5)
    section_label(c, m + 200, yb, "Notes")
    hline(c, m + 235, w - m, yb, FAINT, 0.5)
    hline(c, m, w - m, m + 26, FAINT, 0.5)


# ---------------------------------------------------------------- 2. 周计划表

def weekly_planner(c, w, h):
    m = 42
    top = title(c, "Weekly Planner", w, h, m)
    y = top - 24

    c.setFont("Helvetica", 9)
    c.setFillColor(ACCENT)
    c.drawString(m, y, "WEEK OF")
    hline(c, m + 52, m + 200, y - 2, LINE, 0.6)
    y -= 26

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    col_w = (w - 2 * m) / 7
    area_h = y - m - 60

    for i, day in enumerate(days):
        x = m + i * col_w
        section_label(c, x + 2, y, day)
        rounded_box(c, x, y - area_h - 14, col_w - 6, area_h + 8, FAINT, 0.6, 2)
        # 每列内横线
        yy = y - 34
        while yy > y - area_h - 4:
            hline(c, x + 5, x + col_w - 11, yy, FAINT, 0.4)
            yy -= 20

    yb = m + 36
    section_label(c, m, yb, "Notes & Next Week")
    hline(c, m, w - m, yb - 10, FAINT, 0.5)
    hline(c, m, w - m, yb - 26, FAINT, 0.5)


# ---------------------------------------------------------------- 3. 习惯追踪

def habit_tracker(c, w, h):
    m = 42
    top = title(c, "Habit Tracker", w, h, m)
    y = top - 24

    c.setFont("Helvetica", 9)
    c.setFillColor(ACCENT)
    c.drawString(m, y, "MONTH")
    hline(c, m + 40, m + 160, y - 2, LINE, 0.6)
    y -= 24

    rows, days = 14, 31
    name_w = 130
    grid_w = w - 2 * m - name_w
    cell = min(grid_w / days, 15)
    row_h = min((y - m - 20) / rows, 30)
    x0 = m + name_w

    # 日期表头
    c.setFont("Helvetica", 5.5)
    c.setFillColor(ACCENT)
    for d in range(days):
        c.drawCentredString(x0 + d * cell + cell / 2, y, str(d + 1))
    y -= 8

    for r in range(rows):
        yy = y - r * row_h
        hline(c, m, x0 - 8, yy - row_h / 2 + 3, FAINT, 0.5)
        for d in range(days):
            c.setStrokeColor(LINE)
            c.setLineWidth(0.5)
            c.rect(x0 + d * cell, yy - row_h + 5, cell - 2, row_h - 6)


# ---------------------------------------------------------------- 4. 月度预算

def budget_sheet(c, w, h):
    m = 42
    top = title(c, "Monthly Budget", w, h, m)
    y = top - 24

    c.setFont("Helvetica", 9)
    c.setFillColor(ACCENT)
    c.drawString(m, y, "MONTH")
    hline(c, m + 40, m + 160, y - 2, LINE, 0.6)
    y -= 28

    col_w = (w - 2 * m - 24) / 2
    x_l, x_r = m, m + col_w + 24

    def table(x, y, label, cols, nrows, row_h=20):
        section_label(c, x, y, label)
        y -= 14
        cw = col_w / len(cols)
        for i, cname in enumerate(cols):
            c.setFont("Helvetica-Bold", 6.5)
            c.setFillColor(ACCENT)
            c.drawString(x + i * cw + 2, y, cname.upper())
        y -= 6
        hline(c, x, x + col_w, y, LINE, 0.6)
        for _ in range(nrows):
            y -= row_h
            hline(c, x, x + col_w, y, FAINT, 0.5)
            for i in range(1, len(cols)):
                c.setStrokeColor(FAINT)
                c.setLineWidth(0.4)
                c.line(x + i * cw, y, x + i * cw, y + row_h)
        return y - 12

    yl = table(x_l, y, "Income", ["Source", "Expected", "Actual"], 5)
    yl = table(x_l, yl, "Savings & Debt", ["Item", "Planned", "Actual"], 4)

    yr = table(x_r, y, "Fixed Expenses", ["Item", "Planned", "Actual"], 6)
    yr = table(x_r, yr, "Variable Expenses", ["Item", "Planned", "Actual"], 8)

    # 汇总条
    ys = min(yl, yr) - 6
    section_label(c, m, ys, "Monthly Summary")
    ys -= 16
    labels = ["Total Income", "Total Expenses", "Total Saved", "Difference"]
    bw = (w - 2 * m - 3 * 14) / 4
    for i, lab in enumerate(labels):
        x = m + i * (bw + 14)
        rounded_box(c, x, ys - 34, bw, 34, LINE, 0.7, 3)
        c.setFont("Helvetica-Bold", 6)
        c.setFillColor(ACCENT)
        c.drawCentredString(x + bw / 2, ys - 12, lab.upper())


# ---------------------------------------------------------------- 5. 番茄专注表

def focus_sheet(c, w, h):
    m = 42
    top = title(c, "Focus Session", w, h, m)
    y = top - 26

    c.setFont("Helvetica", 9)
    c.setFillColor(ACCENT)
    c.drawString(m, y, "DATE")
    hline(c, m + 28, m + 140, y - 2, LINE, 0.6)
    c.drawString(m + 160, y, "GOAL FOR TODAY")
    hline(c, m + 250, w - m, y - 2, LINE, 0.6)
    y -= 30

    # 表头
    section_label(c, m, y, "Task")
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(ACCENT)
    cx = w - m - 150
    for i in range(5):
        c.drawCentredString(cx + i * 22, y, str(i + 1))
    c.drawRightString(w - m, y, "DONE")
    y -= 10
    hline(c, m, w - m, y, LINE, 0.6)

    rows = 10
    row_h = (y - m - 90) / rows
    for r in range(rows):
        yy = y - r * row_h
        hline(c, m, w - m, yy - row_h + 8, FAINT, 0.5)
        # 5 个番茄圈
        for i in range(5):
            c.setStrokeColor(LINE)
            c.setLineWidth(0.7)
            c.circle(cx + i * 22, yy - row_h / 2 + 4, 6)
        c.setStrokeColor(LINE)
        c.rect(w - m - 10, yy - row_h / 2 - 1, 9, 9)

    # 底部：干扰收集 + 复盘
    yb = m + 52
    section_label(c, m, yb, "Distraction Parking Lot")
    hline(c, m, w - m, yb - 10, FAINT, 0.5)
    hline(c, m, w - m, yb - 26, FAINT, 0.5)
    section_label(c, m, m + 16, "What worked / what to change")
    hline(c, m + 150, w - m, m + 14, FAINT, 0.5)


PRODUCTS = {
    "daily-planner": daily_planner,
    "weekly-planner": weekly_planner,
    "habit-tracker": habit_tracker,
    "monthly-budget": budget_sheet,
    "focus-session": focus_sheet,
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
