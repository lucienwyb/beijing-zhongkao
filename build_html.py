#!/usr/bin/env python3
"""Convert all .md files in the repo to .html with a clean stylesheet + MathJax."""
import os
import re
from pathlib import Path
import markdown
from html import escape as _html_escape

from build_common import REPO_ROOT, favicon_links, og_tags

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

/* MathJax display styling */
mjx-container { font-size: 1.05em; }

/* ── 打印样式：学生可能打印真题卷做题 ── */
@media print {
  * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important }
  body { background: #fff !important; color: #000 !important; font-size: 11pt; max-width: 100%; padding: 0 0 8pt; }
  /* 隐藏站点导航、页脚、MathJax 离线提示等非题面元素 */
  .nav, .footer, .mathjax-offline-note { display: none !important }
  h1, h2 { border-bottom-color: #999 !important }
  /* 暗色模式下打印：强制标题/正文为黑色，避免深色主题覆盖导致白底浅字不可见 */
  h1, h2, h3, h4 { color: #000 !important }
  a { color: inherit !important }
  /* 避免题块跨页断开 */
  blockquote, table, pre, figure { break-inside: avoid; page-break-inside: avoid }
  /* MathJax 公式按原样打印，不做反色 */
  mjx-container { color: #000 !important }
  mjx-container[jax="CHTML"] { color: #000 !important }
}

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
}
@media (max-width: 600px) {
  body { padding: 20px 18px 72px; font-size: 15px; }
  h1 { font-size: 1.7em; }
  .nav { padding: 10px 12px; }
  .nav a { display: inline-block; margin: 3px 10px 3px 0; }
}
"""

MATHJAX = """
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
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
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
<noscript><p class="mathjax-offline-note" style="background:#fff9e8;border-left:4px solid #f1b84b;padding:10px 14px;border-radius:4px;font-size:13px">公式未渲染：本页需要 JavaScript 与网络加载 MathJax 才能正常显示公式。题干文字仍可阅读，若需公式请联网后刷新。</p></noscript>
<script>
// 离线打开时 MathJax 从 CDN 加载会失败，题面里的 $...$ 公式将保持原文。
// 检测加载失败并提示学生，避免困惑（题干文字本身不受影响）。
(function(){
  var s = document.getElementById('MathJax-script');
  if (!s) return;
  var done = false;
  s.addEventListener('load', function(){ done = true; });
  s.addEventListener('error', function(){ showNote(); });
  // window.MathJax 早已被上面的配置脚本赋值，因此用 MathJax.startup
  // （CDN 脚本加载后才挂载）判断是否真正加载成功。
  setTimeout(function(){ if(!window.MathJax || !window.MathJax.startup){ showNote(); } }, 5000);
  function showNote(){
    if(document.querySelector('.mathjax-offline-note')) return;
    var p = document.createElement('p');
    p.className = 'mathjax-offline-note';
    p.style.cssText = 'background:#fff9e8;border-left:4px solid #f1b84b;padding:10px 14px;border-radius:4px;font-size:13px;margin:16px 0';
    p.textContent = '公式未能加载（可能是离线或网络受限）。题干文字仍可阅读，联网刷新本页即可正常显示 $...$ 公式。';
    var n = document.querySelector('.nav');
    if(n){ n.parentNode.insertBefore(p, n.nextSibling); } else { document.body.insertBefore(p, document.body.firstChild); }
  }
})();
</script>
"""

def rewrite_md_links(html: str, md_rel: Path) -> str:
    """Rewrite in-body links so they resolve from the HTML output location.

    The markdown source lives at <md_rel> under the repo root, but the
    generated HTML lives at html/<md_rel with .html>. Two link kinds need
    different handling:

    - .md links: the target md is ALSO converted, so its HTML lives at
      html/<target.html>. Both source and target are mirrored under html/,
      so the original relative path is depth-correct as-is — only the
      suffix (.md→.html) and the root README.md→index.html rename need
      fixing. (We still recompute via relpath against html/<md_dir> so the
      root-README special case and any cross-tree .md link resolve
      correctly.)
    - non-.md links (e.g. downloads.html at the repo root, or the 2026
      viewer already inside html/): these point at real repo-relative
      files, NOT mirrored md. The md author wrote them for the md's own
      directory, but the HTML is one level deeper (under html/), so the
      depth is off — recompute via relpath from html/<md_dir>.

    Both cases reduce to: resolve the href to a repo-relative target,
    map it to its actual on-disk file path, then relpath from the HTML
    output directory html/<md_dir>.
    """
    md_dir = md_rel.parent                       # repo-relative, e.g. "math" or "."
    html_src_dir = Path("html") / md_dir         # repo-relative dir of output html

    def repl(m):
        href = m.group(1)
        if href.startswith(('http://', 'https://', '#', 'mailto:')):
            return m.group(0)
        # Split off the fragment (and any query) — only the path is rewritten.
        path_part, sep, frag = href.partition('#')
        frag = sep + frag if sep else ''
        if not path_part:
            return m.group(0)                     # pure in-page anchor
        # Resolve the link's target relative to the md's directory.
        target = os.path.normpath(os.path.join(str(md_dir), path_part))
        # Determine the actual on-disk target file:
        if target == 'README.md':
            file_target = Path('html') / 'index.html'      # root README → index.html
        elif target.endswith('.md'):
            file_target = Path('html') / (target[:-3] + '.html')  # mirrored under html/
        else:
            file_target = Path(target)             # real repo-relative file (downloads.html, viewer, …)
        new_path = os.path.relpath(str(file_target), str(html_src_dir))
        return f'href="{new_path}{frag}"'
    return re.sub(r'href="([^"]+)"', repl, html)

def convert_file(md_path: Path, out_path: Path):
    text = md_path.read_text(encoding='utf-8')
    # Python-Markdown requires a blank line before a list. Several papers put
    # answer options immediately after the question, so normalize that format.
    # Match bullet (-,+,*) and ordered (N.) list items, including those nested
    # inside blockquotes (lines like "> - foo" or "> 1. foo"). Without this,
    # ordered lists glued to a paragraph render as plain text, and bullets
    # inside a blockquote leak their "- " markers into the prose.
    _list_re = re.compile(r'^(>\s*)*\s*(?:[-+*]|\d+\.)\s+')
    # Inline answer keys like "1. C　2. B　3. B　4. A　5. B　6. C　7. D　8. C"
    # pack multiple numbered markers onto one line (separated by full-width
    # spaces). These are shorthand answer text, not real list items — if the
    # list regex matched them, Python-Markdown would parse only the leading
    # "1." as a marker and jam every other answer into a single <li>, producing
    # a broken one-item <ol>. Exclude such lines so they render as a <p>.
    _inline_key_re = re.compile(r'^\s*\d+\.\s+\S.*\d+\.\s+\S')

    def _is_list(line):
        return bool(_list_re.match(line)) and not _inline_key_re.match(line)

    lines = text.splitlines()
    normalized = []
    for line in lines:
        is_list_item = _is_list(line)
        prev = normalized[-1] if normalized else ''
        previous_is_list_item = bool(prev) and _is_list(prev)
        if is_list_item and prev.strip() and not previous_is_list_item:
            # Keep the separator inside the blockquote (a bare blank line would
            # terminate it); use an empty ">" line so the blockquote survives.
            normalized.append('>' if prev.lstrip().startswith('>') else '')
        elif not is_list_item and prev.strip() and _is_list(prev) and \
                prev.lstrip().startswith('>') and line.lstrip().startswith('>'):
            # Leaving a blockquote-internal list back to blockquote prose:
            # also need the ">" separator so the list closes cleanly.
            normalized.append('>')
        if _inline_key_re.match(line):
            # Escape the leading "N." so Python-Markdown's block list processor
            # does not treat it as an ordered-list marker (which would collapse
            # the whole answer key into one <li>). The inline pass renders
            # "\." back to ".", so the visible text is unchanged.
            line = re.sub(r'^(\s*\d+)\.', r'\1\\.', line)
        normalized.append(line)
    text = '\n'.join(normalized)
    # Fill-in blanks: sequences of 3+ underscores are meant as answer lines,
    # but Python-Markdown interprets them as <em>/<strong>. Replace with
    # full-width underscores so they render as stable blank lines.
    text = re.sub(r'_{3,}', lambda m: '＿' * len(m.group()), text)
    # Auto-link bare URLs (linkify extension unavailable in this env).
    # Skip URLs already inside backtick code spans (char before is `) —
    # wrapping those in <...> makes Python-Markdown mangle the code span.
    text = re.sub(r'(?<![">`])(https?://[^\s<）)]+)', r'<\1>', text)
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

    # SEO + social share: brand the title and derive a description from the H1.
    page_title = f"{title} · 京考进阶"
    description = f"{title}详解 · 京考进阶复习资料，核心考点、公式速查与历年真题精析。"

    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc', 'sane_lists'])
    body = md.convert(text)

    # Restore math fragments
    def _restore(m):
        idx = int(m.group(1))
        return math_stash[idx]
    body = re.sub(r'\x00MATH(\d+)\x00', _restore, body)

    # Rewrite .md -> .html and fix link depth for the html/ output location
    body = rewrite_md_links(body, md_path.relative_to(REPO_ROOT))

    # Relative path back to root for nav
    depth = len(md_path.relative_to(REPO_ROOT).parts) - 1
    root = '../' * depth if depth else ''

    plan_root = '../' * (depth + 1)
    nav = f'<div class="nav">📚 <a href="{plan_root}index.html">学习计划</a> · <a href="{root}math/exam-points.html">数学考点</a> · <a href="{root}physics/exam-points.html">物理考点</a> · <a href="{plan_root}index.html#mistakes">错题</a> · <a href="{plan_root}downloads.html">真题下载</a></div>'

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{_html_escape(description, quote=True)}">
{og_tags(page_title, description)}
{favicon_links(plan_root)}
<title>{_html_escape(page_title)}</title>
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
