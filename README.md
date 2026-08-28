# Pixel Alchemist - 像素动画精灵图生成器

一款 Web 应用，用户上传参考图并输入动作描述，AI 自动生成 4-6 帧像素动画精灵图（Sprite Sheet），支持导出为 Sprite Sheet 和逐帧 PNG。

## 功能特性

- 图片上传 - 支持上传任意图片作为参考
- 动作描述 - 自然语言描述动作，AI 自动拆解为多帧
- 像素画生成 - 将参考图转化为像素艺术风格
- 多帧动画 - 生成 4-6 帧循环/单次动画
- Sprite Sheet 导出 - 横向排列的单张精灵图
- 逐帧 PNG 导出 - 每帧单独 PNG 文件（ZIP 打包）

## 技术栈

### 前端
- React 18 + Vite
- TypeScript
- Axios

### 后端
- Python 3.10+ / FastAPI
- Pillow (图片处理)
- DashScope SDK (通义万相 API)

### AI 服务
- 通义万相 (WanXiang) - 阿里云百炼平台

## 快速开始

### 1. 环境准备

```bash
# 创建 conda 环境
conda create -n Pixel python=3.10 -y
conda activate Pixel
```

### 2. 启动后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置 API Key (复制模板并填入你的 Key)
cp .env.example .env
# 编辑 .env: DASHSCOPE_API_KEY=你的API Key

# 启动服务
python -m app.main
```

后端服务运行在 http://localhost:8001

API 文档: http://localhost:8001/docs

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端运行在 http://localhost:3000

## 项目结构

```
PixelGenerater/
├── frontend/          # React 前端
├── backend/           # FastAPI 后端
├── requirement.md     # 需求文档
├── tech_design.md     # 技术设计文档
└── README.md          # 本文件
```

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/generate` | 提交生成任务 |
| GET | `/api/task/{task_id}` | 查询任务状态 |
| GET | `/api/download/sprite/{task_id}` | 下载 Sprite Sheet |
| GET | `/api/download/frames/{task_id}` | 下载逐帧 PNG (ZIP) |
| GET | `/api/palettes` | 获取预设调色板列表 |

## 配置说明

编辑 `backend/.env` 文件：

```env
# 阿里云百炼 API Key (必填)
DASHSCOPE_API_KEY=123abc

# 服务配置
HOST=0.0.0.0
PORT=8001

# 文件存储
UPLOAD_DIR=./uploads
OUTPUT_DIR=./outputs

# 最大上传文件大小 (MB)
MAX_UPLOAD_SIZE=10
```

## 获取 API Key

1. 访问 [阿里云百炼平台](https://bailian.console.aliyun.com)
2. 注册/登录账号
3. 开通通义万相服务
4. 获取 API Key

## License

MIT
