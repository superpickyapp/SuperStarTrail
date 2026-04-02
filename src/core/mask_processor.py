"""
蒙版处理模块

负责加载 PNG 蒙版文件，并将其转换为归一化的 float32 数组。
白色区域（255）= 天空（sky_result），黑色区域（0）= 地景（fg_result）。

蒙版始终由用户在 PS 中对着已旋转的图片制作，导出时方向已正确，
因此这里只做 resize，不施加额外旋转。
"""
import numpy as np
from pathlib import Path
from PIL import Image


class MaskProcessor:
    """PNG 蒙版加载器"""

    @staticmethod
    def load(mask_path: Path, target_shape: tuple) -> np.ndarray:
        """
        加载 PNG 蒙版，resize 到目标尺寸，返回 float32 [0,1] 数组。

        target_shape 应为堆栈图像处理后的形状（已含旋转），
        蒙版本身不做额外旋转——用户在 PS 中看到的已是旋转后的图，
        导出的蒙版方向与最终结果一致。

        Args:
            mask_path:    蒙版 PNG 文件路径
            target_shape: 目标形状 (height, width)，与堆栈图像一致

        Returns:
            float32 数组，形状 (height, width)，值域 [0.0, 1.0]

        Raises:
            FileNotFoundError: 文件不存在
            ValueError:        文件不是 PNG 格式
        """
        mask_path = Path(mask_path)

        if not mask_path.exists():
            raise FileNotFoundError(f"蒙版文件不存在: {mask_path}")

        if mask_path.suffix.lower() != ".png":
            raise ValueError(f"蒙版文件必须是 PNG 格式，当前: {mask_path.suffix}")

        img = Image.open(mask_path).convert("L")  # 转灰度

        # Resize 到目标尺寸（target_shape 已经是旋转后的尺寸）
        target_h, target_w = target_shape
        if img.size != (target_w, target_h):
            img = img.resize((target_w, target_h), Image.LANCZOS)

        return np.array(img, dtype=np.float32) / 255.0
