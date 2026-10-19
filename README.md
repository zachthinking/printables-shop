# printables-shop

AI 自动化赚钱试错项目 #1：可打印规划表（printables）数字产品店。
目标：一个月内验证能否出单，见钱加注，不见钱换方向。

## 当前状态（2026-10-19）

- [x] 5 个产品 PDF（A4 + US Letter 双尺寸，共 10 个文件）→ `dist/`
- [x] Etsy 主图 mockup（2400×1800）→ `listings/mockup-main.png`
- [x] 按尺寸打包 zip × 2 → `listings/*.zip`
- [x] 上架文案（Etsy 英文 / 闲鱼中文 / Gumroad 备用）→ `listings/listing-copy.md`
- [x] Gumroad 一键上架脚本 `gen/publish_gumroad.py`（上传 zip → 创建产品 → 挂封面 → 发布）
- [x] 主图公网 URL（Gumroad 封面用）：`https://raw.githubusercontent.com/zachthinking/printables-shop/main/listings/mockup-main.png`
- [x] 项目备份：GitHub `zachthinking/printables-shop`（公开）
- [ ] **上架（唯一待办，需 Zach 约 10 分钟）**：注册 Gumroad → 确认邮箱 → 绑 PayPal → Settings → Advanced 创建 OAuth application → 生成 token（勾 `edit_products` + `view_sales`）→ 把 token 发给 Claude
- [ ] 每个产品的单独预览图（Etsy 附图，可从 make_mockup.py 扩展）

## 产品线

| 产品 | 文件前缀 |
|------|----------|
| 日计划表 | daily-planner |
| 周计划表 | weekly-planner |
| 习惯追踪 | habit-tracker |
| 月度预算 | monthly-budget |
| 番茄专注表 | focus-session |

## 再生成

```bash
uv run gen/gen_planners.py   # 重新生成全部 PDF
uv run gen/make_mockup.py    # 重新生成主图
```

## 上架路径与阻塞点

1. **Gumroad**（主攻，Zach 有 PayPal）：注册后把 access token 给 Claude，运行：
   ```bash
   export GUMROAD_ACCESS_TOKEN=<token>
   export https_proxy=http://172.16.97.12:1081
   uv run gen/publish_gumroad.py --cover-url https://raw.githubusercontent.com/zachthinking/printables-shop/main/listings/mockup-main.png
   ```
2. **闲鱼**（国内备选）：手机 App 发布，文案在 listings/listing-copy.md。
3. **Etsy**：⚠️ 新店铺必须支持 Etsy Payments，**不面向中国大陆主体**——需要海外收款账户。暂放弃。

## 验证标准（一个月，至 2026-11-19）

- 出 ≥1 单 → 加注：扩品类（儿童练习题、婚礼/派对游戏、中文描红）、做 KDP 版本
- 零单 → 复盘流量来源，换方向（候选：自动化短视频账号、KDP 低内容书）

## 后续自动化构想（出单后做）

- 新品类生成脚本化（改参数出新模板）
- 定期自动渲染预览图、更新 listing
- 数据追踪：手动记录曝光/点击/出单
