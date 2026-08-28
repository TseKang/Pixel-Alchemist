"""
图片工具函数
"""
from PIL import Image
from typing import Tuple, Optional
import base64
import io


def resize_image(
    image_path: str,
    target_size: Tuple[int, int],
    keep_aspect: bool = True
) -> str:
    """
    调整图片大小

    Args:
        image_path: 原图路径
        target_size: 目标尺寸 (宽, 高)
        keep_aspect: 是否保持宽高比

    Returns:
        调整后图片的路径
    """
    img = Image.open(image_path).convert("RGBA")

    if keep_aspect:
        img.thumbnail(target_size, Image.NEAREST)
        # 创建透明背景并居中粘贴
        background = Image.new("RGBA", target_size, (0, 0, 0, 0))
        offset = (
            (target_size[0] - img.size[0]) // 2,
            (target_size[1] - img.size[1]) // 2
        )
        background.paste(img, offset, img)
        img = background
    else:
        img = img.resize(target_size, Image.NEAREST)

    # 保存
    output_path = image_path
    img.save(output_path, "PNG")
    return output_path


def image_to_base64(image_path: str) -> str:
    """将图片转为 Base64 字符串"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def base64_to_image(base64_str: str, output_path: str):
    """将 Base64 字符串保存为图片"""
    image_data = base64.b64decode(base64_str)
    with open(output_path, "wb") as f:
        f.write(image_data)


def create_transparent_canvas(size: Tuple[int, int]) -> Image.Image:
    """创建透明画布"""
    return Image.new("RGBA", size, (0, 0, 0, 0))


def pixelize_frame(
    image_path: str,
    target_size: Optional[Tuple[int, int]] = None,
    max_colors: int = 16,
    background_color: Optional[Tuple[int, int, int, int]] = None,
) -> str:
    """
    将一张 AI 生成的"像素风格"图做像素艺术化后处理。

    处理流程：
    1. 若指定 target_size，用 LANCZOS 缩放到目标分辨率（高质量降采样，
       保留人物细节，不是 NEAREST 一步到位的粗暴缩小）
    2. 用 FASTOCTREE 调色板量化到 max_colors 色（像素艺术观感）
    3. 抠掉接近纯白/纯黑的背景，转成透明通道
       (qwen-image 输出的"透明背景"实际多为白底/黑底，这里兜底处理)
    4. 保存覆盖原文件，返回路径

    Args:
        image_path: 输入图片路径
        target_size: 目标像素分辨率 (宽, 高)；None 表示保留原分辨率
        max_colors: 调色板颜色数
        background_color: 若指定，则将该颜色作为背景并抠为透明；否则自动判断白/黑底
    Returns:
        处理后图片的路径（覆盖原文件）
    """
    img = Image.open(image_path).convert("RGBA")

    # 1. 降采样到目标分辨率（若指定）
    # 用 LANCZOS 高质量缩放，避免 NEAREST 把 2048→64 一步丢细节
    if target_size is not None:
        img = img.resize(target_size, Image.LANCZOS)

    # 2. 调色板量化（先转 RGB 量化，再转回 RGBA 保留 alpha）
    rgb = img.convert("RGB")
    quantized = rgb.quantize(colors=max_colors, method=Image.Quantize.FASTOCTREE)
    quantized_rgba = quantized.convert("RGBA")

    # 用原图 alpha 作为掩码，避免量化把透明区域也压成某色
    alpha = img.split()[-1]
    quantized_rgba.putalpha(alpha)

    # 3. 背景透明化处理
    if background_color is not None:
        _make_color_transparent(quantized_rgba, background_color, tolerance=24)
    else:
        # 自动尝试白底和黑底
        _make_color_transparent(quantized_rgba, (255, 255, 255, 255), tolerance=32)
        _make_color_transparent(quantized_rgba, (0, 0, 0, 255), tolerance=24)

    # 4. 保存覆盖原文件
    quantized_rgba.save(image_path, "PNG")
    return image_path


def _make_color_transparent(
    img: Image.Image,
    target: Tuple[int, int, int, int],
    tolerance: int = 24,
):
    """将 img 中与 target 颜色接近的像素 alpha 置为 0（原地修改）。
    纯 Pillow 实现，不依赖 numpy。
    """
    # 生成掩码：距离小于阈值的像素位置为 255（要变透明）
    img_rgba = img.convert("RGBA")
    # 用 Image.point 通道级比较太复杂，这里用 EvaluatePoint + 通道合成
    # 直接用 getdata 遍历更直观
    px = img_rgba.load()
    width, height = img_rgba.size
    tr, tg, tb = target[0], target[1], target[2]
    threshold = tolerance * 3
    transparent = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    tpx = transparent.load()
    for y in range(height):
        for x in range(width):
            r, g, b, a = px[x, y]
            if abs(r - tr) + abs(g - tg) + abs(b - tb) <= threshold:
                tpx[x, y] = (r, g, b, 0)
            else:
                tpx[x, y] = (r, g, b, a)
    img.paste(transparent)


def apply_pixel_grid(
    image: Image.Image,
    grid_size: int = 8
) -> Image.Image:
    """
    应用像素网格效果（用于预览）

    Args:
        image: 原图
        grid_size: 网格大小

    Returns:
        处理后的图片
    """
    width, height = image.size
    pixels = image.load()

    for y in range(0, height, grid_size):
        for x in range(0, width, grid_size):
            # 获取网格内平均颜色
            r_sum, g_sum, b_sum, a_sum, count = 0, 0, 0, 0, 0
            for dy in range(min(grid_size, height - y)):
                for dx in range(min(grid_size, width - x)):
                    if x + dx < width and y + dy < height:
                        r, g, b, a = pixels[x + dx, y + dy]
                        r_sum += r
                        g_sum += g
                        b_sum += b
                        a_sum += a
                        count += 1

            if count > 0:
                avg_color = (
                    r_sum // count,
                    g_sum // count,
                    b_sum // count,
                    a_sum // count
                )
                for dy in range(min(grid_size, height - y)):
                    for dx in range(min(grid_size, width - x)):
                        if x + dx < width and y + dy < height:
                            pixels[x + dx, y + dy] = avg_color

    return image
