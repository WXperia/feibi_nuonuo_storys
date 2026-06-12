---
name: apinebula-image
description: Call APINebula's OpenAI-compatible GPT Image 2 image APIs for generation, reference-image edits, and mask/inpainting edits. Use when Codex needs to create images from text, edit one or more input images, perform masked local repainting, or provide runnable APINebula Images API examples. VIP/PRO models are documented but not used automatically while the VIP service is unavailable.
---

# APINebula Image

Use APINebula's GPT Image 2 groups through the OpenAI-compatible Images API.

- Default group: `gpt-image-2`
- VIP image2-vip group: `gpt-image-2-vip` or `gpt-image-2-pro`

The bundled script defaults to `--model auto`, which currently always uses `gpt-image-2` for every requested size. VIP/PRO models are not selected automatically while the VIP service is unavailable. Pass `--model gpt-image-2-vip` or `--model gpt-image-2-pro` only when explicitly testing VIP/PRO.

Default and VIP/PRO calls can use different API keys. Auto mode uses the default key because it resolves to `gpt-image-2`; when `--model gpt-image-2-vip` or `--model gpt-image-2-pro` is passed explicitly, the script reads the VIP key.

## Quick Start

Prefer the bundled script for real calls:

```bash
python "$SKILL_PATH/scripts/apinebula_image.py" generate \
  --prompt "A clean product photo of a silver wireless earbud case on a light gray background" \
  --output output.png
```

For 2K square output through the default group:

```bash
python "$SKILL_PATH/scripts/apinebula_image.py" generate \
  --prompt "An original anime character sheet, centered full-body teenager with headphones and a small crossbody bag, layered clothing, clean light background, refined line art, soft cel shading, no text, no watermark" \
  --width 2048 \
  --height 2048 \
  --quality high \
  --output output.jpg
```

For 4K widescreen or vertical output, use `--width 3840 --height 2160` or `--width 2160 --height 3840`. The script currently sends `model=gpt-image-2` in auto mode.

```bash
python "$SKILL_PATH/scripts/apinebula_image.py" edit \
  --prompt "Place the product from the first image onto the wooden desk scene in the second image, preserving shadows and perspective" \
  --image product.png \
  --image background.png \
  --size 1536x1024 \
  --quality high \
  --output output.png
```

```bash
python "$SKILL_PATH/scripts/apinebula_image.py" edit \
  --prompt "Place the original anime character from the first image into the cherry-blossom riverside scene in the second image, preserving outfit details and matching sunset light, perspective, and soft shadows, anime film still quality, no text, no watermark" \
  --image anime-character.png \
  --image anime-scenery.png \
  --width 2048 \
  --height 2048 \
  --quality high \
  --input-fidelity high \
  --output output.jpg
```

```bash
python "$SKILL_PATH/scripts/apinebula_image.py" edit \
  --prompt "Replace the masked region with a clean minimalist home corner while preserving natural daylight" \
  --image background.png \
  --mask mask.png \
  --quality high \
  --output output.png
```

If `$SKILL_PATH` is not set, use the absolute path to this skill directory:
`C:\Users\XieZiqian\.codex\skills\apinebula-image`.

## Setup

Before the first real API call, set up the API keys in the user's home directory:

```bash
python "$SKILL_PATH/scripts/setup_apinebula_image.py"
```

The setup script prompts for default-group and VIP/PRO keys without echoing them, then writes:
`~/.apinebula/apinebula-image.json`.

To pass keys non-interactively:

```bash
python "$SKILL_PATH/scripts/setup_apinebula_image.py" \
  --api-key "YOUR_DEFAULT_API_KEY" \
  --vip-api-key "YOUR_VIP_API_KEY"
```

To update only the VIP key and keep the existing default key:

```bash
python "$SKILL_PATH/scripts/setup_apinebula_image.py" --vip-api-key "YOUR_VIP_API_KEY"
```

To verify setup without printing the key:

```bash
python "$SKILL_PATH/scripts/setup_apinebula_image.py" --check
```

On this machine, the absolute setup command is:

```powershell
python C:\Users\XieZiqian\.codex\skills\apinebula-image\scripts\setup_apinebula_image.py
```

## Credentials

Require an APINebula API key. Default-group calls read the key in this order:

1. `--api-key`
2. `APINEBULA_API_KEY`
3. `api_key` in `~/.apinebula/apinebula-image.json`

VIP/PRO calls read the key in this order:

1. `--vip-api-key`
2. `APINEBULA_VIP_API_KEY`
3. `vip_api_key` in `~/.apinebula/apinebula-image.json`

Never print the key. Prefer setup over passing `--api-key` because command-line arguments can be visible in shell history or process listings.

PowerShell:

```powershell
$env:APINEBULA_API_KEY = "YOUR_API_KEY"
$env:APINEBULA_VIP_API_KEY = "YOUR_VIP_API_KEY"
```

## Endpoints

- Text-to-image: `POST https://apinebula.com/v1/images/generations`
- Image edit and mask edit: `POST https://apinebula.com/v1/images/edits`
- Models: `gpt-image-2`, `gpt-image-2-vip`, `gpt-image-2-pro`

For parameter support and caveats, read `references/api.md`.

## Output Handling

Default to `response_format=b64_json` and save the decoded image to a local file. The API also supports `response_format=url`; when using URLs, download the returned URL unless the user specifically asks for only the URL.

Treat `n` as effectively fixed to `1`; do not promise multiple images from one request.

For VIP/PRO, prefer `response_format=b64_json` when saving locally. `response_format=url` is also supported. `output_format=jpeg` and `output_compression=0..100` are supported for JPEG output.
