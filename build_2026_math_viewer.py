#!/usr/bin/env python3
"""Build a consolidated 2026 Beijing math paper viewer from the 4 WeChat sources."""
import os, re, html, json
from pathlib import Path

from build_common import REPO_ROOT as ROOT, favicon_links, og_tags, IMAGE_MIN_BYTES, VIEWER_BADGE_SMALL, VIEWER_BADGE_HD

MATH_DIR = ROOT / 'papers/downloaded/2026/math'
OUT = ROOT / 'html/papers/2026-math-viewer.html'

# The 4 WeChat sources, ordered by content quality (largest image bundles +
# cleanest content first). The first entry is the "primary" source — shown
# expanded by default; the rest are collapsed as "对照版本".
#
# MAINTENANCE: to add a 5th source, append a dict with:
#   slug  — short identifier used in the URL fragment (#src-<slug>)
#   title — display name (shown in tab + section header)
#   note  — 1-line description of the source's strengths
#   dir   — directory name under papers/downloaded/2026/math/ (must end with _imgs)
SOURCES = [
    {
        'slug': 'albert',
        'title': 'Albert · 官方标答 + 后三题解析',
        'note': '独立数学老师整理，含官方标答和最后三道大题的图解。图片清晰、无营销内容。',
        'dir': '2026-math_wx_2026年北京中考数学试卷及官方标答_附后三道题解析__imgs',
    },
    {
        'slug': 'jiao',
        'title': '焦老师 · 6·24 学业水平考试原卷',
        'note': '按考试日期（2026-06-24）标注的原卷扫描，图片分辨率最高，含答案页。',
        'dir': '2026-math_wx__北京中考真题_2026_6_24北京市初中学业水平数学考试试卷_附答案__imgs',
    },
    {
        'slug': 'xdf',
        'title': '新东方北京中考研究所 · 官方版',
        'note': '大机构整理版，图片分辨率高，前几张为营销页，从 img_002 起是试题。',
        'dir': '2026-math_wx_2026北京中考数学试卷真题答案来啦_官方版_快下载__imgs',
    },
    {
        'slug': 'zhentt',
        'title': '西城观察 · 逐题分屏版',
        'note': '把整卷切成小图逐题展示，33 张图更细，但分辨率低。适合手机端一题一图对照。',
        'dir': '2026-math_wx_2026年北京中考数学真题_及答案__imgs',
    },
]

# Marketing filler: skip img_000, img_001, img_last-2 etc. based on size threshold
# (IMAGE_MIN_BYTES from build_common — shared with build_downloads so counts match).
# Among included images, <VIEWER_BADGE_SMALL are labeled "封面/尾图" so viewer can skim past;
# >VIEWER_BADGE_HD are labeled "高清".


def collect(src):
    d = MATH_DIR / src['dir']
    if not d.is_dir():
        return []
    items = []
    for f in sorted(d.iterdir()):
        if f.suffix.lower() not in ('.jpg', '.png', '.webp', '.gif'):
            continue
        size = f.stat().st_size
        if size < IMAGE_MIN_BYTES:
            continue
        # relative from OUT (html/papers/2026-math-viewer.html)
        rel = os.path.relpath(f, OUT.parent)
        items.append({'src': rel, 'size': size, 'idx': int(re.search(r'(\d+)', f.stem).group(1))})
    items.sort(key=lambda x: x['idx'])
    return items


def render_source(src, imgs, primary=False):
    if not imgs:
        return ''
    cards = []
    for i, im in enumerate(imgs):
        sz = im['size']
        badge = ''
        if sz < VIEWER_BADGE_SMALL:
            badge = '<span class="badge badge-hint">封面/尾图</span>'
        elif sz > VIEWER_BADGE_HD:
            badge = '<span class="badge badge-hd">高清</span>'
        # 首图（每组第 1 张）加 fetchpriority=high 提升 LCP 加载优先级
        priority = ' fetchpriority="high"' if i == 0 else ''
        cards.append(
            f'<figure class="pg"><img loading="lazy"{priority} src="{html.escape(im["src"])}" '
            f'alt="{html.escape(src["title"])} 第 {i+1} 张" '
            f'tabindex="0" role="button" aria-label="放大查看 第 {i+1} 张">'
            f'<figcaption>#{i+1:02d} · {sz//1024} KB {badge}</figcaption></figure>'
        )
    grid = f'<div class="grid">{" ".join(cards)}</div>'
    rec = '<span class="badge badge-rec">推荐</span> ' if primary else ''
    body = f'''
  <header>
    <h2>{rec}{html.escape(src['title'])}</h2>
    <p class="note">{html.escape(src['note'])}</p>
    <p class="stat">{len(imgs)} 张图 · 平均 {sum(x['size'] for x in imgs)//len(imgs)//1024} KB</p>
  </header>
  {grid}'''
    if primary:
        return f'<section class="src" id="src-{src["slug"]}">{body}</section>'
    # non-primary sources collapsed to reduce repetition
    return f'<section class="src src-alt" id="src-{src["slug"]}"><details><summary>对照版本：{html.escape(src["title"].split(" · ")[0])} · {len(imgs)} 张图（点击展开）</summary>{body}</details></section>'


