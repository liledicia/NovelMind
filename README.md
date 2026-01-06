# NovelMind - 晋江小说智能推荐系统

一个基于Web的晋江文学城小说推荐系统，提供智能搜索和个性化推荐功能。

## ✨ 项目特性

- **智能搜索**：输入小说名称，先从数据库查询，未找到则实时爬取
- **智能推荐**：基于多维度算法推荐10本相似小说
  - 标签相似度（Jaccard算法，权重50%）
  - 类型视角匹配（权重30%）
  - 完结状态匹配（权重10%）
  - 同作者加分（权重10%）
- **完整数据**：展示小说详情、统计数据、原网站链接
- **前后端分离**：FastAPI + Vue.js 3 + Element Plus

---

## 🛠️ 技术栈

### 后端
- **FastAPI** - 现代高性能Web框架
- **Pydantic** - 数据验证
- **SQLite** - 轻量级数据库（已含150本小说数据）
- **BeautifulSoup4 + lxml** - HTML解析
- **Requests** - HTTP请求

### 前端
- **Vue.js 3** - 渐进式前端框架
- **Element Plus** - UI组件库
- **Axios** - HTTP客户端
- **Vite** - 现代化构建工具

---

## 🚀 快速开始（3步启动）

### 第1步：启动后端

```bash
# 进入项目根目录
cd /Users/zhaozixu/Desktop/NovelMind

# 激活虚拟环境
source .venv/bin/activate

# 启动后端服务
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**或者使用快捷脚本：**
```bash
cd /Users/zhaozixu/Desktop/NovelMind
./start.sh
```

**验证后端启动成功：**
- 浏览器访问: http://localhost:8000/docs
- 应该能看到Swagger API文档

---

### 第2步：安装前端依赖

**打开新的终端窗口**，运行：

```bash
# 进入前端目录
cd /Users/zhaozixu/Desktop/NovelMind/frontend

# 安装npm依赖（首次运行需要）
npm install
```

---

### 第3步：启动前端

```bash
# 在frontend目录下
npm run dev
```

**访问应用：**
打开浏览器访问 **http://localhost:5173**

---

## 📂 项目结构

```
NovelMind/
├── backend/                          # 后端目录
│   ├── app/
│   │   ├── main.py                   # FastAPI应用入口 ⭐
│   │   ├── config.py                 # 配置文件
│   │   ├── database/
│   │   │   └── connection.py        # 数据库连接管理
│   │   ├── services/
│   │   │   ├── crawler_service.py   # 爬虫服务 ⭐
│   │   │   ├── novel_service.py     # 数据库查询服务
│   │   │   └── recommendation_service.py  # 推荐算法 ⭐
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   └── novels.py        # API路由 ⭐
│   │   │   └── schemas/
│   │   │       ├── novel.py         # 数据模型
│   │   │       └── recommendation.py
│   │   └── utils/
│   │       └── similarity.py        # 相似度计算工具 ⭐
│   └── requirements.txt              # Python依赖
│
├── frontend/                         # 前端目录
│   ├── src/
│   │   ├── main.js                  # Vue入口
│   │   ├── App.vue                  # 根组件
│   │   ├── views/
│   │   │   └── Home.vue             # 主页面 ⭐
│   │   ├── components/
│   │   │   ├── SearchBar.vue        # 搜索框组件
│   │   │   ├── NovelCard.vue        # 小说详情卡片
│   │   │   └── RecommendationList.vue # 推荐列表
│   │   ├── api/
│   │   │   └── novels.js            # API封装 ⭐
│   │   └── utils/
│   │       └── formatter.js         # 数据格式化
│   ├── vite.config.js               # Vite配置
│   └── package.json                 # npm依赖
│
├── jinjiang_novels.db               # SQLite数据库（150本小说）
├── NovelMindScrawl.py              # 原始爬虫脚本
├── start.sh                         # 后端启动脚本
└── README.md                        # 本文档
```

---

## 🎯 完整功能演示

### 1. 搜索已存在的小说

1. 在搜索框输入：`全职高手`
2. 点击"搜索"按钮
3. 系统从数据库查询（<1秒）
4. 显示小说详细信息
5. 自动推荐10本相似小说

### 2. 搜索不存在的小说（实时爬取）

1. 输入一个数据库中没有的小说名
2. 系统会提示"正在爬取中"（5-10秒）
3. 爬取成功后保存到数据库
4. 显示详情并推荐

### 3. 查看推荐详情

- 每个推荐卡片显示相似度百分比
- 显示匹配原因（如"标签匹配度75%"）
- 点击"查看详情"跳转到晋江原文

---

## 📡 API使用指南

### 1. 搜索小说

**端点**: `GET /api/novels/search`

**参数**:
- `q` (必填): 小说名称

**示例请求**:
```bash
curl "http://localhost:8000/api/novels/search?q=全职高手"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "book_id": 123456,
    "title": "全职高手",
    "author": "蝴蝶蓝",
    "intro": "简介内容...",
    "tags": "电竞 竞技 游戏",
    "category": "原创-言情-近代现代-爱情",
    "status": "完结",
    "word_count": 530000,
    "chapter_count": 200,
    "url": "https://www.jjwxc.net/onebook.php?novelid=123456"
  },
  "stats": {
    "review_count": 25000,
    "favorite_count": 120000,
    "score": 580000
  },
  "source": "database"
}
```

### 2. 获取推荐列表

**端点**: `GET /api/recommendations/{book_id}`

**参数**:
- `book_id` (路径参数): 小说ID
- `limit` (可选): 推荐数量，默认10本

**示例请求**:
```bash
curl "http://localhost:8000/api/recommendations/123456?limit=5"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "target_novel": {
      "book_id": 123456,
      "title": "全职高手",
      "author": "蝴蝶蓝"
    },
    "recommendations": [
      {
        "book_id": 789012,
        "title": "网游之近战法师",
        "author": "蝴蝶蓝",
        "similarity_score": 85.5,
        "match_reasons": [
          "标签匹配度: 67%",
          "类型相同",
          "同作者",
          "同为完结"
        ],
        "tags": "电竞 竞技",
        "url": "https://www.jjwxc.net/onebook.php?novelid=789012"
      }
    ]
  }
}
```

### 3. API文档

打开浏览器访问：
- **Swagger UI文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/api/health

---

## 🧠 核心功能说明

### 1. 搜索流程

```
用户输入小说名
    ↓
