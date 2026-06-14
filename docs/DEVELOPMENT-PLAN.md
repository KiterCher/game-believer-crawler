# GameBeliever Crawler 开发计划

> **日期**：2026-06-14
> **目标**：建立完整的 HSR 数据爬取系统，输出标准化数据供网站使用

---

## 一、项目架构

### 1.1 数据流架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    GameBeliever Crawler 数据流                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [1] 数据源                                                      │
│      ├── prydwen.gg (角色、光锥、遗器)                              │
│      ├── game8.co (攻略、材料)                                    │
│      └── 官方网站 (官方数据)                                       │
│                         ↓                                       │
│  [2] 爬虫层 (Crawler)                                            │
│      ├── HTTP 请求 + 限流                                        │
│      ├── HTML 解析                                               │
│      └── 缓存管理                                                │
│                         ↓                                       │
│  [3] 解析层 (Parser)                                             │
│      ├── 数据清洗                                                │
│      ├── 格式标准化                                              │
│      └── 数据校验                                                │
│                         ↓                                       │
│  [4] 存储层 (Storage)                                            │
│      ├── data/raw/          # 原始数据（HTML/JSON）               │
│      ├── data/processed/    # 处理后的标准数据                     │
│      └── data/images/       # 下载的图片文件                       │
│                         ↓                                       │
│  [5] 导出层 (Export)                                             │
│      ├── JSON 文件 → GameBeliever-web/src/data/                  │
│      └── 图片文件 → GameBeliever-web/public/images/              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、数据存储规划

### 2.1 目录结构

```
GameBeliever-crawler/
├── data/
│   ├── raw/                          # 原始数据
│   │   ├── html/                     # 原始 HTML 页面
│   │   │   ├── prydwen/
│   │   │   │   ├── characters/
│   │   │   │   ├── lightcones/
│   │   │   │   └── relics/
│   │   │   └── game8/
│   │   └── json/                     # 原始 JSON 数据
│   │       ├── prydwen/
│   │       └── game8/
│   │
│   ├── processed/                    # 处理后的数据
│   │   ├── characters/               # 角色数据
│   │   │   ├── kafka.json
│   │   │   ├── acheron.json
│   │   │   └── ...
│   │   ├── lightcones/               # 光锥数据
│   │   │   ├── patience-is-all-you-need.json
│   │   │   └── ...
│   │   ├── relics/                   # 遗器数据
│   │   │   ├── prisoner-in-deep-confinement.json
│   │   │   └── ...
│   │   └── materials/                # 材料数据
│   │       ├── trace-materials.json
│   │       └── ...
│   │
│   ├── images/                       # 图片文件
│   │   ├── characters/               # 角色图片
│   │   │   ├── kafka/
│   │   │   │   ├── avatar.png        # 头像
│   │   │   │   ├── splash.png        # 立绘
│   │   │   │   └── icon.png          # 小图标
│   │   │   ├── acheron/
│   │   │   └── ...
│   │   ├── lightcones/               # 光锥图片
│   │   │   ├── patience-is-all-you-need.png
│   │   │   └── ...
│   │   ├── relics/                   # 遗器图片
│   │   │   ├── prisoner/
│   │   │   │   ├── head.png
│   │   │   │   ├── hands.png
│   │   │   │   ├── body.png
│   │   │   │   └── feet.png
│   │   │   └── ...
│   │   ├── elements/                 # 属性图标
│   │   │   ├── physical.svg
│   │   │   ├── fire.svg
│   │   │   └── ...
│   │   └── paths/                    # 命途图标
│   │       ├── destruction.svg
│   │       ├── hunt.svg
│   │       └── ...
│   │
│   └── cache/                        # 缓存文件
│       └── ...
│
└── output/                           # 导出目录（临时）
    └── ...
```

### 2.2 数据格式规范

#### 角色数据 (characters/{slug}.json)

```json
{
  "id": "kafka",
  "name": "卡芙卡",
  "nameEn": "Kafka",
  "rarity": 5,
  "element": "Lightning",
  "path": "Nihility",
  "faction": "Stellaron Hunter",
  "releaseVersion": "1.2",
  "releaseDate": "2023-08-09",
  "description": "Kafka is a 5-star Lightning character...",
  "role": "DoT DPS",
  "tags": ["DoT", "Shock", "Debuff", "AoE"],
  "skills": [...],
  "traces": [...],
  "eidolons": [...],
  "stats": {...},
  "images": {
    "avatar": "/images/characters/kafka/avatar.png",
    "splash": "/images/characters/kafka/splash.png",
    "icon": "/images/characters/kafka/icon.png"
  }
}
```

