"""
ParametersPanel 测试
"""

import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from i18n.translator import Translator
from ui.panels.parameters_panel import ParametersPanel
from core.stacking_engine import StackMode


class TestParametersPanel(unittest.TestCase):
    """ParametersPanel 行为测试"""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_default_stack_mode_is_lighten(self):
        """默认堆栈模式应为星轨（Lighten）"""
        panel = ParametersPanel(Translator("zh_CN"))
        self.assertEqual(panel.get_stack_mode(), StackMode.LIGHTEN)

    def test_comet_tail_hidden_in_lighten_mode(self):
        """星轨模式下彗星尾巴选项应隐藏"""
        panel = ParametersPanel(Translator("zh_CN"))
        panel.combo_stack_mode.setCurrentIndex(0)  # Lighten
        self.assertTrue(panel.label_comet_tail.isHidden())
        self.assertTrue(panel.combo_comet_tail.isHidden())

    def test_comet_tail_visible_in_comet_mode(self):
        """彗星模式下彗星尾巴选项应显示"""
        panel = ParametersPanel(Translator("zh_CN"))
        panel.combo_stack_mode.setCurrentIndex(1)  # Comet
        self.assertFalse(panel.label_comet_tail.isHidden())
        self.assertFalse(panel.combo_comet_tail.isHidden())

    def test_gap_filling_enabled_by_default(self):
        """间隔填充默认应启用"""
        panel = ParametersPanel(Translator("zh_CN"))
        self.assertTrue(panel.is_gap_filling_enabled())

    def test_timelapse_disabled_by_default(self):
        """星轨延时和银河延时默认应关闭"""
        panel = ParametersPanel(Translator("zh_CN"))
        self.assertFalse(panel.is_timelapse_enabled())
        self.assertFalse(panel.is_simple_timelapse_enabled())

    def test_comet_fade_factor_values(self):
        """彗星衰减因子映射正确"""
        panel = ParametersPanel(Translator("zh_CN"))
        panel.combo_comet_tail.setCurrentIndex(0)
        self.assertEqual(panel.get_comet_fade_factor(), 0.96)
        panel.combo_comet_tail.setCurrentIndex(1)
        self.assertEqual(panel.get_comet_fade_factor(), 0.97)
        panel.combo_comet_tail.setCurrentIndex(2)
        self.assertEqual(panel.get_comet_fade_factor(), 0.98)


if __name__ == "__main__":
    unittest.main()
