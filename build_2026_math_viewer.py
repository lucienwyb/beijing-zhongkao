#!/usr/bin/env python3
"""Build a consolidated 2026 Beijing math paper viewer from the 4 WeChat sources."""
import os, re, html, json
from pathlib import Path

ROOT = Path('/pulp/beijing-zhongkao')
MATH_DIR = ROOT / 'papers/downloaded/2026/math'
OUT = ROOT / 'html/papers/2026-math-viewer.html'

# The 4 sources, ordered by content quality (largest image bundles + cleanest content)
SOURCES = [
    {
        'slug': 'albert',
        'title': 'Albert · 官方标答 + 后三题解析',
        'note': '独立数学老师整理，含官方标答和最后三道大题的图解。图片清晰、无营销内容。',
        'dir': '2026-math_wx_2026年北京中考数学试卷及官方标答_附后三道题解析__imgs',
        'article': '2026-math_wx_2026年北京中考数学试卷及官方标答_附后三道题解析_.html',
    },
    {
        'slug': 'jiao',
        'title': '焦老师 · 6·24 学业水平考试原卷',
        'note': '按考试日期（2026-06-24）标注的原卷扫描，图片分辨率最高，含答案页。',
        'dir': '2026-math_wx__北京中考真题_2026_6_24北京市初中学业水平数学考试试卷_附答案__imgs',
        'article': '2026-math_wx__北京中考真题_2026_6_24北京市初中学业水平数学考试试卷_附答案_.html',
    },
    {
        'slug': 'xdf',
        'title': '新东方北京中考研究所 · 官方版',
        'note': '大机构整理版，图片分辨率高，前几张为营销页，从 img_002 起是试题。',
        'dir': '2026-math_wx_2026北京中考数学试卷真题答案来啦_官方版_快下载__imgs',
        'article': '2026-math_wx_2026北京中考数学试卷真题答案来啦_官方版_快下载_.html',
    },
    {
        'slug': 'zhentt',
        'title': '西城观察 · 逐题分屏版',
        'note': '把整卷切成小图逐题展示，33 张图更细，但分辨率低。适合手机端一题一图对照。',
        'dir': '2026-math_wx_2026年北京中考数学真题_及答案__imgs',
        'article': '2026-math_wx_2026年北京中考数学真题_及答案__imgs/../2026-math_wx_2026年北京中考数学真题_及答案_.html',
    },
]

# Marketing filler: skip img_000, img_001, img_last-2 etc. based on size threshold
# We include all images >4KB (real content) sorted by index. But we mark <15KB as "封面/尾图" so viewer can skim past.


def collect(src):
    d = MATH_DIR / src['dir']
    if not d.is_dir():
        return []
    items = []
    for f in sorted(d.iterdir()):
        if f.suffix.lower() not in ('.jpg', '.png', '.webp', '.gif'):
            continue
        size = f.stat().st_size
        if size < 4096:
            continue
        # relative from OUT (html/papers/2026-math-viewer.html)
        rel = os.path.relpath(f, OUT.parent)
        items.append({'src': rel, 'size': size, 'idx': int(re.search(r'(\d+)', f.stem).group(1))})
    items.sort(key=lambda x: x['idx'])
    return items


def render_source(src, imgs):
    if not imgs:
        return ''
    cards = []
    for i, im in enumerate(imgs):
        sz = im['size']
        badge = ''
        if sz < 20000:
            badge = '<span class="badge badge-hint">封面/尾图</span>'
        elif sz > 300000:
            badge = '<span class="badge badge-hd">高清</span>'
        cards.append(
            f'<figure class="pg"><img loading="lazy" src="{html.escape(im["src"])}" '
            f'alt="{html.escape(src["title"])} 第 {i+1} 张">'
            f'<figcaption>#{i+1:02d} · {sz//1024} KB {badge}</figcaption></figure>'
        )
    return f'''
<section class="src" id="src-{src['slug']}">
  <header>
    <h2>{html.escape(src['title'])}</h2>
    <p class="note">{html.escape(src['note'])}</p>
    <p class="stat">{len(imgs)} 张图 · 平均 {sum(x['size'] for x in imgs)//len(imgs)//1024} KB</p>
  </header>
  <div class="grid">{''.join(cards)}</div>
</section>'''


