#!/usr/bin/env python3
"""Generate downloads.html: full year × subject gallery of papers/downloaded/."""
import os, html
from pathlib import Path

REPO = Path(__file__).resolve().parent
DL = REPO / "papers" / "downloaded"

SUBJ_ZH = {
    'math': '数学', 'physics': '物理', 'chemistry': '化学', 'biology': '生物',
    'chinese': '语文', 'english': '英语', 'history': '历史',
    'geography': '地理', 'politics': '政治', 'overview': '合辑',
}
SUBJ_ORDER = ['math', 'physics', 'chemistry', 'biology', 'chinese',
              'english', 'history', 'geography', 'politics', 'overview']

EXT_META = {
    'pdf':  ('PDF',   '#d4523f', '原版试卷'),
    'html': ('HTML',  '#39759b', '网页快照'),
    'md':   ('MD',    '#176b4d', 'Markdown 题面'),
    'txt':  ('TXT',   '#61706b', '评析文本'),
}


def scan():
    """Walk papers/downloaded/, but skip image assets inside *_imgs/ dirs and non-document files."""
    ALLOWED_EXT = {'pdf', 'html', 'md', 'txt'}
    data = {}
    for dp, _, fn in os.walk(DL):
        # skip _imgs subdirectories (article images, not deliverables)
        if '_imgs' in Path(dp).parts[-1] or '_imgs/' in dp or dp.endswith('_imgs'):
            continue
        for f in fn:
            if f == 'README.md':
                continue
            ext = f.rsplit('.', 1)[-1].lower()
            if ext not in ALLOWED_EXT:
                continue
            full = Path(dp) / f
            rel = full.relative_to(REPO)
            parts = rel.parts  # papers, downloaded, year, subject?, file
            if len(parts) < 4 or not parts[2].isdigit():
                continue
            year = parts[2]
            subject = parts[3] if len(parts) == 5 else 'overview'
            size = full.stat().st_size
            # count sibling *_imgs image dir to display image bundle size
            imgs_dir = full.parent / (full.stem + '_imgs')
            img_count = 0
            img_bytes = 0
            if imgs_dir.is_dir():
                for ip in imgs_dir.iterdir():
                    if ip.is_file() and ip.suffix.lower() in ('.jpg', '.jpeg', '.png', '.gif', '.webp'):
                        img_count += 1
                        img_bytes += ip.stat().st_size
            data.setdefault(year, {}).setdefault(subject, []).append({
                'name': f, 'href': str(rel), 'size': size, 'ext': ext,
                'imgs': img_count, 'imgs_bytes': img_bytes,
            })
    for y in data:
        for s in data[y]:
            data[y][s].sort(key=lambda x: x['name'])
    return data


def fmt_size(n):
    for u in ['B', 'KB', 'MB']:
        if n < 1024:
            return f"{n:.1f} {u}" if u != 'B' else f"{n} B"
        n /= 1024
    return f"{n:.1f} GB"


def render_card(f):
    ext = f['ext']
    label, color, kind = EXT_META.get(ext, ('文件', '#61706b', ''))
    # if HTML article ships with an image bundle, show it as an extra badge
    extra = ''
    if f.get('imgs'):
        extra = f' · 附 {f["imgs"]} 图 · {fmt_size(f["imgs_bytes"])}'
    # MD files have a rendered HTML version (build_html.py) with site nav — prefer it
    href = f['href']
    if ext == 'md':
        rendered = 'html/' + href[:-3] + '.html'
        if (REPO / rendered).is_file():
            href = rendered
    return f'''
      <a class="dl-file" href="{html.escape(href)}" target="_blank" rel="noopener">
        <span class="dl-badge" style="background:{color}">{label}</span>
        <span class="dl-name">{html.escape(f['name'])}</span>
        <span class="dl-meta">{kind} · {fmt_size(f['size'])}{extra}</span>
      </a>'''


