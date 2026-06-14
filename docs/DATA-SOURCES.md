# 数据源说明

## 一、数据源列表

### 1.1 prydwen.gg（主要数据源）

**网站**: https://prydwen.gg/star-rail

**数据类型**:
- 角色数据（基本信息、技能、行迹、星魂）
- 光锥数据（属性、被动效果）
- 遗器数据（套装效果、主副属性）
- 队伍推荐
- Tier List

**爬取策略**:
- 限流：1 请求/秒
- 缓存：HTML 页面缓存 1 小时
- 重试：3 次重试，指数退避

**URL 模式**:
```
角色列表: https://prydwen.gg/star-rail/characters
角色详情: https://prydwen.gg/star-rail/characters/{slug}
光锥列表: https://prydwen.gg/star-rail/light-cones
光锥详情: https://prydwen.gg/star-rail/light-cones/{slug}
遗器列表: https://prydwen.gg/star-rail/relics
遗器详情: https://prydwen.gg/star-rail/relics/{slug}
```

### 1.2 game8.co（辅助数据源）

**网站**: https://game8.co/games/Honkai-Star-Rail

**数据类型**:
- 角色攻略
- 材料获取途径
- 遗器推荐
- 队伍搭配

**爬取策略**:
- 限流：2 请求/秒
- 缓存：HTML 页面缓存 2 小时
- 重试：3 次重试

### 1.3 官方网站（补充数据源）

**网站**: https://act.hoyoverse.com/...

**数据类型**:
- 角色立绘
- 官方公告
- 版本信息

**爬取策略**:
- 仅下载图片
- 不爬取文本内容

---

## 二、数据解析规则

### 2.1 角色数据解析

```python
# 从 prydwen.gg 解析角色数据
{
    "id": "kafka",  # URL slug
    "name": "Kafka",  # 英文名
    "rarity": 5,  # 稀有度
    "element": "Lightning",  # 属性
    "path": "Nihility",  # 命途
    "role": "DoT DPS",  # 定位
    "skills": [...],  # 技能列表
    "traces": [...],  # 行迹列表
    "eidolons": [...],  # 星魂列表
    "stats": {...},  # 属性数据
}
```

### 2.2 光锥数据解析

```python
# 从 prydwen.gg 解析光锥数据
{
    "id": "patience-is-all-you-need",
    "name": "Patience Is All You Need",
    "rarity": 5,
    "path": "Nihility",
    "stats": {
        "hp": 1058,
        "atk": 582,
        "def": 423
    },
    "passive": {
        "name": "Meditation",
        "description": "...",
        "superimpositions": [...]
    }
}
```

### 2.3 遗器数据解析

```python
# 从 prydwen.gg 解析遗器数据
{
    "id": "prisoner-in-deep-confinement",
    "name": "Prisoner in Deep Confinement",
    "set_effects": [
        {"pieces": 2, "description": "..."},
        {"pieces": 4, "description": "..."}
    ],
    "pieces": [
        {"slot": "Head", "main_stat": "HP", "sub_stats": [...]},
        {"slot": "Hands", "main_stat": "ATK", "sub_stats": [...]},
        ...
    ]
}
```

---

## 三、反爬策略

### 3.1 请求限流

```python
# 每个数据源配置不同的限流
sources:
  prydwen:
    rate_limit: 1.0  # 1 请求/秒
  game8:
    rate_limit: 2.0  # 2 请求/秒
```

### 3.2 User-Agent 轮换

```python
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36...",
    ...
]
```

### 3.3 代理池（可选）

```python
PROXY_POOL = [
    "http://proxy1:port",
    "http://proxy2:port",
    ...
]
```

### 3.4 缓存策略

```python
# 缓存 HTML 页面，避免重复请求
cache_enabled: true
cache_ttl: 3600  # 1小时
```

---

## 四、错误处理

### 4.1 常见错误

| 错误类型 | 原因 | 处理方式 |
|----------|------|----------|
| 403 Forbidden | 被反爬拦截 | 更换 User-Agent、使用代理 |
| 429 Too Many Requests | 请求过于频繁 | 增加限流间隔 |
| 500 Server Error | 服务器错误 | 重试、记录日志 |
| 解析错误 | 页面结构变化 | 更新解析器、报警 |

### 4.2 重试机制

```python
# 使用 tenacity 实现重试
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_page(url: str):
    # 请求逻辑
    pass
```

---

## 五、数据质量保证

### 5.1 数据校验

使用 Pydantic 模型校验数据：

```python
from pydantic import BaseModel, validator

class Character(BaseModel):
    id: str
    name: str
    rarity: int
    
    @validator('rarity')
    def validate_rarity(cls, v):
        if v not in [4, 5]:
            raise ValueError('Rarity must be 4 or 5')
        return v
```

### 5.2 数据完整性检查

```python
# 检查必填字段
required_fields = ['id', 'name', 'rarity', 'element', 'path']

# 检查数据范围
valid_elements = ['Physical', 'Fire', 'Ice', 'Lightning', 'Wind', 'Quantum', 'Imaginary']
```

### 5.3 数据去重

```python
# 基于 ID 去重
seen_ids = set()
for item in data_list:
    if item['id'] in seen_ids:
        continue
    seen_ids.add(item['id'])
    # 处理数据
```
