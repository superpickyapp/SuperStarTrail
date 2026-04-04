"""
TimelapseGenerator 测试
"""

import sys
import tempfile
import unittest
from pathlib import Path
from threading import Event
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.timelapse_generator import TimelapseGenerator


class _FakeVideoWriter:
    def __init__(self, *_args, **_kwargs):
        self.frames_written = 0

    def isOpened(self):
        return True

    def write(self, _frame):
        self.frames_written += 1

    def release(self):
        return None


class TestTimelapseGenerator(unittest.TestCase):
    """TimelapseGenerator 行为测试"""

    def test_generate_video_can_be_cancelled_and_cleans_frames(self):
        """取消编码时应返回 False 并清理临时帧"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            output_path = tmpdir_path / "out.mp4"
            temp_dir = tmpdir_path / "frames"
            temp_dir.mkdir()

            frame_paths = []
            for index in range(2):
                frame_path = temp_dir / f"frame_{index:05d}.jpg"
                frame_path.touch()
                frame_paths.append(frame_path)

            generator = TimelapseGenerator(
                output_path=output_path,
                fps=25,
                resolution=(2, 2),
                temp_dir=temp_dir,
            )
            generator.frame_paths = frame_paths
            generator.frame_count = len(frame_paths)

            stop_event = Event()
            stop_event.set()

            with patch("core.timelapse_generator.cv2.VideoWriter", _FakeVideoWriter), patch(
                "core.timelapse_generator.cv2.VideoWriter_fourcc", return_value=0
            ), patch(
                "core.timelapse_generator.cv2.imread",
                return_value=np.zeros((2, 2, 3), dtype=np.uint8),
            ):
                success = generator.generate_video(cleanup=True, stop_event=stop_event)

            self.assertFalse(success)
            self.assertFalse(output_path.exists())
            self.assertFalse(temp_dir.exists())
