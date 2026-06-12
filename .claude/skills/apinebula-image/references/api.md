# APINebula GPT Image 2 Image APIs

Source: https://docs.apinebula.com/docs/advanced/image/default
VIP source: user-provided APINebula image2-vip docs

## Model Groups

Default group:
- Model: `gpt-image-2`
- Use for ordinary image generation and edits.
- Larger sizes such as `2048x2048` are not reliable in the default group.

image2-vip group:
- Models: `gpt-image-2-vip`, `gpt-image-2-pro`
- Use for 2K or 4K image generation, reference-image edits, and mask edits.
- Supported sizes: `2048x2048`, `3840x2160`, `2160x3840`
- Unsupported size: `4096x4096`; longest side cannot exceed `3840`.
- `n` is only `1`.

Bundled script model selection:
- Default `--model auto` currently always chooses `gpt-image-2` for every requested size because the VIP service is unavailable.
- Pass `--model gpt-image-2-vip` or `--model gpt-image-2-pro` only to force VIP/PRO for documented VIP/PRO sizes.
- `--width` and `--height` are normalized to the API `size` field as `WIDTHxHEIGHT`.

Bundled script credential selection:
- `gpt-image-2` uses the default API key: `--api-key`, then `APINEBULA_API_KEY`, then `api_key` in `~/.apinebula/apinebula-image.json`.
- `gpt-image-2-vip` and `gpt-image-2-pro` use the VIP API key: `--vip-api-key`, then `APINEBULA_VIP_API_KEY`, then `vip_api_key` in `~/.apinebula/apinebula-image.json`.
- In `--model auto`, credential selection uses the default API key because auto resolves to `gpt-image-2`.

## Generation

Endpoint: `POST https://apinebula.com/v1/images/generations`

Body is JSON.

Required fields:
- `model`: `gpt-image-2`, `gpt-image-2-vip`, or `gpt-image-2-pro`
- `prompt`: image description

Common optional fields:
- `size`: default group supports sizes such as `1024x1024`. VIP/PRO support `2048x2048`, `3840x2160`, and `2160x3840`.
- `quality`: `low`, `medium`, `high`, `auto`
- `response_format`: `b64_json` or `url`
- `background`: `opaque` or `transparent`
- `moderation`: `auto` or `low`
- `user`: caller's own end-user or business marker

Partial or limited support:
- `n`: only `1`; requests for more still return one image or should be avoided.
- Default group `output_format`: accepts `png` or `jpeg`, but `jpeg` may still return PNG bytes.
- Default group `output_compression`: `0` to `100`; meaningful only if JPEG output actually takes effect.
- VIP/PRO `output_format`: supports `jpeg`; observed output is JPEG.
- VIP/PRO `output_compression`: `0` to `100` with `output_format=jpeg`.
- VIP/PRO `background`: default or `opaque`; `transparent` is not supported.

Example JSON for VIP 2K generation:

```json
{
  "model": "gpt-image-2-vip",
  "prompt": "An original anime character sheet, centered full-body teenager with headphones and a small crossbody bag, layered clothing, clean light background, refined line art, soft cel shading, no text, no watermark.",
  "size": "2048x2048",
  "quality": "high",
  "response_format": "b64_json"
}
```

Example cURL for VIP 4K widescreen generation:

```bash
curl https://apinebula.com/v1/images/generations \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2-vip",
    "prompt": "A cinematic anime background painting of a rain-washed mountain shrine path, stone steps, torii gate, wet moss, distant mist, no text, no watermark.",
    "size": "3840x2160",
    "quality": "high",
    "response_format": "b64_json"
  }'
```

## Edits

Endpoint: `POST https://apinebula.com/v1/images/edits`

Body is multipart form data.

Required fields:
- `model`: `gpt-image-2`, `gpt-image-2-vip`, or `gpt-image-2-pro`
- `prompt`: edit instruction
- `image`: one or more uploaded images. Repeat the `image` field for multiple reference images.

Common optional fields:
- `mask`: uploaded mask image for local repainting. For mask edits, original image and mask dimensions should match, and the mask should include an alpha channel.
- `size`: examples include `1536x1024` in the default group. VIP/PRO support `2048x2048`, `3840x2160`, and `2160x3840`.
- `quality`: `low`, `medium`, `high`, `auto`
- `response_format`: `b64_json` or `url`
- `input_fidelity`: `high` to follow input images more closely
- `background`: `opaque` or `transparent`
- `moderation`: `auto` or `low`
- `user`: caller's own end-user or business marker

Partial or limited support:
- `n`: only `1`.
- Default group `output_format`: accepts `png` or `jpeg`, but `jpeg` may still return PNG bytes.
- Default group `output_compression`: `0` to `100`; meaningful only if JPEG output actually takes effect.
- VIP/PRO `output_format`: supports `jpeg`; observed output is JPEG.
- VIP/PRO `output_compression`: `0` to `100` with `output_format=jpeg`.
- VIP/PRO `background`: default or `opaque`; `transparent` is not supported.

Example cURL for VIP reference-image edit:

```bash
curl https://apinebula.com/v1/images/edits \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "model=gpt-image-2-vip" \
  -F "prompt=Place the original anime character from the first image into the cherry-blossom riverside scene in the second image, preserving outfit details and matching sunset light, perspective, and soft shadows, anime film still quality, no text, no watermark." \
  -F "size=2048x2048" \
  -F "quality=high" \
  -F "response_format=url" \
  -F "input_fidelity=high" \
  -F "image=@anime-character.png" \
  -F "image=@anime-scenery.png"
```

Example cURL for VIP mask edit:

```bash
curl https://apinebula.com/v1/images/edits \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "model=gpt-image-2-vip" \
  -F "prompt=The entire image is covered by the black mask; repaint it as a different anime background: a rain-washed mountain shrine path with stone steps, torii gate, wet moss, and distant mist, no text, no watermark." \
  -F "size=2048x2048" \
  -F "quality=high" \
  -F "response_format=b64_json" \
  -F "input_fidelity=high" \
  -F "image=@anime-scenery.png" \
  -F "mask=@mask.png"
```

## Prompting Notes

For generation, specify subject, scene, style, aspect ratio, lighting, and any text that should appear.

For reference edits, state what to preserve, what to replace, output style, and the relationship between subjects across input images.

For mask edits, describe what the masked region should become and what should remain consistent outside the mask, such as lighting, perspective, and texture.
