"""
预览面板
负责预览图像显示、日志输出和操作按钮
"""

import numpy as np
from pathlib import Path
from typing import Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
from i18n.translator import Translator
from ui.styles import (
    PRIMARY_BUTTON_STYLE,
    SECONDARY_BUTTON_STYLE,
    TITLE_LABEL_STYLE,
    SUBTITLE_LABEL_STYLE,
    PREVIEW_AREA_STYLE,
    LOG_TEXT_STYLE,
)
from utils.settings import get_settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

try:
    from astropy.visualization import ZScaleInterval, AsinhStretch
    _ASTROPY_AVAILABLE = True
except ImportError:
    _ASTROPY_AVAILABLE = False
    logger.warning("astropy 未安装，预览将使用百分位数拉伸作为备用")


class PreviewPanel(QWidget):
    """预览面板"""

    # 信号定义
    # (移除了播放视频和打开输出目录的信号，这些功能已移至文件列表面板)

    def __init__(self, translator: Translator, parent=None):
        super().__init__(parent)
        self.tr = translator

        # 预览缓存（用于亮度拉伸优化）
        self._preview_cache_valid = False
        self._preview_stretch_cache = None

        self._init_ui()

    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        self.setLayout(layout)

        # 标题栏（带 Logo）
        title_layout = QHBoxLayout()
        title_layout.addStretch()

        # 标题文字（第一部分）
        title_part1 = QLabel("彗星星轨")
        title_part1.setStyleSheet(TITLE_LABEL_STYLE)
        title_layout.addWidget(title_part1)

        # Logo 图标（放在中间）
        logo_path = Path(__file__).parent.parent.parent / "resources" / "logo.png"
        if logo_path.exists():
            logo_label = QLabel()
            logo_pixmap = QPixmap(str(logo_path)).scaled(
                32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            logo_label.setPixmap(logo_pixmap)
            title_layout.addWidget(logo_label)

        # 标题文字（第二部分）
        title_part2 = QLabel("一键生成星轨照片与延时视频")
        title_part2.setStyleSheet(TITLE_LABEL_STYLE)
        title_layout.addWidget(title_part2)
        title_layout.addStretch()

        layout.addLayout(title_layout)

        # 预览区域（3:2 比例，更接近照片原始比例）
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet(PREVIEW_AREA_STYLE)
        self.preview_label.setMinimumSize(800, 533)  # 3:2 比例最小尺寸
        # 不设置最大高度，允许随窗口放大

        # 加载默认背景图片
        bg_path = Path(__file__).parent.parent.parent / "resources" / "bg.jpg"
        if bg_path.exists():
            bg_pixmap = QPixmap(str(bg_path))
            # 缩放到合适大小，保持宽高比
            scaled_bg = bg_pixmap.scaled(
                800, 533, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled_bg)
        else:
            # 如果背景图不存在，显示占位文字
            self.preview_label.setText(self.tr.tr("drop_files_here"))

        layout.addWidget(self.preview_label, stretch=1)  # 拉伸因子让预览区域占据剩余空间

        # 添加日志输出区域
        log_label = QLabel(f"📋 {self.tr.tr('processing_log')}")
        log_label.setStyleSheet(SUBTITLE_LABEL_STYLE)
        layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFixedHeight(120)  # 固定高度 120px，避免遮挡预览
        self.log_text.setStyleSheet(LOG_TEXT_STYLE)

        # 设置默认使用说明
        self._set_default_instructions()

        layout.addWidget(self.log_text)  # 不添加拉伸因子，保持固定大小

    @staticmethod
    def _stretch_for_preview(image: np.ndarray, settings) -> np.ndarray:
        """
        将 uint16 图像拉伸为适合显示的 uint8。

        优先使用 astropy ZScaleInterval + AsinhStretch 组合：
        - ZScale 自动找最优显示范围（天文标准，对星野效果极好）
        - AsinhStretch 非线性拉伸，保留亮星细节的同时提亮暗星

        若 astropy 不可用则回退到简单百分位数拉伸。
        """
        if _ASTROPY_AVAILABLE:
            try:
                # ZScale 基于亮度通道计算显示范围（对多通道 RGB 更准确）
                lum = np.mean(image, axis=2).astype(np.float32) if image.ndim == 3 else image.astype(np.float32)
                vmin, vmax = ZScaleInterval().get_limits(lum)
                scale = max(float(vmax - vmin), 1.0)

                # 归一化到 [0, 1]
                img_float = np.clip(
                    (image.astype(np.float32) - vmin) / scale, 0.0, 1.0
                )

                # AsinhStretch：a=0.1 对星野广角场景效果好
                # a 越小拉伸越激进（暗区提亮越多），0.05~0.2 均可
                img_stretched = AsinhStretch(a=0.1)(img_float)

                logger.debug(f"ZScale+Asinh 拉伸: vmin={vmin:.0f}, vmax={vmax:.0f}")
                return (np.clip(img_stretched, 0.0, 1.0) * 255).astype(np.uint8)

            except Exception as e:
                logger.debug(f"astropy 拉伸失败，回退到百分位数: {e}")

        # 回退：简单百分位数拉伸
        p_low, p_high = settings.get_preview_percentiles()
        v_low = np.percentile(image, p_low)
        v_high = np.percentile(image, p_high)
        scale = max(float(v_high - v_low), 1.0)
        return np.clip((image.astype(np.float32) - v_low) / scale * 255, 0, 255).astype(np.uint8)

    def update_preview(self, image: np.ndarray):
        """更新预览图像（自动曝光优化）"""
        import cv2

        # 从配置获取预览参数
        settings = get_settings()
        max_size = settings.get_preview_max_size()

        # 先缩放再做亮度拉伸，大幅提升速度
        h, w = image.shape[:2]

        # 先缩小图像以加快后续处理
        if max(h, w) > max_size:
            scale = max_size / max(h, w)
            new_h, new_w = int(h * scale), int(w * scale)
            image_small = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        else:
            image_small = image

        # 转换为 8-bit 用于显示
        if image_small.dtype == np.uint16:
            img_8bit = self._stretch_for_preview(image_small, settings)
        else:
            img_8bit = image_small

        # 转换为 QPixmap
        h, w, c = img_8bit.shape
        bytes_per_line = c * w
        q_img = QImage(bytes(img_8bit.tobytes()), w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)

        # 缩放到 label 大小，保持宽高比
        label_size = self.preview_label.size()
        scaled_pixmap = pixmap.scaled(
            label_size,
            Qt.KeepAspectRatio,  # 保持宽高比
            Qt.SmoothTransformation  # 平滑缩放
        )
        self.preview_label.setPixmap(scaled_pixmap)

        # 强制刷新UI
        self.preview_label.update()
        QApplication.processEvents()


    def append_log(self, message: str):
        """添加日志消息到日志区域"""
        self.log_text.append(message)
        # 自动滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def clear_log(self):
        """清空日志"""
        self.log_text.clear()

    def reset_preview_cache(self):
        """重置预览缓存（新处理开始时调用）"""
        self._preview_cache_valid = False
        self._preview_stretch_cache = None

    def show_placeholder(self):
        """显示默认背景图片"""
        self.preview_label.clear()
        # 重新加载默认背景图片
        bg_path = Path(__file__).parent.parent.parent / "resources" / "bg.jpg"
        if bg_path.exists():
            bg_pixmap = QPixmap(str(bg_path))
            # 缩放到当前 label 大小，保持宽高比
            label_size = self.preview_label.size()
            scaled_bg = bg_pixmap.scaled(
                label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled_bg)
        else:
            # 如果背景图不存在，显示占位文字
            self.preview_label.setText(self.tr.tr("drop_files_here"))

    def _set_default_instructions(self):
        """设置默认使用说明"""
        instructions = """欢迎使用彗星星轨！快速开始：
1. 点击「选择目录」选择包含 RAW 文件的文件夹
2. 选择堆栈模式（Lighten 星轨 / Comet 彗星效果）
3. 配置参数（白平衡、延时视频等）
4. 点击「开始合成」，等待处理完成
5. 完成后自动打开输出目录查看结果"""
        self.log_text.setPlainText(instructions)