def main():
    sources_data = [(s, collect(s)) for s in SOURCES]
    total_imgs = sum(len(items) for _, items in sources_data)

    tabs = ''.join(
        f'<a href="#src-{s["slug"]}" class="tab" data-slug="{s["slug"]}">{html.escape(s["title"].split(" · ")[0])} <small>{len(imgs)}</small></a>'
        for s, imgs in sources_data
    )

    sections = '\n'.join(render_source(s, imgs, primary=(i == 0)) for i, (s, imgs) in enumerate(sources_data))

    page = f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="2026 北京中考数学卷整卷图片版 · 4 份来源交叉校对">
{og_tags('2026 北京中考数学 · 整卷图片版 · 京考进阶', f'2026 北京中考数学卷整卷图片版 · 4 份来源交叉校对，含官方标答，{total_imgs} 张试题图逐张浏览。')}
{favicon_links('../../')}
<title>2026 北京中考数学 · 整卷图片版 · 京考进阶</title>
<link rel="stylesheet" href="../../styles.css">
<style>
  body{{background:var(--paper);color:var(--ink)}}
  .viewer-hero{{padding:52px clamp(20px,6vw,80px) 24px;background:var(--paper)}}
  .viewer-hero h1{{font-family:"Noto Serif SC","Songti SC",serif;font-size:clamp(28px,3.6vw,44px);margin:0 0 12px;font-weight:800}}
  .viewer-hero p{{color:var(--muted);line-height:1.75;margin:0 0 8px;max-width:760px}}
  .viewer-hero .warn{{background:#fff9e8;border:1px solid #dfc16d;border-left:4px solid var(--yellow);
    padding:14px 18px;border-radius:4px;font-size:13px;line-height:1.65;margin-top:20px;max-width:820px}}
  .viewer-hero .warn strong{{color:var(--ink)}}
  .tabs{{padding:0 clamp(20px,6vw,80px);display:flex;gap:8px;flex-wrap:wrap;
    border-bottom:1px solid var(--line);background:var(--paper);
    position:sticky;top:68px;z-index:10;padding-bottom:0}}
  .tab{{padding:12px 18px 14px;border-bottom:3px solid transparent;font-size:13px;font-weight:700;color:var(--muted)}}
  .tab small{{display:inline-block;margin-left:4px;color:var(--green);font-family:Georgia,serif}}
  .tab:hover{{color:var(--ink)}}
  .tab:target,.tab:active,.tab.active{{border-bottom-color:var(--green);color:var(--ink)}}
  main.viewer{{padding:20px 0 60px}}
  .src{{padding:36px clamp(20px,6vw,80px);border-top:1px solid var(--line);background:var(--white)}}
  .src:nth-child(even){{background:var(--paper)}}
  .src header h2{{font-family:"Noto Serif SC","Songti SC",serif;font-size:22px;margin:0 0 6px}}
  .src .note{{margin:0 0 4px;color:var(--muted);font-size:13.5px;line-height:1.65;max-width:760px}}
  .src .stat{{margin:0 0 22px;color:var(--green);font-size:12px;font-weight:700}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px}}
  .pg{{margin:0;background:#fff;border:1px solid var(--line);border-radius:4px;
    overflow:hidden;display:flex;flex-direction:column}}
  .pg img{{width:100%;height:auto;display:block;background:#f7f5ee;cursor:zoom-in}}
  .pg img:hover{{opacity:.92}}
  .pg img.img-failed{{min-height:100px;padding:30px 20px;font-size:13px;color:#61706b;text-align:center;cursor:default}}
  .pg img.img-failed:hover{{opacity:1}}
  .pg figcaption{{padding:8px 10px;font-size:11px;color:var(--muted);
    display:flex;justify-content:space-between;align-items:center;gap:8px;
    border-top:1px solid var(--line);background:#fafaf7}}
  .badge{{font-size:10px;font-weight:800;padding:2px 6px;border-radius:2px}}
  .badge-hint{{background:#f4f2eb;color:#6e6759}}
  .badge-hd{{background:var(--green-soft);color:var(--green)}}
  .badge-rec{{background:#fff9e8;color:#a06a00;border:1px solid #dfc16d;padding:1px 8px;border-radius:4px;font-size:12px;vertical-align:middle}}
  .src-alt{{background:#faf9f6;border:1px solid #e8e5dd;border-radius:8px;margin-top:16px}}
  .src-alt details summary{{cursor:pointer;padding:14px 18px;font-weight:600;color:var(--ink)}}
  .src-alt details summary:hover{{background:#f3f1ea;border-radius:8px}}
  .lb-counter{{position:absolute;bottom:24px;left:50%;transform:translateX(-50%);color:#fff;font-size:14px;opacity:.85;background:rgba(0,0,0,.35);padding:4px 12px;border-radius:12px}}
  /* Lightbox */
  .lb{{position:fixed;inset:0;background:rgba(20,32,29,.92);z-index:100;display:none;
    align-items:center;justify-content:center;padding:24px;cursor:zoom-out}}
  .lb.open{{display:flex}}
  .lb img{{max-width:100%;max-height:100%;object-fit:contain;box-shadow:0 20px 60px rgba(0,0,0,.5)}}
  .lb .close{{position:absolute;top:20px;right:24px;color:#fff;font-size:28px;font-weight:700;cursor:pointer;border:0;background:transparent;border-radius:4px}}
  .lb .nav-btn{{position:absolute;top:50%;transform:translateY(-50%);color:#fff;font-size:40px;font-weight:700;cursor:pointer;background:rgba(0,0,0,.3);border:none;width:48px;height:64px;border-radius:8px;display:flex;align-items:center;justify-content:center}}
  .lb .prev{{left:16px}}
  .lb .next{{right:16px}}
  @media(max-width:700px){{
    .viewer-hero h1{{font-size:24px}}
    .tabs{{padding:0 16px;overflow-x:auto;white-space:nowrap;flex-wrap:nowrap;top:68px}}
    .tab{{padding:10px 12px 12px;font-size:12px}}
    .src{{padding:28px 16px}}
    .grid{{grid-template-columns:1fr;gap:10px}}
  }}
  /* 打印真题图片版：隐藏灯箱/标签栏/交互，展开对照版本，逐张图片打印 */
  @media print{{
    *{{-webkit-print-color-adjust:exact !important;print-color-adjust:exact !important}}
    body{{background:#fff !important;color:#000}}
    .topbar,.tabs,.lb,.viewer-hero .warn,.badge-hint{{display:none !important}}
    .viewer-hero,.src{{padding:0 0 8pt}}
    .src-alt{{border:0;margin:0}}
    .src-alt details>summary{{display:none}}
    .src-alt details{{display:block}}
    .grid{{grid-template-columns:repeat(2,1fr) !important;gap:6pt}}
    .pg,.pg img{{break-inside:avoid;page-break-inside:avoid}}
    .pg figcaption{{font-size:9pt;background:#fff !important;border-top:1px solid #999}}
  }}
</style>
</head>
<body>
<header class="topbar">
  <a class="brand" href="../../index.html" aria-label="返回首页">
    <span class="brand-mark">京</span><span>京考进阶</span>
  </a>
  <nav aria-label="主导航">
    <a href="../../index.html#today">今日</a>
    <a href="../../index.html#plan">计划</a>
    <a href="../../index.html#materials">资料</a>
    <a href="../../index.html#mistakes">错题</a>
    <a href="../../downloads.html">真题下载</a>
  </nav>
  <a class="icon-button" href="../../downloads.html#y2026" title="下载页" aria-label="返回下载页">←</a>
</header>

<section class="viewer-hero">
  <p class="eyebrow">2026-06-24 · 北京市初中学业水平数学考试</p>
  <h1>2026 数学 · 整卷图片版</h1>
  <p>这里收录了从微信公众号收集到的 4 份图片版试卷，全部指向同一份 2026-06-24 北京中考数学卷（100 分 · 120 分钟）。
    每份来源各有偏重：Albert 版含官方标答和后三题解析，焦老师版分辨率最高，新东方版覆盖官方答案，西城观察版逐题切分。</p>
  <p class="warn">
    <strong>使用建议：</strong>默认展开 Albert 版（含官方标答），其余 3 份折叠为对照版本，需要时点开即可；
    <a href="../../downloads.html#y2026">下载页</a> 可获取全部高清原图。
    图片单击放大，放大后可用 <strong>← →</strong> 翻页、<strong>Esc</strong> 关闭。
  </p>
</section>

<nav class="tabs" aria-label="来源切换">{tabs}</nav>

<main class="viewer">
{sections}
</main>

<footer><span>京考进阶 · 4 份来源共 {total_imgs} 张图 · 数据仅本地保存</span><a href="../../downloads.html#y2026">下载原始文件 ↗</a></footer>

<div class="lb" id="lb" role="dialog" aria-modal="true" aria-label="图片放大预览"><button class="close" type="button" aria-label="关闭">×</button><button class="nav-btn prev" type="button" aria-label="上一张">‹</button><img alt="放大预览"><button class="nav-btn next" type="button" aria-label="下一张">›</button><span class="lb-counter" id="lbCounter" aria-live="polite"></span></div>
<noscript><p style="padding:18px 24px;background:#fff9e8;border:1px solid #dfc16d;border-left:4px solid #f1b84b;margin:0;font-size:14px;line-height:1.7">图片版查看器依赖 JavaScript 实现放大浏览与来源切换。未启用 JavaScript 时，下方试题图片仍可逐张查看，但无法点击放大。</p></noscript>
<script>
const lb = document.getElementById('lb'), lbImg = lb.querySelector('img'), lbCounter = document.getElementById('lbCounter');
const lbClose = lb.querySelector('.close');
let curImgs = [], cur = -1, lastFocused = null;
function show(i){{
  if (!curImgs.length) return;
  cur = (i + curImgs.length) % curImgs.length;
  lbImg.src = curImgs[cur].src;
  lbImg.alt = curImgs[cur].alt || '放大预览';
  lbCounter.textContent = (cur + 1) + ' / ' + curImgs.length;
  lb.classList.add('open');
  lbClose.focus();
}}
function closeLb(){{ lb.classList.remove('open'); if (lastFocused) lastFocused.focus(); }}
document.querySelectorAll('.pg img').forEach(im => {{
  // Image error fallback: if lazy-loaded image fails (network/CDN/corruption),
  // show alt text as placeholder instead of a bare broken-image icon.
  if (im.complete && im.naturalWidth === 0) {{ im.alt = '图片加载失败'; im.classList.add('img-failed'); }}
  im.addEventListener('error', () => {{ im.alt = '图片加载失败'; im.classList.add('img-failed'); }});
  const open = () => {{
    lastFocused = im;
    const sec = im.closest('.src');
    curImgs = Array.from(sec.querySelectorAll('.pg img'));
    show(curImgs.indexOf(im));
  }};
  im.onclick = open;
  im.addEventListener('keydown', e => {{
    if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); open(); }}
  }});
}});
// Lightbox image error: show message in counter instead of blank
lbImg.addEventListener('error', () => {{ lbCounter.textContent = '图片加载失败'; }});
lbClose.onclick = (e) => {{ e.stopPropagation(); closeLb(); }};
lb.querySelector('.prev').onclick = (e) => {{ e.stopPropagation(); show(cur - 1); }};
lb.querySelector('.next').onclick = (e) => {{ e.stopPropagation(); show(cur + 1); }};
lb.onclick = (e) => {{ if (e.target === lb) closeLb(); }};
document.addEventListener('keydown', e => {{
  if (!lb.classList.contains('open')) return;
  if (e.key === 'Escape') {{ e.preventDefault(); closeLb(); }}
  else if (e.key === 'ArrowLeft') {{ e.preventDefault(); show(cur - 1); }}
  else if (e.key === 'ArrowRight') {{ e.preventDefault(); show(cur + 1); }}
  else if (e.key === 'Tab') {{
    e.preventDefault();
    const f = [lbClose, lb.querySelector('.prev'), lb.querySelector('.next')];
    const idx = f.indexOf(document.activeElement);
    const n = e.shiftKey ? (idx <= 0 ? f.length - 1 : idx - 1) : (idx + 1) % f.length;
    f[n].focus();
  }}
}});
// Tab switching: highlight active tab + expand its <details> on click
const tabLinks = document.querySelectorAll('.tab');
function activateTab(slug){{
  tabLinks.forEach(t => t.classList.toggle('active', t.dataset.slug === slug));
  const sec = document.getElementById('src-' + slug);
  if (sec){{ const det = sec.querySelector('details'); if (det) det.open = true; }}
}}
tabLinks.forEach(t => t.addEventListener('click', () => activateTab(t.dataset.slug)));
// initial: highlight first (primary) tab
if (tabLinks.length) tabLinks[0].classList.add('active');
</script>
</body>
</html>'''
    OUT.write_text(page, encoding='utf-8')
    print(f'✓ Wrote {OUT}')
    print(f'  {len(sources_data)} sources, {total_imgs} images total')
    for s, imgs in sources_data:
        print(f'  · {s["slug"]:10s} {len(imgs):3d} imgs')


if __name__ == '__main__':
    main()
