"""Checks that R2 preparation preserves originals and stable JPEG URLs."""

import importlib.util
import tempfile
import unittest
from pathlib import Path

from PIL import Image


spec = importlib.util.spec_from_file_location("optimize_media", Path(__file__).with_name("optimize-media.py"))
optimizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(optimizer)


class OptimizeMediaTest(unittest.TestCase):
    def test_large_jpeg_archives_original_and_keeps_url(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent.parent) as temporary:
            root = Path(temporary)
            images = root / "images"
            archive = root / "originals"
            source = images / "fieldwork" / "photo.jpg"
            source.parent.mkdir(parents=True)
            Image.new("RGB", (3000, 2100), (120, 80, 40)).save(source, quality=95)
            original = source.read_bytes()
            _, target = optimizer.prepare(source, images, archive)
            self.assertEqual(target, source)
            with Image.open(source) as result:
                self.assertLessEqual(max(result.size), optimizer.MAX_EDGE)
            archived = list(archive.rglob("*.jpg"))
            self.assertEqual(len(archived), 1)
            self.assertEqual(archived[0].read_bytes(), original)
            _, repeat_target = optimizer.prepare(source, images, archive)
            self.assertIsNone(repeat_target)

    def test_large_png_converts_to_webp_and_archives_png(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent.parent) as temporary:
            root = Path(temporary)
            images = root / "images"
            archive = root / "originals"
            source = images / "project" / "photo.png"
            source.parent.mkdir(parents=True)
            Image.new("RGB", (2400, 1800), (20, 70, 130)).save(source)
            original = source.read_bytes()
            _, target = optimizer.prepare(source, images, archive)
            self.assertEqual(target, source.with_suffix(".webp"))
            self.assertFalse(source.exists())
            with Image.open(target) as result:
                self.assertEqual(result.format, "WEBP")
            self.assertEqual(next(archive.rglob("*.png")).read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
