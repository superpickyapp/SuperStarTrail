"""
堆栈引擎测试
"""

import unittest
import numpy as np
import sys
from threading import Event
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.cancellation import ProcessingCancelledError
from core.stacking_engine import StackingEngine, StackMode


class TestStackingEngine(unittest.TestCase):
    """堆栈引擎测试类"""

    def setUp(self):
        """测试前准备"""
        self.test_images = [
            np.random.randint(0, 65535, (100, 100, 3), dtype=np.uint16)
            for _ in range(5)
        ]

    def test_lighten_mode(self):
        """测试 Lighten 模式"""
        engine = StackingEngine(StackMode.LIGHTEN)

        for img in self.test_images:
            engine.add_image(img)

        result = engine.get_result()

        # 验证结果维度
        self.assertEqual(result.shape, (100, 100, 3))

        # 验证结果数据类型
        self.assertEqual(result.dtype, np.uint16)

        # 验证最大值逻辑
        expected = np.maximum.reduce([img.astype(np.float32) for img in self.test_images])
        np.testing.assert_array_equal(result, expected.astype(np.uint16))

    def test_average_mode(self):
        """测试 Average 模式"""
        engine = StackingEngine(StackMode.AVERAGE)

        for img in self.test_images:
            engine.add_image(img)

        result = engine.get_result()

        # 验证结果维度
        self.assertEqual(result.shape, (100, 100, 3))

        # 验证平均值逻辑
        expected = np.mean([img.astype(np.float32) for img in self.test_images], axis=0)
        np.testing.assert_array_almost_equal(result, expected, decimal=0)

    def test_reset(self):
        """测试重置功能"""
        engine = StackingEngine(StackMode.LIGHTEN)

        engine.add_image(self.test_images[0])
        self.assertEqual(engine.count, 1)

        engine.reset()
        self.assertEqual(engine.count, 0)
        self.assertIsNone(engine.result)

    def test_comet_fade_factor(self):
        """测试彗星模式衰减因子设置"""
        engine = StackingEngine(StackMode.COMET)

        engine.set_comet_fade_factor(0.95)
        self.assertEqual(engine.comet_fade_factor, 0.95)

        # 测试无效值
        with self.assertRaises(ValueError):
            engine.set_comet_fade_factor(1.5)

    def test_masked_average_keeps_first_frame_in_count(self):
        """双轨 Average 模式应正确包含第一帧"""
        sky_mask = np.ones((1, 1), dtype=np.float32)
        engine = StackingEngine(StackMode.AVERAGE, sky_mask=sky_mask)

        frame1 = np.array([[[100, 100, 100]]], dtype=np.uint16)
        frame2 = np.array([[[300, 300, 300]]], dtype=np.uint16)

        engine.add_image(frame1)
        engine.add_image(frame2)

        result = engine.get_result()
        np.testing.assert_array_equal(result, np.array([[[200, 200, 200]]], dtype=np.uint16))

    def test_satellite_mask_applies_in_mask_mode(self):
        """蒙版双轨模式下，划痕遮罩应阻止天空和地景都被更新"""
        sky_mask = np.array([[1.0, 0.0]], dtype=np.float32)
        engine = StackingEngine(StackMode.LIGHTEN, sky_mask=sky_mask)

        frame1 = np.array([[[100, 100, 100], [200, 200, 200]]], dtype=np.uint16)
        frame2 = np.array([[[500, 500, 500], [600, 600, 600]]], dtype=np.uint16)
        satellite_mask = np.array([[True, True]], dtype=bool)

        engine.add_image(frame1)
        engine.add_image(frame2, satellite_mask=satellite_mask)

        result = engine.get_result()
        np.testing.assert_array_equal(result, frame1)

    def test_get_result_can_be_cancelled_before_gap_filling(self):
        """gap filling 前若已取消，应抛出取消异常而不是继续处理"""
        engine = StackingEngine(StackMode.LIGHTEN, enable_gap_filling=True)
        engine.add_image(self.test_images[0])

        stop_event = Event()
        stop_event.set()

        with self.assertRaises(ProcessingCancelledError):
            engine.get_result(apply_gap_filling=True, stop_event=stop_event)


if __name__ == "__main__":
    unittest.main()
