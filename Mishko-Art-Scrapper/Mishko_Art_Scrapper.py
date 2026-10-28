#!/usr/bin/env python3
"""Mishko Art Scraper - downloads artwork images from https://mishko.co/

Images are saved into the `images/` folder next to this script.
"""
import argparse
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://mishko.co/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )
}
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "images"


def fetch_image_urls(page_url: str = BASE_URL) -> list[str]:
    """Return absolute URLs of all lazy-loaded images on the page."""
    response = requests.get(page_url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    urls = []
    for img in soup.find_all("img", class_="js-lazy"):
        src = (img.get("data-src") or "").strip()
        if not src:
            continue
        # urljoin handles protocol-relative ("//cdn...") and relative URLs
        urls.append(urljoin(page_url, src))
    return urls


def guess_extension(url: str) -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    return suffix if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif"} else ".jpg"


def download_images(urls: list[str], output_dir: Path) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    saved = 0
    for index, url in enumerate(urls, start=1):
        path = output_dir / f"{index}{guess_extension(url)}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            r.raise_for_status()
        except requests.RequestException as exc:
            print(f"[{index}/{len(urls)}] FAILED {url} ({exc})", file=sys.stderr)
            continue
        path.write_bytes(r.content)
        saved += 1
        print(f"[{index}/{len(urls)}] {url} -> {path.name}")
    return saved


def main() -> int:
    parser = argparse.ArgumentParser(description="Scrape Mishko art images.")
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT,
                        help="directory to save images (default: ./images)")
    args = parser.parse_args()

    urls = fetch_image_urls()
    print(f"Found {len(urls)} images")
    saved = download_images(urls, args.output)
    print(f"Saved {saved}/{len(urls)} images to {args.output}")
    return 0 if saved == len(urls) else 1


if __name__ == "__main__":
    sys.exit(main())

