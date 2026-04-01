"""
FileNamingService 测试
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.file_naming import FileNamingService
from core.stacking_engine import StackMode


class TestFileNamingService(unittest.TestCase):
    """FileNamingService 测试类"""

    def setUp(self):
        self.test_files = [
            Path("/test/IMG_0001.CR2"),
            Path("/test/IMG_0002.CR2"),
            Path("/test/IMG_0003.CR2"),
            Path("/test/IMG_0100.CR2"),
        ]

    def test_extract_file_range_continuous(self):
        files = [
            Path("/test/IMG_0001.CR2"),
            Path("/test/IMG_0002.CR2"),
            Path("/test/IMG_0003.CR2"),
        ]
        self.assertEqual(FileNamingService.extract_file_range(files), "IMG_0001-0003")

    def test_extract_file_range_gap(self):
        self.assertEqual(FileNamingService.extract_file_range(self.test_files), "IMG_0001-0100")

    def test_extract_file_range_single_file(self):
        files = [Path("/test/IMG_0001.CR2")]
        self.assertEqual(FileNamingService.extract_file_range(files), "IMG_0001-0001")

    def test_extract_file_range_two_files(self):
        files = [Path("/test/IMG_0001.CR2"), Path("/test/IMG_0002.CR2")]
        self.assertEqual(FileNamingService.extract_file_range(files), "IMG_0001-0002")

    def test_extract_file_range_different_prefixes(self):
        files = [Path("/test/IMG_0001.CR2"), Path("/test/DSC_0001.CR2")]
        result = FileNamingService.extract_file_range(files)
        self.assertIn("0001", result)

    def test_generate_output_filename_lighten(self):
        filename = FileNamingService.generate_output_filename(
            file_paths=self.test_files,
            stack_mode=StackMode.LIGHTEN,
            file_extension="tif"
        )
        self.assertIn("Lighten", filename)
        self.assertIn(".tif", filename)
        self.assertIn("IMG_0001-0100", filename)

    def test_generate_output_filename_comet(self):
        filename = FileNamingService.generate_output_filename(
            file_paths=self.test_files,
            stack_mode=StackMode.COMET,
            comet_fade_factor=0.97,
            file_extension="jpg"
        )
        self.assertIn("Comet", filename)
        self.assertIn("MidTail", filename)
        self.assertIn(".jpg", filename)

    def test_generate_output_filename_with_gap_filling(self):
        filename = FileNamingService.generate_output_filename(
            file_paths=self.test_files,
            stack_mode=StackMode.LIGHTEN,
            enable_gap_filling=True,
            file_extension="tif"
        )
        self.assertIn("GapFilled", filename)

    def test_generate_timelapse_filename(self):
        filename = FileNamingService.generate_timelapse_filename(
            file_paths=self.test_files,
            stack_mode=StackMode.LIGHTEN,
            file_extension="mp4"
        )
        self.assertIn("Timelapse", filename)
        self.assertIn("Lighten", filename)
        self.assertIn(".mp4", filename)

    def test_generate_timelapse_filename_comet(self):
        filename = FileNamingService.generate_timelapse_filename(
            file_paths=self.test_files,
            stack_mode=StackMode.COMET,
            comet_fade_factor=0.98,
            file_extension="mp4"
        )
        self.assertIn("Comet", filename)
        self.assertIn("LongTail", filename)
        self.assertIn("Timelapse", filename)

    def test_generate_output_filename_is_string(self):
        filename = FileNamingService.generate_output_filename(
            file_paths=self.test_files,
            stack_mode=StackMode.LIGHTEN,
            file_extension="tif"
        )
        self.assertIsInstance(filename, str)
        self.assertGreater(len(filename), 0)

    def test_empty_file_list(self):
        self.assertEqual(FileNamingService.extract_file_range([]), "untitled")

    def test_special_characters_in_filename(self):
        files = [
            Path("/test/IMG 0001 (copy).CR2"),
            Path("/test/IMG 0002 (copy).CR2"),
        ]
        result = FileNamingService.extract_file_range(files)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)


if __name__ == "__main__":
    unittest.main()
