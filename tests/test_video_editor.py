"""Tests for video_editor.py using small synthetically-generated clips.

These tests avoid bundling binary video fixtures by generating short clips
with MoviePy's ColorClip/AudioClip at test time.
"""

import os
import sys
import tempfile
import unittest

import numpy as np
from moviepy import AudioClip, ColorClip, VideoFileClip

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from video_editor import EditOptions, get_duration, process_video


def _make_sample_clip(path: str, duration: float = 2.0, with_audio: bool = True) -> None:
    clip = ColorClip(size=(64, 48), color=(255, 0, 0), duration=duration).with_fps(10)
    if with_audio:
        audio = AudioClip(lambda t: np.sin(440 * 2 * np.pi * t) * 0.5, duration=duration, fps=44100)
        clip = clip.with_audio(audio)
    clip.write_videofile(path, codec="libx264", audio_codec="aac" if with_audio else None, logger=None)


class VideoEditorTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.input_path = os.path.join(self.tmpdir, "input.mp4")
        _make_sample_clip(self.input_path, duration=2.0, with_audio=True)

    def _output_path(self, suffix=".mp4"):
        return os.path.join(self.tmpdir, f"output{suffix}")

    def test_get_duration(self):
        self.assertAlmostEqual(get_duration(self.input_path), 2.0, delta=0.2)

    def test_trim_shortens_duration(self):
        out = self._output_path()
        process_video(self.input_path, out, EditOptions(start=0.5, end=1.5))
        self.assertAlmostEqual(get_duration(out), 1.0, delta=0.2)

    def test_resize_changes_dimensions(self):
        out = self._output_path()
        process_video(self.input_path, out, EditOptions(scale=0.5))
        with VideoFileClip(out) as clip:
            self.assertEqual(list(clip.size), [32, 24])

    def test_speed_change_shortens_duration(self):
        out = self._output_path()
        process_video(self.input_path, out, EditOptions(speed=2.0))
        self.assertAlmostEqual(get_duration(out), 1.0, delta=0.2)

    def test_extract_audio_only(self):
        out = self._output_path(suffix=".mp3")
        process_video(self.input_path, out, EditOptions(extract_audio_only=True))
        self.assertTrue(os.path.exists(out))
        self.assertGreater(os.path.getsize(out), 0)

    def test_extract_audio_without_audio_track_raises(self):
        silent_path = os.path.join(self.tmpdir, "silent.mp4")
        _make_sample_clip(silent_path, duration=1.0, with_audio=False)
        out = self._output_path(suffix=".mp3")
        with self.assertRaises(ValueError):
            process_video(silent_path, out, EditOptions(extract_audio_only=True))


if __name__ == "__main__":
    unittest.main()