def main():
    sources_data = [(s, collect(s)) for s in SOURCES]
    total_imgs = sum(len(items) for _, items in sources_data)

    tabs = ''.join(
        f'<a href="#src-{s["slug"]}" class="tab">{html.escape(s["title"].split(" · ")[0])} <small>{len(imgs)}</small></a>'
        for s, imgs in sources_data
    )

    sections = '\n'.join(render_source(s, imgs) for s, imgs in sources_data)

    page = f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="2026 北京中考数学卷整卷图片版 · 4 份来源交叉校对">
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
  .tab:target,.tab:active{{border-bottom-color:var(--green);color:var(--ink)}}
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
  .pg figcaption{{padding:8px 10px;font-size:11px;color:var(--muted);
    display:flex;justify-content:space-between;align-items:center;gap:8px;
    border-top:1px solid var(--line);background:#fafaf7}}
  .badge{{font-size:10px;font-weight:800;padding:2px 6px;border-radius:2px}}
  .badge-hint{{background:#f4f2eb;color:#a09b8f}}
  .badge-hd{{background:var(--green-soft);color:var(--green)}}
  /* Lightbox */
  .lb{{position:fixed;inset:0;background:rgba(20,32,29,.92);z-index:100;display:none;
    align-items:center;justify-content:center;padding:24px;cursor:zoom-out}}
  .lb.open{{display:flex}}
  .lb img{{max-width:100%;max-height:100%;object-fit:contain;box-shadow:0 20px 60px rgba(0,0,0,.5)}}
  .lb .close{{position:absolute;top:20px;right:24px;color:#fff;font-size:28px;font-weight:700;cursor:pointer}}
  @media(max-width:700px){{
    .viewer-hero h1{{font-size:24px}}
    .tabs{{padding:0 16px;overflow-x:auto;white-space:nowrap;flex-wrap:nowrap;top:0}}
    .tab{{padding:10px 12px 12px;font-size:12px}}
    .src{{padding:28px 16px}}
    .grid{{grid-template-columns:1fr 1fr;gap:10px}}
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
    <a href="../../downloads.html">真题下载</a>
  </nav>
  <a class="icon-button" href="../../downloads.html#y2026" title="下载页">←</a>
</header>

<section class="viewer-hero">
  <p class="eyebrow">2026-06-24 · 北京市初中学业水平数学考试</p>
  <h1>2026 数学 · 整卷图片版</h1>
  <p>本仓库从微信公众号抓取到的 4 份图片版试卷，全部指向同一份 2026-06-24 北京中考数学卷（100 分 · 120 分钟）。
    每份来源各有偏重：Albert 版含官方标答和后三题解析，焦老师版分辨率最高，新东方版覆盖官方答案，西城观察版逐题切分。</p>
  <p class="warn">
    <strong>使用建议：</strong>先看 Albert 版拿到官方标答，再用焦老师版做原卷限时；
    <a href="../../downloads.html#y2026">下载页</a> 有全部原始 HTML 和高清图片文件夹。
    图片点击可放大查看。
  </p>
</section>

<nav class="tabs" aria-label="来源切换">{tabs}</nav>

<main class="viewer">
{sections}
</main>

<footer><span>京考进阶 · 4 份来源共 {total_imgs} 张图 · 数据仅本地保存</span><a href="../../downloads.html#y2026">下载原始文件 ↗</a></footer>

<div class="lb" id="lb"><span class="close">×</span><img alt="放大预览"></div>
<script>
const lb = document.getElementById('lb'), lbImg = lb.querySelector('img');
document.querySelectorAll('.pg img').forEach(im => {{
  im.onclick = () => {{ lbImg.src = im.src; lb.classList.add('open'); }};
}});
lb.onclick = () => lb.classList.remove('open');
document.addEventListener('keydown', e => {{ if (e.key === 'Escape') lb.classList.remove('open'); }});
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
