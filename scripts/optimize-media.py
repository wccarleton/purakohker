"""Prepare project images for R2, preserving full-resolution originals locally."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import tempfile
from pathlib import Path

from PIL import Image, ImageOps

MAX_EDGE = 2000
MAX_BYTES = 1_000_000
JPEG_QUALITY = 88
WEBP_QUALITY = 85
PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
BRANDING = {
    "kk_site_area.png", "kk_site_area.webp", "kk_site_area_900.webp",
    "prasat_prang_icon.png", "prasat_prang_icon.webp",
    "logo_napv.png", "logo_mpggea.jpg",
}


def archive_path(source: Path, image_root: Path, archive_root: Path) -> Path:
    digest = hashlib.sha256(source.read_bytes()).hexdigest()[:12]
    relative = source.relative_to(image_root)
    return archive_root / relative.parent / f"{relative.stem}.{digest}{relative.suffix}"


def prepare(source: Path, image_root: Path, archive_root: Path) -> tuple[str, Path | None]:
    with Image.open(source) as opened:
        width, height = opened.size
        if max(width, height) <= MAX_EDGE and source.stat().st_size <= MAX_BYTES:
            return "already web-sized", None
        image = ImageOps.exif_transpose(opened)
        image.thumbnail((MAX_EDGE, MAX_EDGE), Image.Resampling.LANCZOS)
        extension = source.suffix.lower()
        target = source.with_suffix(".webp") if extension == ".png" else source
        if target != source and target.exists():
            raise FileExistsError(f"Optimized target already exists: {target}")
        fd, temporary_name = tempfile.mkstemp(dir=source.parent, suffix=target.suffix)
        os.close(fd)
        temporary = Path(temporary_name)
        try:
            if extension == ".png" or extension == ".webp":
                if image.mode not in ("RGB", "RGBA"):
                    image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
                image.save(temporary, "WEBP", quality=WEBP_QUALITY, method=6)
            else:
                image = image.convert("RGB")
                image.save(temporary, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
            with Image.open(temporary) as check:
                check.verify()
            if target == source and temporary.stat().st_size >= source.stat().st_size and max(width, height) <= MAX_EDGE:
                return "original already smaller", None
            archived = archive_path(source, image_root, archive_root)
            archived.parent.mkdir(parents=True, exist_ok=True)
            if not archived.exists():
                shutil.copy2(source, archived)
            if hashlib.sha256(archived.read_bytes()).digest() != hashlib.sha256(source.read_bytes()).digest():
                raise RuntimeError(f"Original archive differs from source: {archived}")
            os.replace(temporary, target)
            if target != source:
                source.unlink()
            return f"optimized {source.stat().st_size if target == source else target.stat().st_size:,} bytes; original at {archived}", target
        finally:
            temporary.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    args = parser.parse_args()
    image_root = args.images.resolve()
    archive_root = args.archive.resolve()
    if archive_root == image_root or image_root in archive_root.parents:
        parser.error("Original archive must be outside the upload folder")
    if not image_root.is_dir():
        parser.error(f"Image folder does not exist: {image_root}")
    converted: list[tuple[Path, Path]] = []
    for source in sorted(image_root.rglob("*")):
        if not source.is_file() or source.suffix.lower() not in PHOTO_EXTENSIONS:
            continue
        if source.parent == image_root and source.name in BRANDING:
            continue
        old_size = source.stat().st_size
        result, target = prepare(source, image_root, archive_root)
        print(f"{source.relative_to(image_root)}: {result}")
        if target is not None:
            print(f"  {old_size:,} -> {target.stat().st_size:,} bytes")
            if target != source:
                converted.append((source.relative_to(image_root), target.relative_to(image_root)))
    if converted:
        print("Update any site links that use these converted filenames before publishing:")
        for old, new in converted:
            print(f"  {old} -> {new}")


if __name__ == "__main__":
    main()
