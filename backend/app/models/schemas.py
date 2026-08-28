from pydantic import BaseModel, Field
from typing import Optional


class GenerateRequest(BaseModel):
    """生成请求"""
    reference_image: Optional[str] = Field(
        default=None,
        description="Base64 编码的参考图"
    )
    action_prompt: str = Field(
        ...,
        description="动作描述，如'害羞地低头捏裙摆'",
        min_length=1,
        max_length=500
    )
    frame_count: int = Field(
        default=4,
        ge=4,
        le=6,
        description="帧数 (4-6)"
    )
    canvas_size: str = Field(
        default="64x64",
        description="画布尺寸"
    )
    animation_type: str = Field(
        default="loop",
        description="动画类型: loop / oneshot"
    )
    style: str = Field(
        default="cute",
        description="风格: cute / cool / retro"
    )


class AnimationParams(BaseModel):
    """动画参数"""
    frame_count: int
    frame_size: str
    recommended_interval_ms: int
    is_loop: bool


class TaskResponse(BaseModel):
    """任务响应"""
    task_id: str
    status: str  # pending / processing / completed / failed
    message: str


class TaskResult(BaseModel):
    """任务结果"""
    task_id: str
    status: str
    frames: list[str] = []
    sprite_sheet: str = ""
    palette: list[str] = []
    animation_params: Optional[AnimationParams] = None
    error: Optional[str] = None