在数据库中精确搜索
    ↓
  找到了？
    ├─ 是 → 返回数据库结果（source: "database"）
    └─ 否 → 调用爬虫实时爬取
              ↓
          爬取成功？
              ├─ 是 → 保存到数据库 → 返回结果（source: "crawled"）
              └─ 否 → 返回404错误
```

### 2. 推荐算法

**相似度计算公式**:

```python
similarity_score = (
    tag_similarity * 50% +        # Jaccard相似度
    category_match * 15% +         # 类型匹配
    perspective_match * 15% +      # 视角匹配
    status_match * 10% +           # 状态匹配
    same_author * 10%              # 同作者
) * 100
```

**标签相似度示例**:
```
小说A标签: ["强强", "江湖", "正剧"]
小说B标签: ["强强", "现代", "正剧"]
交集: {"强强", "正剧"} = 2
并集: {"强强", "江湖", "正剧", "现代"} = 4
Jaccard相似度 = 2/4 = 50%
```

---

## 💾 数据库说明

### book表（小说基本信息）

| 字段 | 类型 | 说明 |
|------|------|------|
| book_id | INTEGER | 小说ID（主键）|
| title | TEXT | 书名 |
| author | TEXT | 作者 |
| intro | TEXT | 简介 |
| tags | TEXT | 标签（空格分隔）|
| category | TEXT | 文章类型 |
| perspective | TEXT | 作品视角 |
| status | TEXT | 连载状态 |
| word_count | INTEGER | 字数 |
| chapter_count | INTEGER | 章节数 |
| last_update_time | TEXT | 最后更新时间 |

### stats表（统计数据）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 自增主键 |
| book_id | INTEGER | 关联小说ID |
| date | TEXT | 采集日期 |
| review_count | INTEGER | 书评数 |
| favorite_count | INTEGER | 收藏数 |
| score | INTEGER | 积分 |

**当前数据**: 数据库已包含150本晋江热门小说的完整数据

---

## 🧪 测试验证

### 后端API测试

```bash
# 健康检查
curl http://localhost:8000/api/health

# 搜索小说
curl "http://localhost:8000/api/novels/search?q=全职高手"

# 获取推荐
curl "http://localhost:8000/api/recommendations/1?limit=5"
```

### 使用Python测试

```python
import requests

# 搜索小说
response = requests.get(
    "http://localhost:8000/api/novels/search",
    params={"q": "全职高手"}
)
novel_data = response.json()
print(f"找到小说: {novel_data['data']['title']}")

# 获取推荐
book_id = novel_data['data']['book_id']
response = requests.get(
    f"http://localhost:8000/api/recommendations/{book_id}",
    params={"limit": 5}
)
recommendations = response.json()
print(f"推荐了 {len(recommendations['data']['recommendations'])} 本小说")
```

### 前端功能测试

| 功能 | 测试步骤 | 预期结果 |
|------|---------|---------|
| 搜索框 | 输入"全职高手" | 自动提示，Enter可搜索 |
| 数据库搜索 | 搜索"全职高手" | <1秒显示结果 |
| 实时爬取 | 搜索不存在的小说 | 5-10秒显示结果 |
| 推荐显示 | 查看推荐卡片 | 显示10本小说 |
| 相似度 | 查看相似度环 | 显示0-100%进度 |
| 跳转原文 | 点击"查看原文" | 新标签打开晋江页面 |

---

## ❓ 常见问题

### Q1: 前端npm install失败？

**错误：** `npm error code EACCES`

**解决：**
```bash
# 方法1：使用nvm管理node版本（推荐）
nvm use 18