#### 光锥数据 (lightcones/{slug}.json)

```json
{
  "id": "patience-is-all-you-need",
  "name": "耐心是功德",
  "nameEn": "Patience Is All You Need",
  "rarity": 5,
  "path": "Nihility",
  "stats": {
    "hp": 1058,
    "atk": 582,
    "def": 423
  },
  "passive": {
    "name": "Meditation",
    "description": "After the wearer attacks an enemy...",
    "superimpositions": [...]
  },
  "images": {
    "icon": "/images/lightcones/patience-is-all-you-need.png"
  }
}
```

---

## 三、图片存储规划

### 3.1 图片类型

| 图片类型 | 尺寸 | 格式 | 用途 |
|----------|------|------|------|
| Character Avatar | 128x128 | PNG | 角色卡片、列表 |
| Character Splash | 512x512 | PNG | 角色详情页 |
| Character Icon | 64x64 | PNG | 小图标、导航 |
| Light Cone Icon | 256x256 | PNG | 光锥卡片 |
| Relic Icon | 128x128 | PNG | 遗器卡片 |
| Element Icon | 64x64 | SVG | 属性显示 |
| Path Icon | 64x64 | SVG | 命途显示 |

### 3.2 图片来源

| 来源 | URL 模式 | 优先级 |
|------|----------|--------|
| prydwen.gg | `https://prydwen.gg/static/{type}/{id}.png` | P0 |
| game8.co | `https://img.game8.co/{type}/{id}.png` | P1 |
| 官方资源 | `https://act.hoyoverse.com/...` | P2 |

### 3.3 图片下载策略

```python
# 图片下载流程
1. 检查本地缓存是否存在
2. 如果不存在，从数据源下载
3. 保存到 data/images/{type}/{slug}/
4. 同时保存到 GameBeliever-web/public/images/{type}/{slug}/
5. 在 JSON 数据中记录图片路径
```

### 3.4 图片处理

```python
# 图片处理流程
1. 下载原始图片
2. 调整尺寸（如果需要）
3. 压缩优化（PNG 无损压缩）
4. 生成缩略图（可选）
5. 保存到目标目录
```

---

## 四、与 GameBeliever-web 的数据对接

### 4.1 数据导出路径

```
GameBeliever-crawler/output/
    └── GameBeliever-web/
        └── src/
            └── data/
                ├── characters/      # 角色 JSON
                ├── lightcones/      # 光锥 JSON
                ├── relics/          # 遗器 JSON
                └── keywords/        # 关键词 JSON
```

### 4.2 图片导出路径

```
GameBeliever-crawler/output/
    └── GameBeliever-web/
        └── public/
            └── images/
                ├── characters/      # 角色图片
                ├── lightcones/      # 光锥图片
                ├── relics/          # 遗器图片
                ├── elements/        # 属性图标
                └── paths/           # 命途图标
```

### 4.3 导出命令

```bash
# 导出所有数据
python -m src.main export --output ../GameBeliever-web/

# 导出指定类型
python -m src.main export --type characters --output ../GameBeliever-web/

# 仅导出图片
python -m src.main export --type images --output ../GameBeliever-web/
```

---

## 五、开发阶段

### Phase 1: 基础框架（1-2天）

| 任务 | 优先级 | 状态 |
|------|--------|------|
| 项目结构 | P0 | ✅ |
| 数据模型 | P0 | ✅ |
| 配置管理 | P0 | ✅ |
| HTTP 客户端 | P0 | ✅ |
| 缓存管理 | P0 | ✅ |
| 日志配置 | P0 | ✅ |
| CLI 入口 | P0 | ✅ |

**完成时间**：2026-06-14
**验证结果**：✅ CLI 命令正常工作

### Phase 2: prydwen.gg 爬虫（3-5天）

| 任务 | 优先级 | 状态 |
|------|--------|------|
| 角色列表爬取 | P0 | ✅ |
| 角色详情爬取 | P0 | ✅ |
| 光锥列表爬取 | P0 | ⏳ |
| 遗器列表爬取 | P0 | ⏳ |
| 图片下载 | P0 | ⏳ |
| 数据解析 | P0 | ✅ |

**完成时间**：2026-06-14
**解决方案**：使用 Playwright 渲染 JavaScript

**验证结果**：
- ✅ 成功爬取 90 个角色列表
- ✅ 成功爬取 Kafka 角色详情
- ✅ 提取技能、行迹、星魂、属性数据
- ✅ Playwright 正常工作

### Phase 3: 数据处理（2-3天）

