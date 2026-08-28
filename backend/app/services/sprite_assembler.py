"""
精灵图拼接服务 - 将多帧图片拼接为 Sprite Sheet
"""
from PIL import Image
from typing import List
from pathlib import Path
import uuid


class SpriteAssembler:
    """精灵图拼接服务"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def create_sprite_sheet(
        self,
        frame_paths: List[str],
        direction: str = "horizontal"
    ) -> str:
        """
        将多帧图片拼接为 Sprite Sheet

        Args:
            frame_paths: 帧图片路径列表
            direction: 排列方向 (horizontal/vertical/grid)

        Returns:
            Sprite Sheet 图片路径
        """
        # 打开所有帧图片
        frames = [Image.open(path).convert("RGBA") for path in frame_paths]

        # 确保所有帧尺寸一致
        frame_width, frame_height = frames[0].size
        for i, frame in enumerate(frames):
            if frame.size != (frame_width, frame_height):
                frames[i] = frame.resize((frame_width, frame_height), Image.NEAREST)

        if direction == "horizontal":
            return self._create_horizontal_sheet(frames, frame_width, frame_height)
        elif direction == "vertical":
            return self._create_vertical_sheet(frames, frame_width, frame_height)
        else:  # grid
            return self._create_grid_sheet(frames, frame_width, frame_height)

    def _create_horizontal_sheet(
        self,
        frames: List[Image.Image],
        frame_width: int,
        frame_height: int
    ) -> str:
        """创建横向 Sprite Sheet"""
        total_width = frame_width * len(frames)
        sprite_sheet = Image.new("RGBA", (total_width, frame_height), (0, 0, 0, 0))

        for i, frame in enumerate(frames):
            sprite_sheet.paste(frame, (i * frame_width, 0), frame)

        # 保存
        output_path = self.output_dir / f"sprite_{uuid.uuid4().hex[:8]}.png"
        sprite_sheet.save(str(output_path), "PNG")

        return str(output_path)

    def _create_vertical_sheet(
        self,
        frames: List[Image.Image],
        frame_width: int,
        frame_height: int
    ) -> str:
        """创建纵向 Sprite Sheet"""
        total_height = frame_height * len(frames)
        sprite_sheet = Image.new("RGBA", (frame_width, total_height), (0, 0, 0, 0))

        for i, frame in enumerate(frames):
            sprite_sheet.paste(frame, (0, i * frame_height), frame)

        # 保存
        output_path = self.output_dir / f"sprite_{uuid.uuid4().hex[:8]}.png"
        sprite_sheet.save(str(output_path), "PNG")

        return str(output_path)

    def _create_grid_sheet(
        self,
        frames: List[Image.Image],
        frame_width: int,
        frame_height: int
    ) -> str:
        """创建网格 Sprite Sheet"""
        import math
        cols = math.ceil(math.sqrt(len(frames)))
        rows = math.ceil(len(frames) / cols)

        total_width = frame_width * cols
        total_height = frame_height * rows
        sprite_sheet = Image.new("RGBA", (total_width, total_height), (0, 0, 0, 0))

        for i, frame in enumerate(frames):
            row = i // cols
            col = i % cols
            sprite_sheet.paste(frame, (col * frame_width, row * frame_height), frame)

        # 保存
        output_path = self.output_dir / f"sprite_{uuid.uuid4().hex[:8]}.png"
        sprite_sheet.save(str(output_path), "PNG")

        return str(output_path)

    def extract_frames(
        self,
        sprite_sheet_path: str,
        frame_width: int,
        frame_height: int
    ) -> List[str]:
        """
        从 Sprite Sheet 拆解出单帧

        Args:
            sprite_sheet_path: Sprite Sheet 路径
            frame_width: 单帧宽度
            frame_height: 单帧高度

        Returns:
            单帧图片路径列表
        """
        sprite_sheet = Image.open(sprite_sheet_path).convert("RGBA")
        sheet_width = sprite_sheet.size[0]

        frame_count = sheet_width // frame_width
        frame_paths = []

        for i in range(frame_count):
            left = i * frame_width
            right = left + frame_width
            frame = sprite_sheet.crop((left, 0, right, frame_height))

            output_path = self.output_dir / f"frame_{uuid.uuid4().hex[:8]}.png"
            frame.save(str(output_path), "PNG")
            frame_paths.append(str(output_path))

        return frame_paths

    def extract_palette(self, image_path: str, max_colors: int = 16) -> List[str]:
        """
        从图片提取调色板

        Args:
            image_path: 图片路径
            max_colors: 最大颜色数

        Returns:
            颜色列表 (16进制格式)
        """
        img = Image.open(image_path).convert("RGBA")

        # 量化颜色 (RGBA 只支持 FAST_OCTREE 和 LIBIMAGEQUANT)
        quantized = img.quantize(colors=max_colors, method=Image.Quantize.FASTOCTREE)
        palette = quantized.getpalette()

        # 转换为16进制颜色
        hex_colors = []
        if palette:
            for i in range(0, min(max_colors * 3, len(palette)), 3):
                r, g, b = palette[i], palette[i+1], palette[i+2]
                hex_colors.append(f"#{r:02x}{g:02x}{b:02x}")

        return hex_colors
