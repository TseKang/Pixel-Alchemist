"""
Prompt 构建器 - 将上传照片中的人物转化为Q版像素动画
核心原则：
1. 第一帧：将照片人物转化为Q版像素角色
2. 后续帧：保持同一角色，只改变姿态
"""
from typing import List


class FramePrompt:
    """单帧 Prompt 数据类"""
    def __init__(self, frame_index: int, description: str, prompt: str):
        self.frame_index = frame_index
        self.description = description
        self.prompt = prompt


# 风格关键词映射
_STYLE_KEYWORDS = {
    "cute": "Q版可爱风格，大头小身比例，圆润线条，明亮柔和的色彩",
    "cool": "冷酷帅气风格，正常头身比例，锐利线条，高对比度冷色调",
    "retro": "复古8位机风格，复古调色板，颗粒感，参考FC/红白机像素游戏",
}

# 动画类型关键词映射
_ANIMATION_TYPE_KEYWORDS = {
    "loop": "循环动画，首尾姿态衔接自然",
    "oneshot": "单次动画，起始姿态静止，最后姿态稳定收尾",
}

# 人体结构完整性约束（所有帧通用）
# 防止模型生成"躯干直接接脚、无腿部"等结构缺失
_BODY_STRUCTURE_CONSTRAINT = (
    "必须是完整人体结构，依次包含头部、躯干、大腿、小腿、双脚，"
    "符合正常人体比例，不能出现躯干下方直接接脚、缺失大腿或小腿等结构错误；"
    "若参考图中人物身体部位被遮挡或截断，请按正常人体比例合理补全，"
    "不得照搬缺失状态"
)

# 角色外观一致性约束（用于后续帧）
_APPEARANCE_CONSTRAINT = (
    "保持与第一帧完全相同的角色外观、发型发色、服装款式、服装颜色、身材比例"
)


class PromptBuilder:
    """照片中人物 → Q版像素动画 Prompt 生成器"""

    def build_prompts(
        self,
        action_prompt: str,
        frame_count: int = 4,
        style: str = "cute",
        animation_type: str = "loop",
    ) -> List[FramePrompt]:
        """
        生成每帧的 Prompt

        Args:
            action_prompt: 用户输入的动作描述
            frame_count: 帧数 (4-6)
            style: 风格 (cute/cool/retro)
            animation_type: 动画类型 (loop/oneshot)

        Returns:
            每帧的 Prompt 列表
        """
        style_keywords = _STYLE_KEYWORDS.get(style, _STYLE_KEYWORDS["cute"])
        anim_keywords = _ANIMATION_TYPE_KEYWORDS.get(
            animation_type, _ANIMATION_TYPE_KEYWORDS["loop"]
        )

        frame_descriptions = self._split_action_to_frames(action_prompt, frame_count)

        frame_prompts = []
        for i, desc in enumerate(frame_descriptions):
            if i == 0:
                # 第一帧：将照片中的人物转化为像素风格
                # 保留面部/发型/服装等特征，但人体结构必须完整、比例正常
                full_prompt = (
                    f"参考图是一张人物照片。请保留参考图中人物的面部特征、发型、发色、服装款式（衣服裤子等）、服装颜色，"
                    f"将其转化为像素艺术风格的角色立绘，"
                    f"{style_keywords}，"
                    f"{_BODY_STRUCTURE_CONSTRAINT}，"
                    f"全身可见，从头顶到脚底完整呈现，"
                    f"透明背景，"
                    f"无抗锯齿，清晰像素边缘，有限调色板，"
                    f"角色姿态：{desc}"
                )
            else:
                # 后续帧：保持同一角色外观，只改变姿态
                full_prompt = (
                    f"像素艺术风格角色立绘，{style_keywords}，"
                    f"{_APPEARANCE_CONSTRAINT}，"
                    f"{_BODY_STRUCTURE_CONSTRAINT}，"
                    f"全身可见，从头顶到脚底完整呈现，"
                    f"{anim_keywords}，"
                    f"透明背景，"
                    f"无抗锯齿，清晰像素边缘，有限调色板，"
                    f"角色姿态：{desc}"
                )
            frame_prompts.append(FramePrompt(
                frame_index=i,
                description=desc,
                prompt=full_prompt
            ))

        return frame_prompts

    def _split_action_to_frames(self, action_prompt: str, frame_count: int) -> List[str]:
        """将动作描述拆解为多个帧描述"""
        if frame_count == 4:
            return self._split_4_frames(action_prompt)
        elif frame_count == 5:
            return self._split_5_frames(action_prompt)
        else:
            return self._split_6_frames(action_prompt)

    def _split_4_frames(self, action: str) -> List[str]:
        """4帧拆解：站立 → 动作开始 → 动作顶点 → 回到站立"""
        return [
            f"角色正常站立，{action}的起始姿态",
            f"角色正在{action}，动作轻微展开",
            f"角色{action}到顶点，动作最明显",
            f"角色回到站立，准备循环",
        ]

    def _split_5_frames(self, action: str) -> List[str]:
        """5帧拆解：站立 → 开始 → 顶点 → 缓冲 → 恢复"""
        return [
            f"角色正常站立，{action}的起始姿态",
            f"角色开始{action}，预备阶段",
            f"角色{action}到顶点，主要动作姿态",
            f"角色{action}缓冲，动作回收",
            f"角色恢复到站立姿态",
        ]

    def _split_6_frames(self, action: str) -> List[str]:
        """6帧拆解：更流畅的动画"""
        return [
            f"角色正常站立，{action}的起始姿态",
            f"角色开始{action}，预备阶段",
            f"角色{action}，动作逐渐展开",
            f"角色{action}到顶点，动作最明显",
            f"角色{action}缓冲，开始回收",
            f"角色恢复到站立姿态",
        ]
