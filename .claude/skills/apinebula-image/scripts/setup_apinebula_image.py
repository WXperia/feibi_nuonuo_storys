#!/usr/bin/env python3
"""Store APINebula API keys in the user's home directory for this skill."""

from __future__ import annotations

import argparse
import getpass
import json
from pathlib import Path
import stat
import sys


CONFIG_PATH = Path.home() / ".apinebula" / "apinebula-image.json"


def _read_existing_config(config_path: Path) -> dict[str, str]:
    if not config_path.exists():
        return {}
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Could not read existing config at {config_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"Config at {config_path} must be a JSON object.")
    return {key: value for key, value in data.items() if isinstance(value, str)}


def store_keys(
    api_key: str | None = None,
    vip_api_key: str | None = None,
    config_path: Path = CONFIG_PATH,
) -> Path:
    api_key = api_key.strip() if api_key else None
    vip_api_key = vip_api_key.strip() if vip_api_key else None
    if not api_key and not vip_api_key:
        raise SystemExit("At least one API key must be provided.")

    data = _read_existing_config(config_path)
    if api_key:
        data["api_key"] = api_key
    if vip_api_key:
        data["vip_api_key"] = vip_api_key

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        config_path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass
    return config_path


def check_config(config_path: Path = CONFIG_PATH) -> None:
    if not config_path.exists():
        raise SystemExit(f"No APINebula image config found at {config_path}")
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Could not read config at {config_path}: {exc}") from exc
    has_api_key = isinstance(data.get("api_key"), str) and bool(data["api_key"].strip())
    has_vip_api_key = isinstance(data.get("vip_api_key"), str) and bool(data["vip_api_key"].strip())
    if not has_api_key and not has_vip_api_key:
        raise SystemExit(f"Config exists but api_key is missing at {config_path}")
    print(
        json.dumps(
            {"config": str(config_path), "has_api_key": has_api_key, "has_vip_api_key": has_vip_api_key},
            ensure_ascii=False,
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-key", help="APINebula default-group API key.")
    parser.add_argument("--vip-api-key", help="APINebula VIP/PRO API key.")
    parser.add_argument("--check", action="store_true", help="Check whether setup exists without printing the key.")
    parser.add_argument("--show-path", action="store_true", help="Print the config file path.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.show_path:
        print(CONFIG_PATH)
        return 0
    if args.check:
        check_config()
        return 0

    api_key = args.api_key
    vip_api_key = args.vip_api_key
    if not api_key and not vip_api_key:
        api_key = getpass.getpass("APINebula default-group API key (leave empty to skip): ")
        vip_api_key = getpass.getpass("APINebula VIP/PRO API key (leave empty to skip): ")
    path = store_keys(api_key=api_key, vip_api_key=vip_api_key)
    print(json.dumps({"config": str(path), "saved": True}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
