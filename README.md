# Pixel Alchemist — 像素动画精灵图生成器

中文 | [English](./README.en.md)

上传一张参考图、输入一句动作描述,AI 自动生成 4-6 帧像素风格动画精灵图(Sprite Sheet),支持一键导出 Sprite Sheet 或逐帧 PNG,可直接用于游戏开发。

## 功能特性

- **图片上传**:支持任意图片作为角色参考图
- **自然语言驱动**:如「害羞地低头捏裙摆」,AI 自动拆解为逐帧动作
- **像素化处理**:自动将 AI 生成图转为像素艺术风格,支持透明背景
- **多帧动画**:4-6 帧,支持循环(loop)与单次(oneshot)两种动画类型
- **多种风格**:cute / cool / retro 三种预设风格,内置 5 套配色板
- **灵活导出**:横向 Sprite Sheet 单图导出,或逐帧 PNG 打包 ZIP 下载
- **实时预览**:前端内置动画播放器,生成后即刻预览效果

## 工作原理

```
参考图 + 动作描述
      │
      ▼
┌─────────────────┐   ┌──────────────────┐   ┌─────────────────┐
│  PromptBuilder  │──▶│  ImageGenerator  │──▶│ SpriteAssembler │
│  动作拆解为     │   │  通义万相逐帧    │   │  像素化 + 拼接  │
│  逐帧 Prompt    │   │  图生图          │   │  Sprite Sheet   │
└─────────────────┘   └──────────────────┘   └─────────────────┘
                                                      │
                                                      ▼
                                        Sprite Sheet / 逐帧 PNG / 调色板
```

1. **动作拆解**:将动作描述按帧数拆解为起始、过程、高潮、收尾等阶段性 Prompt
2. **AI 生成**:调用通义万相(Qwen-Image)图生图能力,以参考图为基础逐帧生成
3. **后处理**:像素化降采样、背景透明化、提取主色调色板
4. **拼接导出**:横向拼接为 Sprite Sheet,并提供逐帧提取与 ZIP 打包

## 技术栈

| 层 | 技术 |
|------|------|
| 前端 | React 18 · Vite 5 · TypeScript · Axios |
| 后端 | Python 3.10+ · FastAPI · Pillow · Pydantic |
| AI 服务 | 通义万相 Qwen-Image(阿里云百炼 DashScope SDK) |

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- 阿里云百炼 API Key([获取方式](#获取-api-key))

### 1. 克隆项目

```bash
git clone https://github.com/TseKang/Pixel-Alchemist.git
cd Pixel-Alchemist
```

### 2. 启动后端

```bash
cd backend

# (可选) 创建 conda 环境
conda create -n Pixel python=3.10 -y
conda activate Pixel

# 安装依赖
pip install -r requirements.txt

# 配置 API Key
cp .env.example .env
# 编辑 .env，填入 DASHSCOPE_API_KEY 和 WORKSPACE_ID

# 启动服务
python -m app.main
```

- 后端服务:http://localhost:8001
- API 文档(Swagger):http://localhost:8001/docs

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端运行在 http://localhost:3000,API 请求自动代理到后端。

## 配置说明

`backend/.env` 支持的配置项:

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `DASHSCOPE_API_KEY` | 阿里云百炼 API Key(**必填**) | - |
| `WORKSPACE_ID` | 百炼业务空间 ID(qwen-image 需要) | - |
| `DEFAULT_MODEL` | 生成模型 | `qwen-image-3.0-pro` |
| `HOST` / `PORT` | 服务监听地址 / 端口 | `0.0.0.0` / `8001` |
| `UPLOAD_DIR` / `OUTPUT_DIR` | 上传 / 输出目录 | `./uploads` / `./outputs` |
| `MAX_UPLOAD_SIZE` | 最大上传大小(字节) | `10485760`(10MB) |

> 注意:`qwen-image-3.0-pro` 支持图生图;基础版 `qwen-image-3.0` 可能不支持参考图输入。

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/generate` | 提交生成任务(参考图 + 动作描述 + 参数) |
| GET | `/api/task/{task_id}` | 查询任务状态与结果 |
| GET | `/api/download/sprite/{task_id}` | 下载 Sprite Sheet |
| GET | `/api/download/frame/{task_id}/{frame_index}` | 下载单帧 PNG |
| GET | `/api/download/frames/{task_id}` | 下载全部帧(ZIP 打包) |
| GET | `/api/palettes` | 获取预设调色板列表 |

### 生成参数

| 参数 | 说明 | 可选值 / 默认 |
|------|------|--------------|
| `action_prompt` | 动作描述(必填) | 1-500 字符 |
| `frame_count` | 动画帧数 | 4-6,默认 `4` |
| `canvas_size` | 画布尺寸 | 默认 `64x64` |
| `animation_type` | 动画类型 | `loop` / `oneshot` |
| `style` | 画面风格 | `cute` / `cool` / `retro` |

## 项目结构

```
Pixel-Alchemist/
├── frontend/                  # React 前端
│   └── src/
│       ├── components/        # 上传、输入、结果展示组件
│       └── services/          # API 封装
├── backend/                   # FastAPI 后端
│   ├── app/
│   │   ├── api/               # 路由层
│   │   ├── services/          # Prompt 构建 / 图片生成 / 精灵图拼接
│   │   ├── utils/             # 像素化等图片处理工具
│   │   ├── models/            # Pydantic 数据模型
│   │   └── config.py          # 配置管理
│   └── .env.example           # 环境变量模板
├── requirement.md             # 需求文档
└── README.md
```

## 获取 API Key

1. 访问[阿里云百炼平台](https://bailian.console.aliyun.com)并注册 / 登录
2. 开通通义万相(图像生成)服务
3. 在控制台创建 API Key,填入 `backend/.env` 的 `DASHSCOPE_API_KEY`
4. 在业务空间管理中获取 Workspace ID,填入 `WORKSPACE_ID`

## License

[MIT](https://opensource.org/licenses/MIT)
