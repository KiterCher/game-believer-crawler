# 图片存储方案

## 一、图片分类

### 1.1 角色图片

| 类型 | 尺寸 | 格式 | 用途 | 存储路径 |
|------|------|------|------|----------|
| Avatar | 128x128 | PNG | 角色卡片、列表 | `images/characters/{slug}/avatar.png` |
| Splash | 512x512 | PNG | 角色详情页 | `images/characters/{slug}/splash.png` |
| Icon | 64x64 | PNG | 小图标 | `images/characters/{slug}/icon.png` |

### 1.2 光锥图片

| 类型 | 尺寸 | 格式 | 用途 | 存储路径 |
|------|------|------|------|----------|
| Icon | 256x256 | PNG | 光锥卡片 | `images/lightcones/{slug}.png` |

### 1.3 遗器图片

| 类型 | 尺寸 | 格式 | 用途 | 存储路径 |
|------|------|------|------|----------|
| Head | 128x128 | PNG | 遗器卡片 | `images/relics/{set}/head.png` |
| Hands | 128x128 | PNG | 遗器卡片 | `images/relics/{set}/hands.png` |
| Body | 128x128 | PNG | 遗器卡片 | `images/relics/{set}/body.png` |
| Feet | 128x128 | PNG | 遗器卡片 | `images/relics/{set}/feet.png` |

### 1.4 图标图片

| 类型 | 尺寸 | 格式 | 用途 | 存储路径 |
|------|------|------|------|----------|
| Element | 64x64 | SVG | 属性显示 | `images/elements/{element}.svg` |
| Path | 64x64 | SVG | 命途显示 | `images/paths/{path}.svg` |

---

## 二、图片来源

### 2.1 prydwen.gg

```
角色头像: https://prydwen.gg/static/characters/{slug}.png
光锥图标: https://prydwen.gg/static/lightcones/{slug}.png
遗器图标: https://prydwen.gg/static/relics/{slug}.png
```

### 2.2 game8.co

```
角色图片: https://img.game8.co/images/{type}/{id}.png
```

### 2.3 官方资源

```
角色立绘: https://act.hoyoverase.com/...
```

---

## 三、图片下载流程

```
┌─────────────────────────────────────────────────────────┐
│                    图片下载流程                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 检查本地缓存                                         │
│     ↓                                                   │
│  2. 如果存在 → 跳过下载                                  │
│     如果不存在 → 继续                                    │
│     ↓                                                   │
│  3. 从数据源下载图片                                      │
│     ↓                                                   │
│  4. 保存到 data/images/{type}/{slug}/                   │
│     ↓                                                   │
│  5. 同时复制到 GameBeliever-web/public/images/           │
│     ↓                                                   │
│  6. 在 JSON 数据中记录图片路径                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 四、图片存储位置

### 4.1 开发环境

```
GameBeliever-crawler/
└── data/
    └── images/
        ├── characters/
        │   ├── kafka/
        │   │   ├── avatar.png
        │   │   ├── splash.png
        │   │   └── icon.png
        │   └── ...
        ├── lightcones/
        │   ├── patience-is-all-you-need.png
        │   └── ...
        ├── relics/
        │   ├── prisoner/
        │   │   ├── head.png
        │   │   ├── hands.png
        │   │   ├── body.png
        │   │   └── feet.png
        │   └── ...
        ├── elements/
        │   ├── physical.svg
        │   ├── fire.svg
        │   └── ...
        └── paths/
            ├── destruction.svg
            ├── hunt.svg
            └── ...
```

### 4.2 生产环境（GameBeliever-web）

```
GameBeliever-web/
└── public/
    └── images/
        ├── characters/      # 角色图片
        ├── lightcones/      # 光锥图片
        ├── relics/          # 遗器图片
        ├── elements/        # 属性图标
        └── paths/           # 命途图标
```

### 4.3 CDN 部署（可选）

```
Cloudflare R2 Bucket:
└── gamebeliever-images/
    ├── characters/
    ├── lightcones/
    ├── relics/
    ├── elements/
    └── paths/
```

---

## 五、图片优化

### 5.1 压缩策略

- **PNG**: 使用 `pngquant` 或 `Pillow` 进行无损压缩
- **SVG**: 使用 `svgo` 进行优化
- **WebP**: 可选转换为 WebP 格式以减小文件大小

### 5.2 懒加载

前端实现图片懒加载：

```html
<img src="placeholder.svg" data-src="actual-image.png" loading="lazy" />
```

### 5.3 响应式图片

根据设备尺寸加载不同分辨率的图片：

```html
<picture>
  <source media="(min-width: 768px)" srcset="image-large.png" />
  <source media="(min-width: 480px)" srcset="image-medium.png" />
  <img src="image-small.png" alt="..." />
</picture>
```

---

## 六、图片管理命令

```bash
# 下载所有角色图片
python -m src.main download --type characters --all

# 下载指定角色图片
python -m src.main download --type characters --slug kafka

# 下载所有光锥图片
python -m src.main download --type lightcones --all

# 清理图片缓存
python -m src.main cache --clear images

# 检查图片完整性
python -m src.main check --type images
```
