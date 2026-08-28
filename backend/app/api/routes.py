from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import Optional
import asyncio
import base64
import uuid
from pathlib import Path

from ..models.schemas import GenerateRequest, TaskResponse, TaskResult
from ..services.task_manager import TaskManager
from ..services.image_generator import ImageGenerator
from ..services.sprite_assembler import SpriteAssembler
from ..config import settings

router = APIRouter()

# 初始化服务
task_manager = TaskManager()
image_generator = ImageGenerator(api_key=settings.dashscope_api_key)
sprite_assembler = SpriteAssembler(output_dir=settings.output_dir)


@router.post("/generate", response_model=TaskResponse)
async def generate_animation(
    reference_image: Optional[UploadFile] = File(default=None),
    action_prompt: str = Form(...),
    frame_count: int = Form(default=4),
    canvas_size: str = Form(default="64x64"),
    animation_type: str = Form(default="loop"),
    style: str = Form(default="cute")
):
    """提交像素动画生成任务"""

    # 验证帧数
    if frame_count < 4 or frame_count > 6:
        raise HTTPException(status_code=400, detail="帧数必须在 4-6 之间")

    # 保存参考图
    reference_path = None
    if reference_image:
        # 验证文件大小
        content = await reference_image.read()
        if len(content) > settings.max_upload_size:
            raise HTTPException(status_code=400, detail="文件大小超过限制")

        # 保存文件
        ext = Path(reference_image.filename).suffix or ".png"
        reference_path = settings.upload_dir / f"{uuid.uuid4()}{ext}"
        with open(reference_path, "wb") as f:
            f.write(content)

    # 创建任务
    task_id = str(uuid.uuid4())
    task_manager.create_task(task_id, {
        "action_prompt": action_prompt,
        "frame_count": frame_count,
        "canvas_size": canvas_size,
        "animation_type": animation_type,
        "style": style,
        "reference_path": str(reference_path) if reference_path else None,
    })

    # 异步处理任务
    asyncio.create_task(process_generation_task(
        task_id=task_id,
        action_prompt=action_prompt,
        frame_count=frame_count,
        canvas_size=canvas_size,
        animation_type=animation_type,
        style=style,
        reference_path=str(reference_path) if reference_path else None,
    ))

    return TaskResponse(
        task_id=task_id,
        status="processing",
        message="任务已提交，正在生成..."
    )


async def process_generation_task(
    task_id: str,
    action_prompt: str,
    frame_count: int,
    canvas_size: str,
    animation_type: str,
    style: str,
    reference_path: Optional[str] = None,
):
    """处理生成任务"""
    import traceback
    try:
        task_manager.update_status(task_id, "processing")
        print(f"[{task_id}] 开始处理，构建 prompts...")

        # 1. 构建每帧的 Prompt
        from ..services.prompt_builder import PromptBuilder
        prompt_builder = PromptBuilder()
        frame_prompts = prompt_builder.build_prompts(
            action_prompt=action_prompt,
            frame_count=frame_count,
            style=style,
            animation_type=animation_type,
        )
        print(f"[{task_id}] 生成 {len(frame_prompts)} 个 prompts")

        # 2. 生成每帧图片（每帧都以原始参考图为准，避免链式风格漂移）
        frame_paths = await image_generator.generate_animation_frames(
            prompts=frame_prompts,
            reference_image=reference_path
        )
        print(f"[{task_id}] 生成 {len(frame_paths)} 张图片: {frame_paths}")

        # 3. 拼接 Sprite Sheet
        # 注意：不做任何像素化/调色板/透明背景后处理，直接使用 AI 生成的原图
        print(f"[{task_id}] 拼接 Sprite Sheet")
        task_output_dir = settings.output_dir / task_id
        task_output_dir.mkdir(parents=True, exist_ok=True)

        sprite_assembler_task = SpriteAssembler(output_dir=task_output_dir)
        sprite_sheet_path = sprite_assembler_task.create_sprite_sheet(
            frame_paths=frame_paths,
        )
        print(f"[{task_id}] Sprite Sheet: {sprite_sheet_path}")

        # 4. 提取调色板（仅用于前端展示，不影响图片本身）
        palette = sprite_assembler_task.extract_palette(frame_paths[0])
        print(f"[{task_id}] 调色板: {palette}")

        # 5. 更新任务状态
        recommended_interval = 150 if animation_type == "loop" else 200
        task_manager.complete_task(task_id, {
            "frames": frame_paths,
            "sprite_sheet": sprite_sheet_path,
            "palette": palette,
            "animation_params": {
                "frame_count": frame_count,
                "frame_size": canvas_size,
                "recommended_interval_ms": recommended_interval,
                "is_loop": animation_type == "loop"
            }
        })
        print(f"[{task_id}] 完成!")

    except Exception as e:
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"[{task_id}] 失败: {error_msg}")
        task_manager.fail_task(task_id, str(e))


