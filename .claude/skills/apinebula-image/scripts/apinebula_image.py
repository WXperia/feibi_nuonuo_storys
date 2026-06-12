#!/usr/bin/env python3
"""Call APINebula GPT Image 2 image endpoints and save the result."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
from pathlib import Path
import sys
import time
from typing import Iterable
from urllib import error, request


BASE_URL = "https://apinebula.com/v1"
AUTO_MODEL = "auto"
DEFAULT_MODEL = "gpt-image-2"
VIP_MODELS = {"gpt-image-2-vip", "gpt-image-2-pro"}
SUPPORTED_MODELS = [AUTO_MODEL, DEFAULT_MODEL, *sorted(VIP_MODELS)]
VIP_SIZES = {"2048x2048", "3840x2160", "2160x3840"}
CONFIG_PATH = Path.home() / ".apinebula" / "apinebula-image.json"
DEFAULT_API_KEY_ENV = "APINEBULA_API_KEY"
VIP_API_KEY_ENV = "APINEBULA_VIP_API_KEY"


def _config_api_key(field: str) -> str | None:
    if not CONFIG_PATH.exists():
        return None
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Could not read APINebula config at {CONFIG_PATH}: {exc}") from exc
    key = data.get(field)
    return key if isinstance(key, str) and key.strip() else None


def _api_key(args: argparse.Namespace, model: str) -> str:
    if model in VIP_MODELS:
        key = args.vip_api_key or os.environ.get(VIP_API_KEY_ENV) or _config_api_key("vip_api_key")
        if not key:
            raise SystemExit(
                "Missing VIP API key for gpt-image-2-vip/gpt-image-2-pro. "
                "Run setup_apinebula_image.py --vip-api-key, set APINEBULA_VIP_API_KEY, "
                "or pass --vip-api-key."
            )
        return key

    key = args.api_key or os.environ.get(DEFAULT_API_KEY_ENV) or _config_api_key("api_key")
    if not key:
        raise SystemExit(
            "Missing API key. Run setup_apinebula_image.py, set APINEBULA_API_KEY, or pass --api-key."
        )
    return key


def _headers(args: argparse.Namespace, model: str, content_type: str | None = None) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {_api_key(args, model)}"}
    if content_type:
        headers["Content-Type"] = content_type
    return headers


def _request_json(url: str, headers: dict[str, str], body: bytes, timeout: int) -> dict:
    req = request.Request(url, data=body, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {exc.code}: {detail}") from exc
    except error.URLError as exc:
        raise SystemExit(f"Request failed: {exc}") from exc

    try:
        return json.loads(data.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Response was not JSON: {data[:500]!r}") from exc


def _add_common_fields(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--api-key", help="APINebula default-group API key. Prefer setup or APINEBULA_API_KEY.")
    parser.add_argument(
        "--vip-api-key",
        help="APINebula VIP/PRO API key. Prefer setup --vip-api-key or APINEBULA_VIP_API_KEY.",
    )
    parser.add_argument(
        "--model",
        choices=SUPPORTED_MODELS,
        default=AUTO_MODEL,
        help=(
            "Image model. Defaults to auto, which currently always uses gpt-image-2. "
            "Pass gpt-image-2-vip or gpt-image-2-pro only to force VIP/PRO."
        ),
    )
    parser.add_argument("--prompt", required=True, help="Image prompt or edit instruction.")
    parser.add_argument("--output", "-o", help="Output image path. Defaults to a timestamped PNG.")
    parser.add_argument(
        "--size",
        help=(
            "Requested output size, for example 1024x1024 or 1536x1024. "
            "VIP/PRO support 2048x2048, 3840x2160, and 2160x3840."
        ),
    )
    parser.add_argument("--width", type=int, help="Requested output width. Use with --height.")
    parser.add_argument("--height", type=int, help="Requested output height. Use with --width.")
    parser.add_argument("--quality", choices=["low", "medium", "high", "auto"], help="Image quality.")
    parser.add_argument("--response-format", choices=["b64_json", "url"], default="b64_json")
    parser.add_argument("--background", choices=["opaque", "transparent"])
    parser.add_argument("--moderation", choices=["auto", "low"])
    parser.add_argument("--user", help="Optional end-user or business source marker.")
    parser.add_argument("--n", type=int, choices=[1], help="Only 1 is supported.")
    parser.add_argument("--output-format", choices=["png", "jpeg"])
    parser.add_argument("--output-compression", type=int, choices=range(0, 101), metavar="0-100")
    parser.add_argument("--timeout", type=int, default=300, help="Request timeout in seconds.")


def _clean_options(args: argparse.Namespace, names: Iterable[str]) -> dict[str, object]:
    model, size = _validate_and_resolve_options(args)
    data: dict[str, object] = {"model": model, "prompt": args.prompt}
    for name in names:
        value = size if name == "size" else getattr(args, name)
        if value is not None:
            data[name] = value
    return data


def _parse_size(size: str | None) -> tuple[int, int] | None:
    if not size:
        return None
    parts = size.lower().split("x")
    if len(parts) != 2:
        raise SystemExit(f"Invalid --size {size!r}; expected WIDTHxHEIGHT, for example 2048x2048.")
    try:
        width, height = int(parts[0]), int(parts[1])
    except ValueError as exc:
        raise SystemExit(f"Invalid --size {size!r}; width and height must be integers.") from exc
    if width <= 0 or height <= 0:
        raise SystemExit(f"Invalid --size {size!r}; width and height must be positive.")
    return width, height


def _resolve_size(args: argparse.Namespace) -> tuple[str | None, tuple[int, int] | None]:
    size_tuple = _parse_size(args.size)

    has_width = args.width is not None
    has_height = args.height is not None
    if has_width or has_height:
        if not has_width or not has_height:
            raise SystemExit("Pass both --width and --height, or use --size WIDTHxHEIGHT.")
        if args.width <= 0 or args.height <= 0:
            raise SystemExit("--width and --height must be positive integers.")
        wh_tuple = (args.width, args.height)
        if size_tuple and size_tuple != wh_tuple:
            raise SystemExit(
                f"--size {args.size} does not match --width {args.width} --height {args.height}."
            )
        size_tuple = wh_tuple

    if not size_tuple:
        return None, None
    width, height = size_tuple
    return f"{width}x{height}", size_tuple


def _resolve_model(args: argparse.Namespace, size: str | None) -> str:
    if args.model != AUTO_MODEL:
        return args.model
    return DEFAULT_MODEL


def _validate_and_resolve_options(args: argparse.Namespace) -> tuple[str, str | None]:
    size, _ = _resolve_size(args)
    model = _resolve_model(args, size)

    if model in VIP_MODELS:
        if size and size not in VIP_SIZES:
            valid = ", ".join(sorted(VIP_SIZES))
            raise SystemExit(
                f"{model} supports these documented 2K/4K sizes: {valid}. "
                "4096x4096 is not supported."
            )
        if args.background == "transparent":
            raise SystemExit(f"{model} does not support transparent background; omit it or use opaque.")
        if args.output_format and args.output_format != "jpeg":
            raise SystemExit(f"{model} only documents output_format=jpeg; omit it or use jpeg.")

    return model, size


def _default_output_path() -> Path:
    return Path.cwd() / f"apinebula-image-{int(time.time())}.png"


def _strip_data_url(value: str) -> str:
    if value.startswith("data:") and "," in value:
        return value.split(",", 1)[1]
    return value


def _extension_for_bytes(data: bytes) -> str:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return ".webp"
    return ".img"


def _write_bytes(data: bytes, output: str | None) -> Path:
    path = Path(output) if output else _default_output_path()
    if not output and path.suffix == ".png":
        suffix = _extension_for_bytes(data)
        if suffix != ".img":
            path = path.with_suffix(suffix)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def _save_response_image(response: dict, output: str | None, timeout: int) -> dict[str, str]:
    data = response.get("data")
    if not isinstance(data, list) or not data:
        raise SystemExit(f"No image data in response: {json.dumps(response, ensure_ascii=False)[:1000]}")

    first = data[0]
    if "b64_json" in first:
        raw = base64.b64decode(_strip_data_url(first["b64_json"]))
        path = _write_bytes(raw, output)
        return {"output": str(path), "bytes": str(len(raw))}

    if "url" in first:
        url = first["url"]
        try:
            with request.urlopen(url, timeout=timeout) as resp:
                raw = resp.read()
        except error.URLError as exc:
            raise SystemExit(f"Could not download image URL {url!r}: {exc}") from exc
        path = _write_bytes(raw, output)
        return {"output": str(path), "url": url, "bytes": str(len(raw))}

    raise SystemExit(f"Unsupported image response: {json.dumps(first, ensure_ascii=False)[:1000]}")


def _multipart_body(fields: dict[str, object], files: list[tuple[str, Path]]) -> tuple[bytes, str]:
    boundary = f"apinebula-{int(time.time() * 1000)}"
    chunks: list[bytes] = []

    for key, value in fields.items():
        chunks.extend(
            [
                f"--{boundary}\r\n".encode(),
                f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode(),
                str(value).encode("utf-8"),
                b"\r\n",
            ]
        )

    for key, path in files:
        if not path.exists():
            raise SystemExit(f"File not found: {path}")
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        chunks.extend(
            [
                f"--{boundary}\r\n".encode(),
                f'Content-Disposition: form-data; name="{key}"; filename="{path.name}"\r\n'.encode(),
                f"Content-Type: {mime}\r\n\r\n".encode(),
                path.read_bytes(),
                b"\r\n",
            ]
        )

    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def generate(args: argparse.Namespace) -> None:
    fields = _clean_options(
        args,
        [
            "n",
            "size",
            "quality",
            "response_format",
            "output_format",
            "output_compression",
            "background",
            "moderation",
            "user",
        ],
    )
    model = str(fields["model"])
    body = json.dumps(fields, ensure_ascii=False).encode("utf-8")
    response = _request_json(
        f"{BASE_URL}/images/generations",
        _headers(args, model, "application/json"),
        body,
        args.timeout,
    )
    print(json.dumps(_save_response_image(response, args.output, args.timeout), ensure_ascii=False))


def edit(args: argparse.Namespace) -> None:
    fields = _clean_options(
        args,
        [
            "n",
            "size",
            "quality",
            "response_format",
            "input_fidelity",
            "output_format",
            "output_compression",
            "background",
            "moderation",
            "user",
        ],
    )
    model = str(fields["model"])
    files = [("image", Path(image)) for image in args.image]
    if args.mask:
        files.append(("mask", Path(args.mask)))
    body, content_type = _multipart_body(fields, files)
    response = _request_json(
        f"{BASE_URL}/images/edits",
        _headers(args, model, content_type),
        body,
        args.timeout,
    )
    print(json.dumps(_save_response_image(response, args.output, args.timeout), ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen = subparsers.add_parser("generate", help="Create an image from text.")
    _add_common_fields(gen)
    gen.set_defaults(func=generate)

    ed = subparsers.add_parser("edit", help="Edit images or perform masked repainting.")
    _add_common_fields(ed)
    ed.add_argument("--image", action="append", required=True, help="Input image. Repeat for references.")
    ed.add_argument("--mask", help="Mask image for local repainting.")
    ed.add_argument("--input-fidelity", choices=["high"], help="Follow input images more closely.")
    ed.set_defaults(func=edit)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
