# Pixel Alchemist — AI Pixel Art Sprite Sheet Generator

[中文](./README.md) | English

Upload a reference image, describe an action in natural language, and let AI generate a 4-6 frame pixel-art animation sprite sheet. Export as a single sprite sheet or individual PNG frames, ready to drop into your game.

## Features

- **Image upload**: use any image as the character reference
- **Natural language driven**: e.g. "shyly lowers head and pinches skirt hem" — AI splits it into per-frame actions
- **Pixelation pipeline**: converts AI-generated images into pixel-art style with transparent background
- **Multi-frame animation**: 4-6 frames, supporting both `loop` and `oneshot` animation types
- **Multiple styles**: cute / cool / retro presets, plus 5 built-in color palettes
- **Flexible export**: single horizontal sprite sheet, or per-frame PNGs bundled as a ZIP
- **Live preview**: built-in animation player in the frontend for instant playback

## How It Works

```
Reference image + action prompt
      │
      ▼
┌─────────────────┐   ┌──────────────────┐   ┌─────────────────┐
│  PromptBuilder  │──▶│  ImageGenerator  │──▶│ SpriteAssembler │
│  Split action   │   │  Qwen-Image      │   │  Pixelate +     │
│  into per-frame │   │  image-to-image  │   │  assemble       │
│  prompts        │   │  per frame       │   │  sprite sheet   │
└─────────────────┘   └──────────────────┘   └─────────────────┘
                                                      │
                                                      ▼
                                    Sprite sheet / PNG frames / palette
```

1. **Action decomposition**: the action prompt is split into staged per-frame prompts (start, progression, climax, recovery)
2. **AI generation**: each frame is generated via Qwen-Image (image-to-image) based on the reference image
3. **Post-processing**: pixelation via downsampling, background transparency, dominant palette extraction
4. **Assembly & export**: frames are stitched horizontally into a sprite sheet, with per-frame extraction and ZIP packaging

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18 · Vite 5 · TypeScript · Axios |
| Backend | Python 3.10+ · FastAPI · Pillow · Pydantic |
| AI Service | Qwen-Image via Alibaba Cloud Model Studio (DashScope SDK) |

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- An Alibaba Cloud Model Studio API key ([how to get one](#getting-an-api-key))

### 1. Clone the repository

```bash
git clone https://github.com/TseKang/Pixel-Alchemist.git
cd Pixel-Alchemist
```

### 2. Start the backend

```bash
cd backend

# (Optional) create a conda environment
conda create -n Pixel python=3.10 -y
conda activate Pixel

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and fill in DASHSCOPE_API_KEY and WORKSPACE_ID

# Start the server
python -m app.main
```

- Backend: http://localhost:8001
- API docs (Swagger): http://localhost:8001/docs

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at http://localhost:3000, with API requests proxied to the backend automatically.

## Configuration

Available options in `backend/.env`:

| Option | Description | Default |
|--------|-------------|---------|
| `DASHSCOPE_API_KEY` | Alibaba Cloud Model Studio API key (**required**) | - |
| `WORKSPACE_ID` | Model Studio workspace ID (required by qwen-image) | - |
| `DEFAULT_MODEL` | Generation model | `qwen-image-3.0-pro` |
| `HOST` / `PORT` | Server bind address / port | `0.0.0.0` / `8001` |
| `UPLOAD_DIR` / `OUTPUT_DIR` | Upload / output directories | `./uploads` / `./outputs` |
| `MAX_UPLOAD_SIZE` | Max upload size in bytes | `10485760` (10MB) |

> Note: `qwen-image-3.0-pro` supports image-to-image; the base `qwen-image-3.0` model may not accept reference images.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/generate` | Submit a generation task (reference image + action prompt + options) |
| GET | `/api/task/{task_id}` | Query task status and result |
| GET | `/api/download/sprite/{task_id}` | Download the sprite sheet |
| GET | `/api/download/frame/{task_id}/{frame_index}` | Download a single frame PNG |
| GET | `/api/download/frames/{task_id}` | Download all frames as a ZIP |
| GET | `/api/palettes` | List built-in color palettes |

### Generation Options

| Parameter | Description | Values / Default |
|-----------|-------------|------------------|
| `action_prompt` | Action description (required) | 1-500 characters |
| `frame_count` | Number of animation frames | 4-6, default `4` |
| `canvas_size` | Canvas size | default `64x64` |
| `animation_type` | Animation type | `loop` / `oneshot` |
| `style` | Visual style | `cute` / `cool` / `retro` |

## Project Structure

```
Pixel-Alchemist/
├── frontend/                  # React frontend
│   └── src/
│       ├── components/        # Upload, input, and result display components
│       └── services/          # API client
├── backend/                   # FastAPI backend
│   ├── app/
│   │   ├── api/               # Route layer
│   │   ├── services/          # Prompt building / image generation / sprite assembly
│   │   ├── utils/             # Image processing utilities (pixelation, etc.)
│   │   ├── models/            # Pydantic data models
│   │   └── config.py          # Configuration management
│   └── .env.example           # Environment variable template
├── requirement.md             # Requirements doc (Chinese)
└── README.md
```

## Getting an API Key

1. Visit [Alibaba Cloud Model Studio](https://bailian.console.aliyun.com) and sign up / log in
2. Enable the Tongyi Wanxiang (image generation) service
3. Create an API key in the console and set it as `DASHSCOPE_API_KEY` in `backend/.env`
4. Find your workspace ID in workspace management and set it as `WORKSPACE_ID`

## License

[MIT](https://opensource.org/licenses/MIT)
