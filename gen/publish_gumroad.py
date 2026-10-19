#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["requests>=2.31"]
# ///
"""一键上架 Gumroad：上传 zip → 创建产品 → 挂封面 → 发布。

用法:
    export GUMROAD_ACCESS_TOKEN=xxx
    # 境外 API + S3，大陆网络需代理：
    export https_proxy=http://172.16.97.12:1081
    uv run gen/publish_gumroad.py --cover-url https://<公网URL>/mockup-main.png

token 获取: Gumroad → Settings → Advanced → Create OAuth application →
Generate access token（勾 edit_products + view_sales）。
"""
import argparse
import os
import sys

import requests

API = "https://api.gumroad.com/v2"
HERE = os.path.dirname(__file__)
LISTINGS = os.path.join(HERE, "..", "listings")

NAME = "Minimalist Planner Bundle (5 Printable Templates, A4 + US Letter)"
PRICE_CENTS = 499
TAGS = ["printable planner", "planner bundle", "minimalist planner",
        "daily planner", "weekly planner", "habit tracker",
        "budget planner", "productivity", "instant download"]

DESCRIPTION = """
<p>Get organized with this clean, ink-friendly <strong>Minimalist Planner Bundle</strong> —
5 printable templates covering your day, week, month, habits, and budget.</p>

<p><strong>✦ What's included ✦</strong></p>
<ul>
<li><strong>Daily Planner</strong> — schedule (6:00–22:00), top 3 priorities, to-do list, water tracker, notes</li>
<li><strong>Weekly Planner</strong> — 7-day overview with notes section</li>
<li><strong>Habit Tracker</strong> — 14 habits × 31 days grid</li>
<li><strong>Monthly Budget</strong> — income, savings &amp; debt, fixed/variable expenses, monthly summary</li>
<li><strong>Focus Session</strong> — pomodoro-style task tracker with distraction parking lot</li>
</ul>

<p><strong>✦ Sizes ✦</strong><br>
Every template comes in BOTH A4 and US Letter (2 zip files, 10 PDFs total).
Undated — print as many copies as you need, forever.</p>

<p><strong>✦ How it works ✦</strong></p>
<ol>
<li>Download instantly after payment</li>
<li>Print at home or at a local print shop (ink-friendly design)</li>
<li>Also works in GoodNotes / Notability / any PDF annotation app</li>
</ol>

<p><strong>✦ Please note ✦</strong></p>
<ul>
<li>Digital download — no physical item will be shipped</li>
<li>For personal use only — not for resale or redistribution</li>
</ul>
"""

ZIPS = [
    os.path.join(LISTINGS, "minimalist-planner-bundle-A4.zip"),
    os.path.join(LISTINGS, "minimalist-planner-bundle-Letter.zip"),
]


def die(msg):
    sys.exit(f"✗ {msg}")


def call(method, url, **kw):
    r = requests.request(method, url, timeout=120, **kw)
    try:
        data = r.json()
    except ValueError:
        die(f"{url} 返回非 JSON（HTTP {r.status_code}）: {r.text[:300]}")
    if r.status_code >= 400 or data.get("success") is False:
        die(f"{url} 失败（HTTP {r.status_code}）: {data.get('message', data)}")
    return data


def upload_file(token, path):
    """四步上传: presign → PUT → complete → file_url"""
    size = os.path.getsize(path)
    filename = os.path.basename(path)
    pre = call("POST", f"{API}/files/presign",
               data={"access_token": token, "filename": filename, "file_size": size})
    upload_id, key = pre["upload_id"], pre["key"]
    parts = pre["parts"]

    etags = []
    with open(path, "rb") as f:
        for part in parts:
            body = f.read(100 * 1024 * 1024)
            r = requests.put(part["presigned_url"], data=body, timeout=300)
            r.raise_for_status()
            # S3 返回的 ETag 带引号，complete 端点要求原样回传
            etags.append((part["part_number"], r.headers["ETag"]))

    # 文档格式: parts[][part_number]=1, parts[][etag]="abc"（同名字段重复，用 tuple 列表）
    form = [("access_token", token), ("upload_id", upload_id), ("key", key)]
    for pn, etag in etags:
        form.append(("parts[][part_number]", str(pn)))
        form.append(("parts[][etag]", etag))
    done = call("POST", f"{API}/files/complete", data=form)
    file_url = done.get("file_url") or pre.get("file_url")
    print(f"  ✓ 上传 {filename} → {file_url[:80]}…")
    return file_url


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cover-url", help="主图的公网 URL（covers 端点只接受公开 URL）")
    ap.add_argument("--draft", action="store_true", help="创建为草稿而不是直接发布")
    args = ap.parse_args()

    token = os.environ.get("GUMROAD_ACCESS_TOKEN") or die(
        "缺少 GUMROAD_ACCESS_TOKEN 环境变量（见脚本顶部注释）")

    print("1/3 上传产品文件…")
    file_urls = [upload_file(token, z) for z in ZIPS]

    print("2/3 创建产品…")
    payload = [
        ("access_token", token),
        ("native_type", "digital"),
        ("name", NAME),
        ("price", str(PRICE_CENTS)),
        ("price_currency_type", "usd"),
        ("description", DESCRIPTION),
        ("custom_summary", "5 ink-friendly printable planner templates (daily/weekly/habits/budget/focus), A4 + US Letter, instant download."),
        ("custom_permalink", "minimalist-planner-bundle"),
    ]
    payload += [("tags[]", t) for t in TAGS]
    payload += [("files[][url]", u) for u in file_urls]
    if args.draft:
        payload["draft"] = "true"
    product = call("POST", f"{API}/products", data=payload)["product"]
    pid = product["id"]
    print(f"  ✓ 产品 ID: {pid}  published={product.get('published')}  {product.get('short_url', '')}")

    if args.cover_url:
        print("3/3 挂封面…")
        call("POST", f"{API}/products/{requests.utils.quote(pid, safe='')}/covers",
             data={"access_token": token, "url": args.cover_url})
        print(f"  ✓ 封面已设置: {args.cover_url}")
    else:
        print("3/3 跳过封面（未提供 --cover-url）")

    print("\n完成！")
    if not product.get("published"):
        print("⚠ 产品被存为草稿（通常是邮箱未确认或未设置收款方式），")
        print("  到 Gumroad 后台补齐后到产品页点 Publish，或运行 enable 端点。")


if __name__ == "__main__":
    main()
