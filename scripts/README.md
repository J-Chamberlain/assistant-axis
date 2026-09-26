# Gemini Image to Text

`gemini_image_to_text.py` sends an image directly to the Gemini API and prints a detailed plain-text description for non-multimodal agents.

## Setup

Create `assistant-axis/.env` or export the variable in your shell:

```bash
GEMINI_API_KEY=your_api_key_here
```

Optional:

```bash
GEMINI_MODEL=gemini-2.5-flash
```

## Usage

Describe an image file:

```bash
uv run python scripts/gemini_image_to_text.py path/to/image.png
```

Describe the current macOS clipboard image:

```bash
uv run python scripts/gemini_image_to_text.py --clipboard
```

Describe an image URL:

```bash
uv run python scripts/gemini_image_to_text.py https://example.com/image.jpg
```

The script uses inline image input, which is suitable for requests under Gemini's 20MB inline limit.