@router.get("/task/{task_id}", response_model=TaskResult)
async def get_task_status(task_id: str):
    """查询任务状态"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    result = task.get("result") or {}
    return TaskResult(
        task_id=task_id,
        status=task["status"],
        frames=result.get("frames", []),
        sprite_sheet=result.get("sprite_sheet", ""),
        palette=result.get("palette", []),
        animation_params=result.get("animation_params"),
        error=task.get("error")
    )


@router.get("/download/sprite/{task_id}")
async def download_sprite_sheet(task_id: str):
    """下载 Sprite Sheet"""
    task = task_manager.get_task(task_id)
    if not task or task["status"] != "completed":
        raise HTTPException(status_code=404, detail="任务不存在或未完成")

    sprite_path = task["result"].get("sprite_sheet")
    if not sprite_path or not Path(sprite_path).exists():
        raise HTTPException(status_code=404, detail="Sprite Sheet 不存在")

    return FileResponse(
        path=sprite_path,
        media_type="image/png",
        filename=f"sprite_{task_id}.png"
    )


@router.get("/download/frame/{task_id}/{frame_index}")
async def download_frame(task_id: str, frame_index: int):
    """下载单帧 PNG"""
    task = task_manager.get_task(task_id)
    if not task or task["status"] != "completed":
        raise HTTPException(status_code=404, detail="任务不存在或未完成")

    frame_paths = task["result"].get("frames", [])
    if frame_index < 0 or frame_index >= len(frame_paths):
        raise HTTPException(status_code=404, detail="帧索引不存在")

    frame_path = frame_paths[frame_index]
    if not Path(frame_path).exists():
        raise HTTPException(status_code=404, detail="帧图片不存在")

    return FileResponse(
        path=frame_path,
        media_type="image/png",
        filename=f"frame_{frame_index + 1:02d}.png"
    )


@router.get("/download/frames/{task_id}")
async def download_frames(task_id: str):
    """下载逐帧 PNG (ZIP)"""
    import zipfile
    import tempfile

    task = task_manager.get_task(task_id)
    if not task or task["status"] != "completed":
        raise HTTPException(status_code=404, detail="任务不存在或未完成")

    frame_paths = task["result"].get("frames", [])
    if not frame_paths:
        raise HTTPException(status_code=404, detail="帧图片不存在")

    # 创建临时 ZIP 文件 (放在 output_dir 下，便于与任务一起清理)
    task_output_dir = settings.output_dir / task_id
    task_output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = task_output_dir / f"frames_{task_id}.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, frame_path in enumerate(frame_paths):
            frame_name = f"frame_{i+1:02d}.png"
            zf.write(frame_path, frame_name)

    return FileResponse(
        path=str(zip_path),
        media_type="application/zip",
        filename=f"frames_{task_id}.zip"
    )


@router.get("/palettes")
async def get_palettes():
    """获取预设调色板列表"""
    return {
        "palettes": [
            {
                "name": "复古游戏",
                "colors": ["#1a1a2e", "#16213e", "#0f3460", "#e94560", "#533483"]
            },
            {
                "name": "可爱粉",
                "colors": ["#ff6b9d", "#c44569", "#f78fb3", "#3dc1d3", "#e056a0"]
            },
            {
                "name": "森林绿",
                "colors": ["#2d6a4f", "#40916c", "#52b788", "#74c69d", "#95d5b2"]
            },
            {
                "name": "赛博朋克",
                "colors": ["#0d0221", "#0f084b", "#26408b", "#a6cfd5", "#c2e7d9"]
            },
            {
                "name": "日落橙",
                "colors": ["#ff4800", "#ff5400", "#ff6000", "#ff6d00", "#ff7900"]
            }
        ]
    }
