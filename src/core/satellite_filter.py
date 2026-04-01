"""
卫星/飞机/星链划痕检测模块

工作原理
--------
卫星、飞机、星链在单张曝光中产生横跨大部分画面的长直线轨迹，
而广角镜头下的恒星是点状（或极短弧），两者在空间尺度上差异显著。

对每帧图像单独检测长直亮线（霍夫直线变换），生成像素遮罩后再堆栈，
被遮罩的像素在 Lighten/Comet 堆栈中跳过更新，从而消除划痕。

适用范围
--------
- ✅ 卫星（ISS、各类低轨道卫星）
- ✅ Starlink 星链（通常成串出现）
- ✅ 飞机（机身灯形成连续亮线，闪光灯会断开但仍可检测）
- ✅ 流星（同样是长直线，副作用：流星也会被去除，可接受）
- ❌ 无法去除云层（形状不规则）
"""

import numpy as np
import cv2
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SatelliteFilter:
    """
    卫星/飞机划痕检测器

    Parameters
    ----------
    min_streak_fraction : float
        有效划痕占图像短边的最小比例，默认 0.15（即 6000px 宽的图≥ 900px 的线才算）
        调大 → 更少误报；调小 → 能检测较短的划痕（如帧角落的卫星）
    brightness_percentile : float
        亮度阈值百分位数，高于此百分位才参与检测，默认 97.0
        避免把普通背景噪点误检为划痕
    mask_thickness : int
        遮罩线宽（全分辨率像素），需覆盖划痕实际宽度，默认 24px
    """

    def __init__(
        self,
        min_streak_fraction: float = 0.15,
        brightness_percentile: float = 97.0,
        mask_thickness: int = 24,
    ):
        self.min_streak_fraction = min_streak_fraction
        self.brightness_percentile = brightness_percentile
        self.mask_thickness = mask_thickness

    def detect_streaks(self, image: np.ndarray) -> np.ndarray:
        """
        检测单帧中的卫星/飞机划痕，返回像素遮罩

        Parameters
        ----------
        image : np.ndarray
            输入图像 (H, W, 3)，uint16 或 uint8

        Returns
        -------
        np.ndarray
            bool 类型遮罩 (H, W)，True = 该像素属于划痕
        """
        h, w = image.shape[:2]

        # ── Step 1: 降采样到 1/4 分辨率，加速后续运算 ──────────────────────
        scale = 4
        small_w, small_h = max(w // scale, 1), max(h // scale, 1)

        # 转换为 8-bit 灰度
        if image.dtype == np.uint16:
            img_8bit = (image >> 8).astype(np.uint8)
        else:
            img_8bit = image.astype(np.uint8)

        gray = cv2.cvtColor(img_8bit, cv2.COLOR_RGB2GRAY) if img_8bit.ndim == 3 else img_8bit
        small = cv2.resize(gray, (small_w, small_h), interpolation=cv2.INTER_AREA)

        # ── Step 2: 亮度阈值，只分析足够亮的区域 ───────────────────────────
        thresh_val = float(np.percentile(small, self.brightness_percentile))
        thresh_val = max(thresh_val, 20.0)  # 绝对下限，避免噪点全通过
        _, bright = cv2.threshold(small, thresh_val, 255, cv2.THRESH_BINARY)

        # 轻度膨胀连接相邻亮点（弥合闪光灯飞机的间隙）
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        bright = cv2.dilate(bright, kernel, iterations=1)

        # ── Step 3: Hough 概率直线变换 ──────────────────────────────────────
        min_dim_small = min(small_w, small_h)
        min_length = max(int(min_dim_small * self.min_streak_fraction), 25)
        max_gap = max(int(min_length * 0.15), 8)  # 允许一定间隙（闪光灯飞机）
        hough_threshold = max(int(min_length * 0.6), 20)

        lines = cv2.HoughLinesP(
            bright,
            rho=1,
            theta=np.pi / 180,
            threshold=hough_threshold,
            minLineLength=min_length,
            maxLineGap=max_gap,
        )

        if lines is None:
            return np.zeros((h, w), dtype=bool)

        # ── Step 4: 在缩小图上绘制遮罩 ──────────────────────────────────────
        mask_small = np.zeros((small_h, small_w), dtype=np.uint8)
        thickness_small = max(self.mask_thickness // scale, 2)

        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(mask_small, (x1, y1), (x2, y2), 255, thickness_small)

        # ── Step 5: 放大回原始分辨率 ─────────────────────────────────────────
        mask_full = cv2.resize(mask_small, (w, h), interpolation=cv2.INTER_NEAREST)

        n_streaks = len(lines)
        n_masked_pixels = int(np.sum(mask_full > 0))
        coverage = n_masked_pixels / (h * w) * 100
        logger.info(
            f"🛸 检测到 {n_streaks} 条划痕，遮罩 {n_masked_pixels:,} 像素 ({coverage:.2f}% 画面)"
        )

        return mask_full > 0