def render_year(year, subjects):
    subj_html = []
    for s in SUBJ_ORDER:
        if s not in subjects:
            continue
        files = subjects[s]
        cards = ''.join(render_card(f) for f in files)
        # coverage badge: pdf > md > html > txt
        exts = {f['ext'] for f in files}
        if 'pdf' in exts:
            badge = '<span class="cov cov-pdf">原版 PDF</span>'
        elif 'md' in exts:
            badge = '<span class="cov cov-md">完整 MD</span>'
        elif 'html' in exts:
            badge = '<span class="cov cov-html">网页快照</span>'
        else:
            badge = '<span class="cov cov-txt">仅评析</span>'
        subj_html.append(f'''
    <section class="dl-subject">
      <header>
        <h3>{SUBJ_ZH.get(s, s)}</h3>
        {badge}
        <span class="dl-count">{len(files)} 个文件</span>
      </header>
      <div class="dl-files">{cards}
      </div>
    </section>''')
    all_ext_sum = sum(len(v) for v in subjects.values())
    viewer_hint = ''
    if year == '2026':
        viewer_hint = '''
  <div class="dl-viewer-hint">
    <strong>📐 做题首选：</strong>2026 数学整卷图片版查看器（4 份来源交叉校对 · 含官方标答 · 80 张试题图逐张浏览）
    <a class="dl-viewer-link" href="html/papers/2026-math-viewer.html" target="_blank" rel="noopener">打开 2026 数学整卷查看器 →</a>
  </div>'''
    return f'''
<section class="dl-year" id="y{year}">
  <div class="dl-year-head">
    <h2>{year} 年</h2>
    <span class="dl-year-count">{len(subjects)} 个学科 · {all_ext_sum} 个文件</span>
  </div>{viewer_hint}
  <div class="dl-subjects">
    {''.join(subj_html)}
  </div>
</section>'''


def main():
    data = scan()
    years = sorted(data.keys(), reverse=True)

    total_files = sum(len(f) for y in data.values() for f in y.values())
    total_pdf = sum(1 for y in data.values() for fs in y.values() for f in fs if f['ext'] == 'pdf')
    total_html = sum(1 for y in data.values() for fs in y.values() for f in fs if f['ext'] == 'html')
    total_md = sum(1 for y in data.values() for fs in y.values() for f in fs if f['ext'] == 'md')
    total_txt = sum(1 for y in data.values() for fs in y.values() for f in fs if f['ext'] == 'txt')

    year_nav = ' · '.join(f'<a href="#y{y}">{y}</a>' for y in years)
    year_blocks = '\n'.join(render_year(y, data[y]) for y in years)

    # coverage matrix
    all_subs = ['math','physics','chemistry','biology','chinese','english','history','geography','politics']
    rows = []
    for y in years:
        cells = [f'<th>{y}</th>']
        for s in all_subs:
            fs = data[y].get(s, [])
            if not fs:
                cells.append('<td class="miss">—</td>')
            else:
                exts = {f['ext'] for f in fs}
                if 'pdf' in exts:
                    cells.append(f'<td class="ok"><a href="#y{y}">PDF</a></td>')
                elif 'md' in exts:
                    cells.append(f'<td class="mid"><a href="#y{y}">MD</a></td>')
                elif 'html' in exts:
                    cells.append(f'<td class="mid"><a href="#y{y}">HTML</a></td>')
                else:
                    cells.append(f'<td class="weak"><a href="#y{y}">TXT</a></td>')
        rows.append('<tr>' + ''.join(cells) + '</tr>')

    matrix = f'''<table class="cov-matrix">
<thead><tr><th></th>{''.join(f'<th>{SUBJ_ZH[s]}</th>' for s in all_subs)}</tr></thead>
<tbody>{''.join(rows)}</tbody></table>'''

    page = f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="北京中考 2017-2026 真题下载合集：{total_pdf}份 PDF + {total_html}份 HTML + {total_md}份 MD + {total_txt}份 TXT">
