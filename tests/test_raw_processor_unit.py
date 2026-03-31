"""
RawProcessor 单元测试
"""

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.raw_processor import RawProcessor


class TestRawProcessorUnit(unittest.TestCase):
    """RawProcessor 的纯单元测试"""

    def test_is_raw_file_only_matches_raw_extensions(self):
        """JPG 不应被识别为 RAW"""
        self.assertTrue(RawProcessor.is_raw_file(Path("test.nef")))
        self.assertFalse(RawProcessor.is_raw_file(Path("test.jpg")))

    def test_kelvin_to_user_wb_returns_four_channel_multipliers(self):
        """手动色温应转换为 rawpy 所需的 4 通道倍率"""
        multipliers = RawProcessor._kelvin_to_user_wb(3200)

        self.assertEqual(len(multipliers), 4)
        self.assertGreater(multipliers[0], 0)
        self.assertEqual(multipliers[1], 1.0)
        self.assertGreaterEqual(multipliers[2], 0)
        self.assertEqual(multipliers[3], 1.0)

    def test_non_raw_files_ignore_white_balance_settings(self):
        """JPG 路径不应用白平衡或手动色温"""
        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / "test.jpg"
            image = np.array(
                [
                    [[255, 128, 0], [0, 64, 255]],
                    [[30, 200, 90], [120, 10, 220]],
                ],
                dtype=np.uint8,
            )
            Image.fromarray(image).save(image_path, "JPEG", quality=100, subsampling=0)

            processor = RawProcessor()
            camera_result = processor.process(image_path, white_balance="camera")
            manual_result = processor.process(
                image_path,
                white_balance="manual",
                color_temperature=3200,
            )

            np.testing.assert_array_equal(camera_result, manual_result)


if __name__ == "__main__":
    unittest.main()
