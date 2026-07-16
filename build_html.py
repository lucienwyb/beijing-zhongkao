#!/usr/bin/env python3
"""Convert all .md files in the repo to .html with a clean stylesheet + MathJax."""
import os
import re
from pathlib import Path
import markdown

REPO_ROOT = Path(__file__).resolve().parent
OUT_ROOT = REPO_ROOT / "html"

CSS = """
* { box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB",
               "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
  line-height: 1.75;
  color: #24292f;
  background: #ffffff;
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 40px 96px;
  font-size: 16px;
}
h1, h2, h3, h4 { border-bottom: none; margin-top: 1.5em; margin-bottom: 0.6em; font-weight: 600; color: #1f2328; }
h1 { font-size: 2em; border-bottom: 2px solid #d0d7de; padding-bottom: 8px; }
h2 { font-size: 1.5em; border-bottom: 1px solid #d0d7de; padding-bottom: 6px; }
h3 { font-size: 1.25em; }
h4 { font-size: 1.1em; color: #57606a; }
p, li { line-height: 1.85; }
strong { color: #0969da; }
blockquote {
  border-left: 4px solid #d0d7de;
  color: #57606a;
  margin: 1em 0;
  padding: 6px 16px;
  background: #f6f8fa;
  border-radius: 4px;
}
code {
  background: #f6f8fa;
  color: #d73a49;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: "SF Mono", Menlo, Monaco, Consolas, monospace;
  font-size: 0.92em;
}
pre {
  background: #f6f8fa;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
}
pre code { background: none; padding: 0; color: #24292f; }
table {
  border-collapse: collapse;
  margin: 1em 0;
  width: 100%;
  font-size: 0.95em;
  display: block;
  overflow-x: auto;
}
th, td { border: 1px solid #d0d7de; padding: 8px 12px; text-align: left; }
th { background: #f6f8fa; font-weight: 600; }
tr:nth-child(even) td { background: #fafbfc; }
a { color: #0969da; text-decoration: none; }
a:hover { text-decoration: underline; }
hr { border: none; border-top: 1px solid #d0d7de; margin: 2em 0; }
.emoji { font-size: 1.2em; }
.nav {
  background: #f6f8fa;
  border: 1px solid #d0d7de;
  border-radius: 8px;
  padding: 12px 20px;
  margin-bottom: 24px;
  font-size: 0.95em;
}
.nav a { margin-right: 16px; }
.footer {
  margin-top: 60px;
  padding-top: 20px;
  border-top: 1px solid #d0d7de;
  color: #57606a;
  font-size: 0.9em;
  text-align: center;
}
.missing-figure {
  margin: -0.35em 0 1.2em;
  padding: 10px 12px;
  border-left: 4px solid #bf8700;
  background: #fff8c5;
  color: #633c01;
  font-size: 0.9em;
  border-radius: 4px;
}
.missing-figure a { font-weight: 600; }

/* MathJax display styling */
mjx-container { font-size: 1.05em; }

/* Dark mode */
@media (prefers-color-scheme: dark) {
  body { background: #0d1117; color: #c9d1d9; }
  h1, h2, h3, h4 { color: #f0f6fc; }
  h1, h2 { border-bottom-color: #30363d; }
  h4 { color: #8b949e; }
  strong { color: #58a6ff; }
  blockquote { background: #161b22; color: #8b949e; border-left-color: #30363d; }
  code { background: #161b22; color: #ff7b72; }
  pre { background: #161b22; }
  pre code { color: #c9d1d9; }
  th, td { border-color: #30363d; }
  th { background: #161b22; }
  tr:nth-child(even) td { background: #0d1117; }
  a { color: #58a6ff; }
  hr { border-top-color: #30363d; }
  .nav { background: #161b22; border-color: #30363d; }
  .footer { border-top-color: #30363d; color: #8b949e; }
  .missing-figure { background: #2d2515; color: #eac54f; border-left-color: #d29922; }
}
@media (max-width: 600px) {
  body { padding: 20px 18px 72px; font-size: 15px; }
  h1 { font-size: 1.7em; }
  .nav { padding: 10px 12px; }
  .nav a { display: inline-block; margin: 3px 10px 3px 0; }
}
"""

MATHJAX = """
<script>
window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
    displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
    processEscapes: true
  },
  svg: { fontCache: 'global' }
};
</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
"""

