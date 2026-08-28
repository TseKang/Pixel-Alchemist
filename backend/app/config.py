from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# .env 文件路径 (相对于 config.py 所在目录)
ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
    )

    # API Key (从 .env 文件读取，请勿在此硬编码)
    dashscope_api_key: str = ""

    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8001

    # 文件存储
    upload_dir: Path = Path("./uploads")
    output_dir: Path = Path("./outputs")

    # 最大上传文件大小 (字节) - 10MB
    max_upload_size: int = 10 * 1024 * 1024

    # AI 模型配置
    default_model: str = "qwen-image-3.0"
    default_image_size: str = "1024*1024"
    workspace_id: str = ""  # qwen-image 需要


settings = Settings()

# 确保目录存在
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.output_dir.mkdir(parents=True, exist_ok=True)
