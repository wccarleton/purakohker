"""Build the gallery from public R2 object keys.

Usage: python generate_photos_page.py
"""

import argparse
import os
from pathlib import Path
from urllib.parse import quote, urlparse


MANIFEST = Path("media/gallery-objects.txt")
OUTPUT = Path("photos.qmd")
DEFAULT_MEDIA_BASE_URL = "https://media.wccarleton.org"
HEADER = """---
title: Fieldwork Photos
lightbox: true
---

"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the photo gallery from R2 object keys.")
    parser.add_argument(
        "--media-base-url",
        default=os.environ.get("R2_MEDIA_BASE_URL", DEFAULT_MEDIA_BASE_URL),
        help="Public R2 base URL; may also be set with R2_MEDIA_BASE_URL.",
    )
    args = parser.parse_args()

    if not args.media_base_url or not args.media_base_url.startswith("https://"):
        parser.error("provide an HTTPS public R2 base URL with --media-base-url")
    if (urlparse(args.media_base_url).hostname or "").endswith(".r2.cloudflarestorage.com"):
        parser.error("the R2 S3 API endpoint is not a public image URL; use an R2 custom domain")

    keys = [
        line.strip()
        for line in MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not keys or len(keys) != len(set(keys)) or any(
        key.startswith("/") or ".." in Path(key).parts for key in keys
    ):
        parser.error("gallery manifest must contain unique relative object keys")

    base_url = args.media_base_url.rstrip("/")
    lines = [
        f'![]({base_url}/{quote(key, safe="/")}){{group="my-gallery" loading="lazy"}}'
        for key in keys
    ]
    OUTPUT.write_text(HEADER + "\n\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated {OUTPUT} with {len(keys)} R2 images.")


if __name__ == "__main__":
    main()