def rewrite_md_links(html: str, rel_depth: int) -> str:
    """Rewrite .md links to .html so navigation between pages works."""
    def repl(m):
        href = m.group(1)
        if href.startswith(('http://', 'https://', '#', 'mailto:')):
            return m.group(0)
        if href.endswith('.md'):
            href = href[:-3] + '.html'
        return f'href="{href}"'
    return re.sub(r'href="([^"]+)"', repl, html)

def mark_missing_figures(html: str, resources_href: str) -> str:
    """Figure omissions are already marked inline in source md as 〔需配图〕;
    this previously injected a duplicate yellow box, which double-flagged
    figures and split question/option paragraphs. Inline text is sufficient."""
    return html

def convert_file(md_path: Path, out_path: Path):
    text = md_path.read_text(encoding='utf-8')
    # Python-Markdown requires a blank line before a list. Several papers put
    # answer options immediately after the question, so normalize that format.
    lines = text.splitlines()
    normalized = []
    for line in lines:
        is_list_item = re.match(r'^\s*[-+*]\s+', line) is not None
        previous_is_list_item = bool(normalized and re.match(r'^\s*[-+*]\s+', normalized[-1]))
        if is_list_item and normalized and normalized[-1].strip() and not previous_is_list_item:
            normalized.append('')
        normalized.append(line)
    text = '\n'.join(normalized)
    # Fill-in blanks: sequences of 3+ underscores are meant as answer lines,
    # but Python-Markdown interprets them as <em>/<strong>. Replace with
    # full-width underscores so they render as stable blank lines.
    text = re.sub(r'_{3,}', lambda m: '＿' * len(m.group()), text)
    # Auto-link bare URLs (linkify extension unavailable in this env)
    text = re.sub(r'(?<![">])(https?://[^\s<）)]+)', r'<\1>', text)
    # Protect math fragments from Python-Markdown backslash escaping.
    # Markdown eats \\ (cases row break) and \! (negative thin space) inside $...$,
    # corrupting the math. Stash math, convert, then restore.
    math_stash = []
    def _stash(m):
        math_stash.append(m.group(0))
        return f'\x00MATH{len(math_stash)-1}\x00'
    text = re.sub(r'\$\$.*?\$\$', _stash, text, flags=re.DOTALL)
    text = re.sub(r'\$[^$\n]+?\$', _stash, text)
    # Escape backslashes in stashed math is unnecessary; we just skip markdown processing.
    # Extract first h1 as title, fallback to filename
    title_m = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
    title = title_m.group(1).strip() if title_m else md_path.stem

    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc', 'sane_lists'])
    body = md.convert(text)

    # Restore math fragments
    def _restore(m):
        idx = int(m.group(1))
        return math_stash[idx]
    body = re.sub(r'\x00MATH(\d+)\x00', _restore, body)

    # Rewrite .md -> .html
    body = rewrite_md_links(body, 0)

    # Relative path back to root for nav
    depth = len(md_path.relative_to(REPO_ROOT).parts) - 1
    root = '../' * depth if depth else ''
    body = mark_missing_figures(body, f'{root}papers/sources/README.html')

    plan_root = '../' * (depth + 1)
    nav = f'<div class="nav">📚 <a href="{plan_root}index.html">学习计划</a> · <a href="{root}math/exam-points.html">数学考点</a> · <a href="{root}physics/exam-points.html">物理考点</a> · <a href="{plan_root}index.html#mistakes">错题</a> · <a href="{plan_root}downloads.html">真题下载</a></div>'

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>{CSS}</style>
{MATHJAX}
</head>
<body>
{nav}
{body}
<div class="footer">北京中考数学 & 物理 · 核心考点与真题精析 ·
<a href="https://github.com/lucienwyb/beijing-zhongkao">GitHub</a> ·
<a href="https://gitee.com/lucienwyb/beijing-zhongkao">Gitee</a></div>
</body>
</html>
"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding='utf-8')

def main():
    md_files = list(REPO_ROOT.glob('**/*.md'))
    md_files = [p for p in md_files if 'html/' not in str(p) and '.git' not in str(p)]
    print(f"Converting {len(md_files)} markdown files → html/")
    for md in md_files:
        rel = md.relative_to(REPO_ROOT)
        # README.md at root → index.html; others: math/exam-points.md → html/math/exam-points.html
        if rel.name == 'README.md' and len(rel.parts) == 1:
            out = OUT_ROOT / 'index.html'
        else:
            out = OUT_ROOT / rel.with_suffix('.html')
        convert_file(md, out)
        print(f"  {rel} → html/{out.relative_to(OUT_ROOT)}")
    print(f"\n✓ Done. Open: file://{OUT_ROOT}/index.html")

if __name__ == '__main__':
    main()