<title>真题下载合集 · 京考进阶</title>
<link rel="stylesheet" href="styles.css">
<style>
  .dl-hero{{padding:60px clamp(24px,8vw,120px) 30px;background:var(--paper)}}
  .dl-hero h1{{font-family:"Noto Serif SC","Songti SC",serif;font-size:clamp(34px,4vw,52px);margin:0 0 12px}}
  .dl-hero p{{color:var(--muted);max-width:780px;line-height:1.75;margin:0}}
  .dl-stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;margin-top:36px}}
  .dl-stat{{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:22px}}
  .dl-stat b{{font-family:Georgia,serif;font-size:36px;color:var(--green);display:block;line-height:1}}
  .dl-stat span{{font-size:12px;color:var(--muted);display:block;margin-top:6px;font-weight:700;letter-spacing:.06em}}
  .dl-hero .year-nav{{margin-top:24px;font-size:13px;font-weight:700}}
  .dl-hero .year-nav a{{color:var(--green);margin-right:14px;border-bottom:1px solid transparent}}
  .dl-hero .year-nav a:hover{{border-bottom-color:var(--green)}}
  main.dl-main{{padding:20px clamp(24px,8vw,120px) 80px;background:var(--white)}}
  .cov-matrix{{width:100%;border-collapse:collapse;margin:20px 0 40px;font-size:13px;background:#fff;display:block;overflow-x:auto;-webkit-overflow-scrolling:touch;white-space:nowrap}}
  .cov-matrix th,.cov-matrix td{{padding:9px 8px;border:1px solid var(--line);text-align:center}}
  .cov-matrix thead th{{background:var(--ink);color:#fff;font-weight:700}}
  .cov-matrix tbody th{{background:var(--paper);font-family:Georgia,serif;font-size:15px}}
  .cov-matrix td a{{color:inherit;font-weight:700}}
  .cov-matrix td.ok{{background:#dcebe2;color:#0e4b34}}
  .cov-matrix td.mid{{background:#fff8c5;color:#5a4600}}
  .cov-matrix td.weak{{background:#fbe4d5;color:#7a2f19}}
  .cov-matrix td.miss{{background:#f4f2eb;color:#a09b8f}}
  .dl-year{{margin:50px 0 0;padding-top:30px;border-top:1px solid var(--line)}}
  .dl-year:first-of-type{{border-top:0}}
  .dl-viewer-hint{{background:linear-gradient(90deg,#f4fbf6,#f0f7fb);border:1px solid var(--green-soft,#cfe6db);border-left:4px solid var(--green,#176b4d);border-radius:var(--radius);padding:14px 20px;margin-bottom:18px;font-size:14.5px;line-height:1.7}}
  .dl-viewer-hint strong{{color:var(--green,#176b4d)}}
  .dl-viewer-link{{display:inline-block;margin-left:10px;background:var(--green,#176b4d);color:#fff !important;padding:6px 14px;border-radius:6px;font-size:13px;font-weight:600;text-decoration:none !important}}
  .dl-viewer-link:hover{{opacity:.9}}
  .dl-year-head{{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:22px;gap:20px;flex-wrap:wrap}}
  .dl-year-head h2{{font-family:Georgia,serif;font-size:56px;margin:0;color:var(--green);line-height:1}}
  .dl-year-count{{color:var(--muted);font-size:13px;font-weight:700}}
  .dl-subjects{{display:grid;gap:14px}}
  .dl-subject{{border:1px solid var(--line);border-radius:var(--radius);padding:18px 22px;background:#fff}}
  .dl-subject header{{display:flex;align-items:baseline;gap:16px;flex-wrap:wrap;margin-bottom:14px}}
  .dl-subject h3{{margin:0;font-size:18px}}
  .cov{{font-size:11px;font-weight:700;padding:3px 8px;border-radius:3px;letter-spacing:.04em}}
  .cov-pdf{{background:#dcebe2;color:#0e4b34}}
  .cov-md{{background:#e8dfff;color:#4c2f7a}}
  .cov-html{{background:#fff8c5;color:#5a4600}}
  .cov-txt{{background:#fbe4d5;color:#7a2f19}}
  .dl-count{{margin-left:auto;color:var(--muted);font-size:12px}}
  .dl-files{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px}}
  .dl-file{{display:grid;grid-template-columns:44px 1fr;grid-template-rows:auto auto;column-gap:12px;padding:10px 14px;border:1px solid var(--line);border-radius:4px;background:var(--paper);transition:border-color .15s,background .15s}}
  .dl-file:hover{{border-color:var(--green);background:#fff}}
  .dl-badge{{grid-row:1/3;grid-column:1;align-self:center;justify-self:center;width:40px;height:40px;display:grid;place-items:center;border-radius:4px;color:#fff;font-size:11px;font-weight:800;letter-spacing:.02em}}
  .dl-name{{grid-column:2;grid-row:1;font-size:13px;font-weight:700;word-break:break-all;color:var(--ink);line-height:1.35}}
  .dl-meta{{grid-column:2;grid-row:2;font-size:11px;color:var(--muted);margin-top:3px}}
  @media(max-width:700px){{.dl-stats{{grid-template-columns:1fr 1fr}}.dl-year-head h2{{font-size:42px}}.cov-matrix{{font-size:11px}}.cov-matrix th,.cov-matrix td{{padding:6px 4px}}}}
</style>
</head>
<body>
<header class="topbar">
  <a class="brand" href="index.html" aria-label="返回首页">
    <span class="brand-mark">京</span><span>京考进阶</span>
  </a>
  <nav aria-label="主导航">
    <a href="index.html#today">今日</a>
    <a href="index.html#plan">计划</a>
    <a href="index.html#materials">资料</a>
    <a href="index.html#mistakes">错题</a>
    <a href="downloads.html" aria-current="page">真题下载</a>
  </nav>
  <a class="icon-button" href="index.html" title="返回">←</a>
</header>

<section class="dl-hero">
  <p class="eyebrow">EXAM PAPERS · 2017 → 2026</p>
  <h1>北京中考真题下载合集</h1>
  <p>历经多轮长任务从 <code>zhongkaobj.cn</code>（阿里云 OSS 直链）、GitHub 教辅仓库、zizzs.com / gaokzx.com 等来源整理的原版试题，覆盖 9 个学科 · 10 个年份。点击卡片在新标签打开 PDF 预览或网页快照（可在浏览器中另存下载）。</p>
  <div class="dl-stats">
    <div class="dl-stat"><b>{total_pdf}</b><span>PDF 原版试卷</span></div>
    <div class="dl-stat"><b>{total_html}</b><span>HTML 网页快照</span></div>
    <div class="dl-stat"><b>{total_md}</b><span>Markdown 完整题面</span></div>
    <div class="dl-stat"><b>{total_txt}</b><span>TXT 评析文本</span></div>
  </div>
  <div class="year-nav">跳转年份：{year_nav}</div>
</section>

<main class="dl-main">
  <h2 style="margin:0 0 8px;font-family:'Noto Serif SC',serif;font-size:22px">覆盖矩阵</h2>
  <p style="color:var(--muted);font-size:13px;margin:0 0 6px">
    颜色说明：<span class="cov cov-pdf">绿 = 原版 PDF</span> ·
    <span class="cov cov-md">紫 = 完整 MD</span> ·
    <span class="cov cov-html">黄 = HTML 快照</span> ·
    <span class="cov cov-txt">橙 = 仅评析</span> ·
    灰色破折号 = 未收录
  </p>
  {matrix}
  {year_blocks}
</main>

<footer>
  <span>京考进阶 · 真题合集，来源详见 <a href="html/papers/downloaded/README.html">下载 README</a></span>
  <a href="index.html">← 返回首页</a>
</footer>
</body>
</html>
'''
    out = REPO / 'downloads.html'
    out.write_text(page, encoding='utf-8')
    print(f'✓ Wrote {out} — {total_files} files, {total_pdf} PDF + {total_html} HTML + {total_md} MD + {total_txt} TXT')


if __name__ == '__main__':
    main()
