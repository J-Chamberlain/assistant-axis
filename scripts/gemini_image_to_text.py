#!/usr/bin/env python3
"""Describe an image with Gemini for non-multimodal agents."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import platform
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_MODEL = "gemini-2.5-flash"
INLINE_LIMIT_BYTES = 20 * 1024 * 1024

DEFAULT_PROMPT = """When I send you an image, describe it in detail suitable for a non-multimodal AI that cannot see images. Your description should capture:

1. What type of content this is (e.g. code editor, terminal output, website, chart, diagram, error message, settings panel, etc.)
2. All text visible in the image, reproduced exactly and in full, including any code, file paths, error messages, terminal output, UI labels, button text, menu items, headings, data values, numbers, or table contents.
3. Layout and structure - where things are positioned relative to each other, what is highlighted or selected, what is expanded or collapsed.
4. Any visual indicators of state - error highlighting, warnings, success indicators, loading states, cursor position.
5. Anything unusual, unexpected, or relevant to a debugging or analysis task.

Format your response as structured plain text with clear section labels. Prioritize completeness and precision over brevity. Do not add any preamble - start your response immediately with the description."""


def load_dotenv() -> None:
    """Load simple KEY=VALUE entries from the nearest .env without adding a dependency."""
    for directory in [Path.cwd(), *Path.cwd().parents]:
        env_path = directory / ".env"
        if not env_path.exists():
            continue
        for raw_line in env_path.read_text().splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)
        return


def api_key() -> str:
    load_dotenv()
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise SystemExit(
            "Missing GEMINI_API_KEY. Add it to your shell environment or to assistant-axis/.env."
        )
    return key


def clipboard_image() -> tuple[bytes, str]:
    if platform.system() != "Darwin":
        raise SystemExit("--clipboard currently supports macOS only.")

    with tempfile.TemporaryDirectory() as tmpdir:
        tiff_path = Path(tmpdir) / "clipboard.tiff"
        png_path = Path(tmpdir) / "clipboard.png"

        tiff_script = f"""
        set outFile to POSIX file "{tiff_path}"
        set imageData to the clipboard as TIFF picture
        set fileRef to open for access outFile with write permission
        set eof fileRef to 0
        write imageData to fileRef
        close access fileRef
        """
        tiff_result = subprocess.run(
            ["osascript", "-e", tiff_script],
            text=True,
            capture_output=True,
            check=False,
        )
        if tiff_result.returncode != 0 or not tiff_path.exists() or not tiff_path.stat().st_size:
            raise SystemExit("No image data found on the macOS clipboard.")

        convert_result = subprocess.run(
            ["sips", "-s", "format", "png", str(tiff_path), "--out", str(png_path)],
            text=True,
            capture_output=True,
            check=False,
        )
        if convert_result.returncode != 0:
            raise SystemExit(f"Could not convert clipboard TIFF to PNG: {convert_result.stderr}")
        return png_path.read_bytes(), "image/png"


def fetch_url(url: str) -> tuple[bytes, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "gemini-image-to-text/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            content_type = response.headers.get_content_type()
            data = response.read()
    except urllib.error.URLError as exc:
        raise SystemExit(f"Could not fetch image URL: {exc}") from exc

    if not content_type.startswith("image/"):
        content_type = "image/jpeg"
    return data, content_type


def read_image(source: str | None, use_clipboard: bool) -> tuple[bytes, str]:
    if use_clipboard:
        return clipboard_image()
    if not source:
        raise SystemExit("Provide an image path/URL, or pass --clipboard.")
    if source.startswith(("http://", "https://")):
        return fetch_url(source)

    path = Path(source).expanduser()
    if not path.exists():
        raise SystemExit(f"Image not found: {path}")
    mime_type = mimetypes.guess_type(path.name)[0] or "image/png"
    if not mime_type.startswith("image/"):
        raise SystemExit(f"Not an image MIME type for {path}: {mime_type}")
    return path.read_bytes(), mime_type


def generate_description(
    image_bytes: bytes,
    mime_type: str,
    prompt: str,
    model: str,
    key: str,
) -> str:
    if len(image_bytes) > INLINE_LIMIT_BYTES:
        raise SystemExit(
            "Image is larger than the 20MB inline request limit. Use a smaller image or extend this script to use the Gemini Files API."
        )

    body = {
        "contents": [
            {
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": base64.b64encode(image_bytes).decode("ascii"),
                        }
                    },
                    {"text": prompt},
                ]
            }
        ]
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            payload = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Gemini API error ({exc.code}): {error_body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Gemini API request failed: {exc}") from exc

    try:
        parts = payload["candidates"][0]["content"]["parts"]
    except (KeyError, IndexError, TypeError) as exc:
        raise SystemExit(f"Unexpected Gemini API response: {json.dumps(payload, indent=2)}") from exc

    text = "\n".join(part.get("text", "") for part in parts).strip()
    if not text:
        raise SystemExit(f"Gemini returned no text: {json.dumps(payload, indent=2)}")
    return text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send an image to Gemini and print a precise text description."
    )
    parser.add_argument("image", nargs="?", help="Image path or HTTP(S) image URL.")
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="Read the current macOS clipboard image instead of an image path.",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("GEMINI_MODEL", DEFAULT_MODEL),
        help=f"Gemini model to use. Defaults to GEMINI_MODEL or {DEFAULT_MODEL}.",
    )
    parser.add_argument(
        "--prompt-file",
        type=Path,
        help="Optional file containing a custom image-description prompt.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    prompt = args.prompt_file.read_text() if args.prompt_file else DEFAULT_PROMPT
    image_bytes, mime_type = read_image(args.image, args.clipboard)
    print(
        generate_description(
            image_bytes=image_bytes,
            mime_type=mime_type,
            prompt=prompt,
            model=args.model,
            key=api_key(),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
