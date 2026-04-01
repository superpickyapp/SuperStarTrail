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

    def test_is_supported_file_includes_image_formats(self):
        """TIFF/JPG/PNG 应被识别为支持的格式"""
        self.assertTrue(RawProcessor.is_supported_file(Path("test.tif")))
        self.assertTrue(RawProcessor.is_supported_file(Path("test.jpg")))
        self.assertTrue(RawProcessor.is_supported_file(Path("test.png")))
        self.assertFalse(RawProcessor.is_supported_file(Path("test.bmp")))

    def test_process_jpg_returns_16bit_array(self):
        """处理 JPG 应返回 16-bit numpy 数组"""
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
            result = processor.process(image_path)

            self.assertEqual(result.dtype, np.uint16)
            self.assertEqual(result.ndim, 3)
            self.assertEqual(result.shape[2], 3)

    def test_process_jpg_ignores_extra_kwargs(self):
        """process() 应忽略多余的关键字参数（向后兼容）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / "test.jpg"
            image = np.zeros((4, 4, 3), dtype=np.uint8)
            Image.fromarray(image).save(image_path)

            processor = RawProcessor()
            # 传入旧版 white_balance / color_temperature 参数不应报错
            result = processor.process(
                image_path,
                white_balance="camera",
                color_temperature=3200,
            )
            self.assertIsNotNone(result)

    def test_process_file_not_found_raises(self):
        """文件不存在时应抛出 FileNotFoundError"""
        processor = RawProcessor()
        with self.assertRaises(FileNotFoundError):
            processor.process(Path("/nonexistent/file.jpg"))


if __name__ == "__main__":
    unittest.main()
