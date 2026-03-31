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


class TestParametersPanel(unittest.TestCase):
    """ParametersPanel 行为测试"""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_manual_white_balance_disabled_without_raw(self):
        panel = ParametersPanel(Translator("zh_CN"))
        panel.combo_white_balance.setCurrentIndex(3)

        panel.set_has_raw_files(False)

        self.assertEqual(panel.combo_white_balance.currentIndex(), 0)
        self.assertFalse(panel.combo_white_balance.model().item(3).isEnabled())
        self.assertFalse(panel.spin_color_temperature.isEnabled())
        self.assertTrue(panel.spin_color_temperature.isHidden())

    def test_manual_white_balance_enabled_with_raw(self):
        panel = ParametersPanel(Translator("zh_CN"))

        panel.set_has_raw_files(True)
        panel.combo_white_balance.setCurrentIndex(3)

        self.assertTrue(panel.combo_white_balance.model().item(3).isEnabled())
        self.assertTrue(panel.spin_color_temperature.isEnabled())
        self.assertFalse(panel.spin_color_temperature.isHidden())

    def test_default_white_balance_is_manual_3800k(self):
        panel = ParametersPanel(Translator("zh_CN"))

        self.assertEqual(panel.get_white_balance(), "manual")
        self.assertEqual(panel.get_color_temperature(), 3800)
        self.assertFalse(panel.spin_color_temperature.isHidden())


if __name__ == "__main__":
    unittest.main()
