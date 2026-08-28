"""
AI 图片生成服务 - 封装通义万相/通义千问图片生成 API
支持:
- wanx-v1: 使用 ImageSynthesis API
- qwen-image-3.0/qwen-image-3.0-pro: 使用 MultiModalConversation API
"""
import dashscope
from dashscope import ImageSynthesis, MultiModalConversation
from typing import List, Optional
from pathlib import Path
import uuid
import urllib.request
import asyncio
import base64
import io
from concurrent.futures import ThreadPoolExecutor

from ..config import settings


def encode_file_to_base64(file_path: str) -> str:
    """将本地图片转为 base64 data URI"""
    from PIL import Image
    img = Image.open(file_path).convert("RGB")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_b64}"


class ImageGenerator:
    """AI 图片生成服务"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        dashscope.api_key = api_key
        self.executor = ThreadPoolExecutor(max_workers=4)
        # 设置 workspace URL (qwen-image 需要)
        if settings.workspace_id:
            dashscope.base_http_api_url = f'https://{settings.workspace_id}.cn-beijing.maas.aliyuncs.com/api/v1'

    async def generate_frame(
        self,
        prompt: str,
        reference_image: Optional[str] = None,
        size: str = "1024*1024"
    ) -> str:
        """生成单帧图片"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._sync_generate_frame,
            prompt,
            reference_image,
            size
        )

    def _sync_generate_frame(
        self,
        prompt: str,
        reference_image: Optional[str],
        size: str
    ) -> str:
        """同步生成单帧图片"""
        if "qwen-image" in settings.default_model:
            return self._generate_qwen_image(prompt, reference_image)
        else:
            return self._generate_wanx_image(prompt, reference_image, size)

    def _generate_qwen_image(
        self,
        prompt: str,
        reference_image: Optional[str]
    ) -> str:
        """使用 MultiModalConversation API 生成 (qwen-image-3.0-pro)"""
        content = []

        # 添加参考图（必须在 text 之前）
        if reference_image and Path(reference_image).exists():
            img_data_uri = encode_file_to_base64(reference_image)
            content.append({"image": img_data_uri})
            print(f"[DEBUG] 参考图片已添加: {reference_image}, data_uri长度: {len(img_data_uri)}")
        else:
            print(f"[DEBUG] 无参考图片: reference_image={reference_image}")

        # 添加文本 prompt
        content.append({"text": prompt})

        print(f"[DEBUG] 调用模型: {settings.default_model}, prompt前50字: {prompt[:50]}...")

        response = MultiModalConversation.call(
            api_key=self.api_key,
            model=settings.default_model,
            messages=[{
                "role": "user",
                "content": content
            }],
            prompt_extend=False,
        )

        if response.status_code != 200:
            raise Exception(
                f"图片生成失败: {response.code} - {response.message}"
            )

        # 从响应中提取图片 URL
        image_url = response.output.choices[0].message.content[0]["image"]
        print(f"[DEBUG] 生成图片URL: {image_url[:80]}...")

        # 保存到本地
        output_path = settings.output_dir / f"{uuid.uuid4()}.png"
        urllib.request.urlretrieve(image_url, str(output_path))

        return str(output_path)

    def _generate_wanx_image(
        self,
        prompt: str,
        reference_image: Optional[str],
        size: str
    ) -> str:
        """使用 ImageSynthesis API 生成 (wanx-v1)"""
        kwargs = {
            "model": settings.default_model,
            "prompt": prompt,
            "n": 1,
            "size": size,
            "prompt_extend": False,
        }

        # 如果有参考图，统一转为 PNG 后编码为 base64 data URI
        if reference_image and Path(reference_image).exists():
            data_uri = encode_file_to_base64(reference_image)
            kwargs["extra_input"] = {
                "ref_img": data_uri,
                "ref_strength": 0.85,
            }

        response = ImageSynthesis.call(**kwargs)

        if response.status_code != 200:
            raise Exception(
                f"图片生成失败: {response.code} - {response.message}"
            )

        # 下载生成的图片
        result = response.output.results[0]
        image_url = result.url

        # 保存到本地
        output_path = settings.output_dir / f"{uuid.uuid4()}.png"
        urllib.request.urlretrieve(image_url, str(output_path))

        return str(output_path)

    async def generate_animation_frames(
        self,
        prompts: List,
        reference_image: Optional[str] = None,
        chain: bool = True,
    ) -> List[str]:
        """
        批量生成动画帧。

        Args:
            prompts: 每帧 Prompt 列表
            reference_image: 原始参考图路径
            chain: 是否链式生成（每帧参考前一帧）。
                   默认 True，保持人物外观在多帧间的一致性。
        """
        frame_paths = []
        prev_frame = reference_image  # 第一帧用原图参考

        for i, frame_prompt in enumerate(prompts):
            # chain=True 时，每帧参考前一帧，保持人物外观一致
            ref_for_this_frame = prev_frame if chain else reference_image
            path = await self.generate_frame(
                prompt=frame_prompt.prompt,
                reference_image=ref_for_this_frame
            )
            frame_paths.append(path)
            if chain:
                prev_frame = path  # 链式模式下更新为当前帧，供下一帧参考

        return frame_paths