# 方法2：手动安装依赖
cd frontend
npm install --legacy-peer-deps
```

### Q2: 后端启动失败？

**错误：** `ModuleNotFoundError: No module named 'app'`

**解决：**
```bash
# 确保在backend目录下启动
cd /Users/zhaozixu/Desktop/NovelMind/backend
uvicorn app.main:app --reload
```

### Q3: 前后端连接失败？

**错误：** 前端显示"网络错误"

**检查清单：**
1. ✅ 后端是否在8000端口运行？
   ```bash
   curl http://localhost:8000/api/health
   ```
2. ✅ 前端代理配置是否正确？查看 `frontend/vite.config.js`
3. ✅ 防火墙是否允许？

### Q4: 搜索一直加载？

**可能原因：**
- 网络问题导致爬虫超时
- 晋江网站访问受限

**解决：**
1. 先搜索数据库已有的小说（如"全职高手"）
2. 检查网络连接
3. 查看后端日志确认错误

### Q5: 为什么有些小说搜索不到？

可能该小说不在数据库中，且爬虫搜索也未找到。建议检查小说名称拼写。

### Q6: 推荐的小说不够相似？

可以调整 `backend/app/config.py` 中的相似度权重配置，增加某个维度的权重。

### Q7: 如何添加更多小说到数据库？

运行原始的 `NovelMindScrawl.py` 脚本，或者通过搜索API让系统自动爬取。

---

## 📊 开发进度

### ✅ 已完成

- [x] 后端项目结构搭建
- [x] 数据库连接层
- [x] 爬虫服务重构
- [x] 小说查询服务
- [x] 推荐算法实现（多维度相似度计算）
- [x] FastAPI路由和接口
- [x] API数据模型（Pydantic）
- [x] CORS配置
- [x] API文档（Swagger/ReDoc）
- [x] 数据库索引优化
- [x] 前端Vue.js 3项目搭建
- [x] 前端组件开发（SearchBar, NovelCard, RecommendationList）
- [x] 前端与后端API集成
- [x] 响应式UI设计
- [x] 完整的错误处理和加载状态

### 🔜 可选扩展功能

- [ ] Redis缓存层
- [ ] 用户系统（注册/登录/收藏）
- [ ] 阅读历史记录
- [ ] 单元测试
- [ ] Docker部署
- [ ] 数据分析面板

---

## ⚠️ 注意事项

### 爬虫使用规范

**重要提示**:
1. 本项目仅供学习研究使用
2. 请遵守晋江文学城的 robots.txt 规则
3. 爬虫已内置延迟机制（2-3秒），避免频繁请求
4. 请勿用于商业用途
5. 爬取的数据请尊重原作者版权

### 性能优化建议

**后端优化**:
- 数据库已添加索引（title, tags, author, book_id）
- 推荐计算在内存中进行，响应速度快
- 可添加Redis缓存进一步提升性能

**前端优化**:
- 图片懒加载
- 虚拟滚动（推荐列表很长时）
- 缓存搜索结果（localStorage）

### 错误处理

- 404: 小说未找到（数据库和爬取都失败）
- 500: 服务器错误（爬虫异常、数据库错误等）
- 422: 参数验证失败

---

## 🎨 界面展示

### 主页面
- **顶部**：NovelMind标题 + 副标题
- **搜索区**：大号搜索框 + 提示文字
- **结果区**：小说详情卡片（白色背景）
- **推荐区**：网格布局的推荐卡片

### 小说详情卡
- 标题 + 来源标签（数据库/实时爬取）
- 作者信息
- 属性表格（类型、视角、状态、字数等）
- 标签云
- 统计数据（收藏、评论、积分）
- 简介（可滚动）
- 查看原文按钮

### 推荐卡片
- 相似度进度环（彩色）
- 小说标题 + 作者
- 匹配原因标签
- 状态 + 字数
- 收藏数 + 评论数
- 查看详情按钮

---

## 📝 更新日志

- **2026-01-05**:
  - ✅ 后端完整开发完成
  - ✅ 前端Vue项目创建
  - ✅ 所有组件开发完成
  - ✅ 前后端联调测试通过

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

---

## 📄 许可证

本项目仅供学习交流使用

---

## 📧 联系方式

如遇到问题：
1. 查看浏览器控制台（F12）
2. 查看后端日志
3. 检查本文档的"常见问题"部分

---

**最后更新**: 2026-01-05
**版本**: v1.0.0

**祝你使用愉快！** 🎉
