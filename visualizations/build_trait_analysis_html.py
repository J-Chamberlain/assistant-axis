from __future__ import annotations

import base64
import html
import re
from pathlib import Path

import mistune


ROOT = Path(__file__).resolve().parent
MD_PATH = ROOT / "trait_analysis_summary.md"
OUT_DIR = ROOT / "trait-analysis"
HTML_PATH = OUT_DIR / "index.html"
EMBED_IMAGES = {
    "trait_layer_discrimination.png",
    "permutation_test.png",
}
DATA_LINKS = [
    ("role_trait_similarity.csv", "Raw role-trait cosine similarity matrix"),
    ("role_trait_similarity_zscored.csv", "Per-trait z-scored role-trait similarity matrix"),
    ("cluster_trait_profiles.csv", "Cluster-level trait profile table"),
    ("trait_role_analysis.py", "Reproducible analysis script"),
    ("trait_analysis_summary.md", "Markdown summary source"),
]


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


def build_data_links() -> str:
    items = []
    for filename, description in DATA_LINKS:
        href = f"../{filename}"
        items.append(f'<li><a href="{href}">{filename}</a> - {html.escape(description)}</li>')
    return "<ul>\n" + "\n".join(items) + "\n</ul>"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    markdown_text = MD_PATH.read_text()
    markdown_text = embed_selected_images(markdown_text)

    renderer = HeadingRenderer()
    markdown = mistune.create_markdown(renderer=renderer, plugins=["table", "strikethrough"])
    body_html = markdown(markdown_text)
    toc_html = build_toc(MD_PATH.read_text())
    data_links_html = build_data_links()

    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Trait Analysis Appendix</title>
  <style>
    body {{
      margin: 0;
      background: #ffffff;
      color: #1f2328;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.6;
    }}
    main {{
      max-width: 860px;
      margin: 0 auto;
      padding: 40px 24px 64px;
    }}
    h1, h2, h3 {{
      line-height: 1.25;
      margin-top: 1.8em;
    }}
    h1 {{
      margin-top: 0;
      font-size: 2.0rem;
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
    .lead {{
      border: 1px solid #d0d7de;
      border-radius: 12px;
      padding: 20px 24px;
      background: #f6f8fa;
      margin: 24px 0 32px;
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
    .toc-level-1 {{
      margin-left: 0;
      font-weight: 700;
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
    <p><a href="../research_paper.html">Back to original research paper</a></p>
    <div class="lead">
      <h1>Trait Analysis Appendix</h1>
      <p>
        Separate GH Pages appendix for the role-trait similarity analysis over the Gemma 2 27B
        Assistant Axis dataset. This page preserves the earlier paper URL while publishing the
        new cluster-trait and permutation-test results at a distinct path.
      </p>
    </div>
    <div class="toc-wrap">
      <h2 id="table-of-contents">Table of Contents</h2>
      {toc_html}
    </div>
    {body_html}
    <h2 id="downloads">Downloads</h2>
    {data_links_html}
    <footer>
      Trait-analysis appendix for the Assistant Axis project |
      Published on GitHub Pages at
      <a href="https://j-chamberlain.github.io/assistant-axis/visualizations/trait-analysis/">https://j-chamberlain.github.io/assistant-axis/visualizations/trait-analysis/</a>
    </footer>
  </main>
</body>
</html>
"""
    HTML_PATH.write_text(html_text)
    print(f"Wrote {HTML_PATH} ({HTML_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
