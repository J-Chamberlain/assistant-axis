from __future__ import annotations

import base64
import html
import re
from pathlib import Path

import mistune


ROOT = Path(__file__).resolve().parent
MD_PATH = ROOT / "research_paper.md"
HTML_PATH = ROOT / "research_paper.html"
EMBED_IMAGES = {
    "axis_ranking_layer45.png",
    "layer_depth_heatmap.png",
    "cluster_distances.png",
}


def slugify(text: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", text).strip().lower()
    slug = re.sub(r"[\s_]+", "-", slug)
    return slug


def embed_selected_images(markdown_text: str) -> str:
    def replacer(match: re.Match[str]) -> str:
        alt_text, target = match.group(1), match.group(2)
        path = ROOT / target
        if path.name not in EMBED_IMAGES or not path.exists():
            return match.group(0)
        mime = "image/png"
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"![{alt_text}](data:{mime};base64,{data})"

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replacer, markdown_text)


class HeadingRenderer(mistune.HTMLRenderer):
    def heading(self, text: str, level: int, **attrs) -> str:
        anchor = slugify(re.sub(r"<[^>]+>", "", text))
        return f'<h{level} id="{anchor}">{text}</h{level}>\n'


def build_toc(markdown_text: str) -> str:
    toc_items = []
    for line in markdown_text.splitlines():
        if not line.startswith("#"):
            continue
        hashes, title = line.split(" ", 1)
        level = len(hashes)
        if level > 3:
            continue
        anchor = slugify(title)
        css_class = f"toc-level-{level}"
        toc_items.append(f'<li class="{css_class}"><a href="#{anchor}">{html.escape(title)}</a></li>')
    return "<ul class='toc'>\n" + "\n".join(toc_items) + "\n</ul>"


def main() -> None:
    markdown_text = MD_PATH.read_text()
    markdown_text = embed_selected_images(markdown_text)

    renderer = HeadingRenderer()
    markdown = mistune.create_markdown(renderer=renderer, plugins=["table", "strikethrough"])
    body_html = markdown(markdown_text)
    toc_html = build_toc(MD_PATH.read_text())

    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>The Persona Space of Language Models</title>
  <style>
    body {{
      margin: 0;
      background: #ffffff;
      color: #1f2328;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.6;
    }}
    main {{
      max-width: 800px;
      margin: 0 auto;
      padding: 40px 24px 64px;
    }}
    h1, h2, h3 {{
      line-height: 1.25;
      margin-top: 1.8em;
    }}
    h1 {{
      margin-top: 0;
      font-size: 2.1rem;
    }}
    h2 {{
      border-bottom: 1px solid #e5e7eb;
      padding-bottom: 0.2em;
    }}
    p, li {{
      font-size: 1rem;
    }}
    code {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      background: #f6f8fa;
      padding: 0.1em 0.3em;
      border-radius: 4px;
      font-size: 0.95em;
    }}
    pre code {{
      display: block;
      padding: 1em;
      overflow-x: auto;
    }}
    a {{
      color: #0969da;
      text-decoration: none;
    }}
    a:hover {{
      text-decoration: underline;
    }}
    img {{
      display: block;
      max-width: 100%;
      height: auto;
      margin: 20px auto;
      border: 1px solid #e5e7eb;
    }}
    .toc-wrap {{
      border: 1px solid #e5e7eb;
      border-radius: 10px;
      padding: 20px 24px;
      background: #fafbfc;
      margin: 24px 0 32px;
    }}
    .toc {{
      list-style: none;
      padding-left: 0;
      margin: 0;
    }}
    .toc li {{
      margin: 6px 0;
    }}
    .toc-level-2 {{
      margin-left: 0;
      font-weight: 600;
    }}
    .toc-level-3 {{
      margin-left: 18px;
      font-weight: 400;
    }}
    footer {{
      border-top: 1px solid #e5e7eb;
      margin-top: 48px;
      padding-top: 18px;
      color: #57606a;
      font-size: 0.95rem;
    }}
  </style>
</head>
<body>
  <main>
    <div class="toc-wrap">
      <h2 id="table-of-contents">Table of Contents</h2>
      {toc_html}
    </div>
    {body_html}
    <footer>
      Analysis conducted May 2026 | Data source: lu-christina/assistant-axis-vectors (HuggingFace) | Source paper: Lu et al. (2026) arxiv:2601.10387
    </footer>
  </main>
</body>
</html>
"""
    HTML_PATH.write_text(html_text)
    size = HTML_PATH.stat().st_size
    print(f"Wrote {HTML_PATH.name} ({size} bytes)")


if __name__ == "__main__":
    main()