| 任务 | 优先级 | 状态 |
|------|--------|------|
| 数据清洗 | P0 | ⏳ |
| 数据校验 | P0 | ⏳ |
| 数据导出 | P0 | ⏳ |
| 增量更新 | P1 | ⏳ |

**完成时间**：2026-06-14

**已完成功能**：
- ✅ 光锥列表爬取（162 个光锥）
- ✅ 遗器列表爬取（56 个遗器套装）
- ✅ Playwright 渲染 JavaScript

**待完成功能**：
- ⏳ 数据清洗
- ⏳ 数据校验

**已完成功能**：
- ✅ 数据导出到 GameBeliever-web
- ✅ 同步状态检查
- ✅ 定时任务脚本
- ✅ Cron/Systemd 配置

**验证结果**：
- ✅ 成功同步 90 个角色到 GameBeliever-web
- ✅ 同步命令正常工作
- ✅ 状态检查命令正常工作

### Phase 4: 扩展数据源（5-7天）

| 任务 | 优先级 | 状态 |
|------|--------|------|
| game8.co 爬虫 | P1 | ⏳ |
| 官方数据爬虫 | P1 | ⏳ |
| 多源数据合并 | P1 | ⏳ |

### Phase 5: 质量保证（2-3天）

| 任务 | 优先级 | 状态 |
|------|--------|------|
| 单元测试 | P0 | ⏳ |
| 集成测试 | P0 | ⏳ |
| 错误处理 | P0 | ⏳ |
| 监控告警 | P1 | ⏳ |

---

## 六、关键技术决策

### 6.1 为什么选择 Python？

- 丰富的爬虫库（requests, BeautifulSoup, Scrapy）
- 异步支持（aiohttp）
- 数据处理能力强（pandas, pydantic）
- 社区活跃，文档完善

### 6.2 为什么不用 Scrapy？

- 项目规模中等，不需要 Scrapy 的复杂架构
- 更灵活的控制
- 更容易与 GameBeliever-web 集成

### 6.3 图片存储策略

- **本地存储**：开发阶段使用本地存储
- **CDN 部署**：生产环境使用 Cloudflare R2 或 Cloudflare Pages
- **懒加载**：前端实现图片懒加载

---

## 七、与现有系统的集成

### 7.1 数据格式兼容

爬虫输出的 JSON 格式与 GameBeliever-web 的数据采集器兼容：

```typescript
// GameBeliever-web/src/scripts/collector/data-collector.ts
// 当前手动生成的数据格式
{
  "id": "kafka",
  "name": "Kafka",
  "element": "Lightning",
  ...
}

// 爬虫输出的数据格式（相同）
{
  "id": "kafka",
  "name": "Kafka",
  "element": "Lightning",
  ...
}
```

### 7.2 图片路径兼容

爬虫下载的图片路径与前端组件兼容：

```typescript
// CharacterCard.astro
const elementIcons: Record<string, string> = {
  Lightning: '/images/elements/lightning.svg',  // 爬虫下载
  Fire: '/images/elements/fire.svg',
  ...
};
```

---

## 八、风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| 数据源反爬 | 高 | 限流、User-Agent 轮换、代理池 |
| 数据格式变化 | 高 | 模块化解析器、版本控制 |
| 图片链接失效 | 中 | 多源备份、本地缓存 |
| 数据质量不一 | 中 | 严格校验、人工审核 |
| JavaScript 渲染 | 高 | 使用 Playwright 或寻找其他数据源 |

---

## 九、进度更新

### 2026-06-14

#### Phase 1: 基础框架 ✅ 完成

| 任务 | 状态 |
|------|------|
| 项目结构 | ✅ |
| 数据模型 | ✅ |
| 配置管理 | ✅ |
| HTTP 客户端 | ✅ |
| 缓存管理 | ✅ |
| 日志配置 | ✅ |
| CLI 入口 | ✅ |

#### Phase 2: prydwen.gg 爬虫 ⚠️ 部分完成

| 任务 | 状态 | 说明 |
|------|------|------|
| 角色列表爬取 | ✅ | 成功爬取 90 个角色 |
| 角色详情爬取 | ⚠️ | 页面使用 JavaScript 渲染 |
| 光锥列表爬取 | ⏳ | 待实现 |
| 遗器列表爬取 | ⏳ | 待实现 |
| 图片下载 | ⏳ | 待实现 |
| 数据解析 | ⏳ | 待实现 |

**下一步**：
1. 评估是否需要使用 Playwright 渲染 JavaScript
2. 考虑使用其他数据源
3. 实现光锥和遗器爬取
