# GameBeliever Crawler

Honkai Star Rail 数据爬虫项目

## 项目目标

从多个数据源爬取 HSR 游戏数据，输出标准化 JSON 格式，供 GameBeliever 网站使用。

## 数据范围

| 数据类型 | 目标数量 | 优先级 |
|----------|----------|--------|
| Characters | 60+ | P0 |
| Light Cones | 100+ | P0 |
| Relics | 40+ | P1 |
| Materials | 80+ | P1 |

## 数据源

| 数据源 | URL | 数据类型 | 状态 |
|--------|-----|----------|------|
| prydwen.gg | prydwen.gg/star-rail | 角色、光锥、遗器 | ⏳ 待接入 |
| game8.co | game8.co/games/Honkai-Star-Rail | 攻略、材料 | ⏳ 待接入 |
| 官方网站 | houkainsr.hoyoverse.com | 官方数据 | ⏳ 待接入 |

## 技术栈

- Python 3.10+
- requests - HTTP 请求
- BeautifulSoup4 - HTML 解析
- pydantic - 数据校验
- click - CLI 工具
- loguru - 日志记录

## 项目结构

```
GameBeliever-crawler/
├── src/
│   ├── __init__.py
│   ├── main.py              # CLI 入口
│   ├── config.py            # 配置管理
│   ├── crawler/             # 爬虫模块
│   │   ├── __init__.py
│   │   ├── base.py          # 爬虫基类
│   │   ├── prydwen.py       # prydwen.gg 爬虫
│   │   ├── game8.py         # game8.co 爬虫
│   │   └── official.py      # 官方数据爬虫
│   ├── parser/              # 解析模块
│   │   ├── __init__.py
│   │   ├── character.py     # 角色数据解析
│   │   ├── lightcone.py     # 光锥数据解析
│   │   ├── relic.py         # 遗器数据解析
│   │   └── material.py      # 材料数据解析
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   ├── character.py     # 角色模型
│   │   ├── lightcone.py     # 光锥模型
│   │   ├── relic.py         # 遗器模型
│   │   └── material.py      # 材料模型
│   ├── pipeline/            # 数据管道
│   │   ├── __init__.py
│   │   ├── clean.py         # 数据清洗
│   │   ├── validate.py      # 数据校验
│   │   └── export.py        # 数据导出
│   └── utils/               # 工具函数
│       ├── __init__.py
│       ├── http.py          # HTTP 工具
│       ├── cache.py         # 缓存管理
│       └── logger.py        # 日志配置
├── data/                    # 数据目录
│   ├── raw/                 # 原始数据
│   ├── processed/           # 处理后数据
│   └── output/              # 输出数据
├── config/                  # 配置文件
│   ├── settings.yaml        # 主配置
│   └── sources.yaml         # 数据源配置
├── tests/                   # 测试文件
├── requirements.txt         # 依赖列表
├── pyproject.toml           # 项目配置
└── README.md
```

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置

编辑 `config/settings.yaml` 配置数据源和输出路径。

### 运行爬虫

```bash
# 爬取所有角色
python -m src.main crawl --type characters

# 爬取指定角色
python -m src.main crawl --type characters --slug kafka

# 爬取所有光锥
python -m src.main crawl --type lightcones

# 导出数据
python -m src.main export --format json --output ../GameBeliever-web/src/data/
```

## 开发计划

### Phase 1: 骨架搭建
- [x] 项目结构
- [ ] 基础配置
- [ ] 爬虫基类
- [ ] 数据模型

### Phase 2: 核心功能
- [ ] prydwen.gg 爬虫
- [ ] 数据解析器
- [ ] 数据管道
- [ ] CLI 工具

### Phase 3: 数据源扩展
- [ ] game8.co 爬虫
- [ ] 官方数据爬虫
- [ ] 增量更新
- [ ] 缓存管理

### Phase 4: 质量保证
- [ ] 单元测试
- [ ] 集成测试
- [ ] 数据校验
- [ ] 错误处理
