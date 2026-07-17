#!/usr/bin/env python3
"""DOM structure validator for all HTML files in the repo."""
import sys
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Comment
import re

ROOT = Path("/pulp/beijing-zhongkao")

# Obsolete/deprecated HTML5 tags
OBSOLETE_TAGS = {
    'font', 'center', 'marquee', 'blink', 'strike', 'u', 'basefont',
    'big', 'tt', 'acronym', 'applet', 'dir', 'frame', 'frameset',
    'noframes', 'isindex', 'listing', 'plaintext', 'xmp', 'spacer',
}

# Valid parents for block-level inside inline — illegal nesting
# <p> cannot contain block-level elements
BLOCK_TAGS = {'div', 'section', 'article', 'aside', 'header', 'footer',
             'nav', 'main', 'figure', 'figcaption', 'fieldset', 'blockquote',
             'pre', 'table', 'ul', 'ol', 'dl', 'h1', 'h2', 'h3', 'h4', 'h5',
             'h6', 'hr', 'form', 'address', 'details', 'dialog', 'p',
             'menu', 'hr', 'figure'}

# <a> cannot contain interactive content
INTERACTIVE_TAGS = {'button', 'a', 'input', 'select', 'textarea',
                   'label', 'details', 'embed', 'iframe', 'object'}

def find_all_html():
    return sorted(ROOT.rglob("*.html"))

def check_file(path):
    raw = path.read_text(encoding='utf-8', errors='replace')
    issues = []
    rel = path.relative_to(ROOT)

    # Use lxml for parsing; it auto-closes tags and reports via recovery
    # First parse with html.parser to detect structure
    try:
        soup = BeautifulSoup(raw, 'lxml')
    except Exception:
        soup = BeautifulSoup(raw, 'html.parser')

    # --- Check 1: unclosed tags ---
    # Compare tag balance using a manual scan
    VOID = {'area','base','br','col','embed','hr','img','input','link',
            'meta','param','source','track','wbr'}
    # Use html.parser to track open tags
    import html.parser
    class TagChecker(html.parser.HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.stack = []
            self.unclosed = []
            self.mismatched = []
        def handle_starttag(self, tag, attrs):
            if tag in VOID:
                return
            self.stack.append((tag, self.getpos()))
        def handle_endtag(self, tag):
            if tag in VOID:
                return
            # find matching
            for i in range(len(self.stack)-1, -1, -1):
                if self.stack[i][0] == tag:
                    # anything above is unclosed
                    for t, pos in reversed(self.stack[i+1:]):
                        self.unclosed.append((t, pos))
                    del self.stack[i:]
                    return
            # no match — stray end tag
            self.mismatched.append((tag, self.getpos()))
    try:
        tc = TagChecker()
        tc.feed(raw)
        for t, pos in tc.unclosed:
            issues.append(f"UNCLOSED: <{t}> opened at line {pos[0]} never closed")
        for t, pos in tc.mismatched:
            issues.append(f"STRAY_END: </{t}> at line {pos[0]} has no opening")
        if tc.stack:
            for t, pos in tc.stack:
                issues.append(f"UNCLOSED: <{t}> opened at line {pos[0]} never closed (eof)")
    except Exception as e:
        issues.append(f"PARSE_ERROR: {e}")

    # --- Check 2: illegal nesting ---
    # <p> containing block-level
    for p in soup.find_all('p'):
        for child in p.find_all(True):
            if child.name in {'div', 'section', 'article', 'ul', 'ol',
                              'table', 'form', 'blockquote', 'pre',
                              'h1','h2','h3','h4','h5','h6', 'hr',
                              'header','footer','nav','main','aside',
                              'figure','fieldset'}:
                issues.append(f"NESTING: <p> contains <{child.name}> (block in p)")

    # <a> containing interactive content
    for a in soup.find_all('a'):
        for child in a.find_all(True):
            if child.name in INTERACTIVE_TAGS:
                issues.append(f"NESTING: <a> contains <{child.name}> (interactive in a)")

    # --- Check 3: duplicate ids ---
    ids = {}
    for el in soup.find_all(attrs={'id': True}):
        eid = el['id']
        ids.setdefault(eid, []).append(el.sourceline if el.sourceline else '?')
    for eid, lines in ids.items():
        if len(lines) > 1:
            issues.append(f"DUPLICATE_ID: id='{eid}' appears {len(lines)} times at lines {lines}")

    # --- Check 4: img without alt ---
    for img in soup.find_all('img'):
        if 'alt' not in img.attrs:
            issues.append(f"IMG_NO_ALT: <img src='{img.get('src','?')}'> at line {img.sourceline}")
        elif not img['alt'].strip() and not img.get('role'):
            # empty alt is OK for decorative images, but flag src
            pass

    # --- Check 5: form/label association ---
    for form in soup.find_all('form'):
        # each input should have an associated label (for/id) or aria-label
        for inp in form.find_all(['input', 'select', 'textarea']):
            if inp.get('type') in ('hidden', 'submit', 'button', 'reset'):
                continue
            # check aria-label
            if inp.get('aria-label') or inp.get('aria-labelledby'):
                continue
            # check wrapped in label
            parent = inp.parent
            if parent and parent.name == 'label':
                continue
            # check label[for]
            inp_id = inp.get('id')
            if inp_id:
                label = soup.find('label', attrs={'for': inp_id})
                if label:
                    continue
            issues.append(f"FORM_NO_LABEL: <{inp.name}> at line {inp.sourceline} has no associated <label>")

    # --- Check 6: table structure ---
    for table in soup.find_all('table'):
        # direct children should be thead/tbody/tfoot/tr/caption/colgroup
        for child in table.children:
            if isinstance(child, NavigableString):
                if isinstance(child, Comment):
                    continue
                if str(child).strip():
                    pass  # text directly in table — non-standard but minor
                continue
            if child.name not in {'thead','tbody','tfoot','tr','caption',
                                  'colgroup','col'}:
                issues.append(f"TABLE_BAD_CHILD: <table> directly contains <{child.name}> at line {child.sourceline}")
        # tr should contain th/td
        for tr in table.find_all('tr'):
            for child in tr.children:
                if isinstance(child, Comment):
                    continue
                if isinstance(child, NavigableString):
                    if str(child).strip():
                        issues.append(f"TABLE_TEXT_IN_TR: bare text in <tr> at line {tr.sourceline}")
                    continue
                if child.name not in {'th','td'}:
                    issues.append(f"TABLE_BAD_TR_CHILD: <tr> contains <{child.name}> at line {child.sourceline}")

    # --- Check 7: obsolete tags ---
    for tag in OBSOLETE_TAGS:
        for el in soup.find_all(tag):
            issues.append(f"OBSOLETE_TAG: <{tag}> at line {el.sourceline}")

    # --- Check 8: head order ---
    head = soup.find('head')
    if head:
        head_children = [c for c in head.children if not isinstance(c, NavigableString) or str(c).strip()]
        # Expect: meta charset, meta viewport, title, ...
        order = [c.name for c in head_children if hasattr(c,'name') and c.name]
        # find positions
        def pos(name):
            for i,n in enumerate(order):
                if n == name:
                    return i
            return -1
        ti = pos('title')
        mc = -1
        for i,c in enumerate(head_children):
            if hasattr(c,'name') and c.name=='meta' and c.get('charset'):
                mc = i
                break
        mv = -1
        for i,c in enumerate(head_children):
            if hasattr(c,'name') and c.name=='meta' and 'viewport' in (c.get('name','') or ''):
                mv = i
                break
        # charset should be first, title before links/scripts
        if mc > 0 and mc != 0:
            # allow doctype only; charset should be very first in head
            pass  # we'll just report order
        if ti >= 0:
            # title should come before link/script ideally
            for i,c in enumerate(head_children):
                if hasattr(c,'name') and c.name in ('link','script') and i < ti:
                    # link before title — flag only if it's a stylesheet/script
                    rel_attr = c.get('rel','')
                    if isinstance(rel_attr, list):
                        rel_attr = ' '.join(rel_attr)
                    if 'stylesheet' in rel_attr or c.name == 'script':
                        issues.append(f"HEAD_ORDER: <{c.name}> (stylesheet/script) appears before <title> at line {c.sourceline}")
                        break

    # --- Check 9: empty href/src ---
    for el in soup.find_all('a'):
        if 'href' in el.attrs:
            if not el['href'].strip():
                issues.append(f"EMPTY_HREF: <a> with empty href at line {el.sourceline}")
    for el in soup.find_all(['img','script','link','source']):
        attr = 'src' if el.name in ('img','script','source') else 'href'
        if attr in el.attrs and not el[attr].strip():
            issues.append(f"EMPTY_{attr.upper()}: <{el.name}> with empty {attr} at line {el.sourceline}")

    # --- Check 10: html lang ---
    html_tag = soup.find('html')
    if html_tag:
        lang = html_tag.get('lang', '')
        if lang != 'zh-CN':
            issues.append(f"HTML_LANG: <html lang='{lang}'> (expected zh-CN)")
    else:
        issues.append("NO_HTML_TAG: no <html> root")

    return rel, issues

def main():
    files = find_all_html()
    total_issues = 0
    for f in files:
        rel, issues = check_file(f)
        if issues:
            total_issues += len(issues)
            print(f"\n=== {rel} ({len(issues)} issues) ===")
            for iss in issues:
                print(f"  {iss}")
        else:
            print(f"OK  {rel}")
    print(f"\n{'='*60}")
    print(f"Total: {len(files)} files, {total_issues} issues")
    return 1 if total_issues else 0

if __name__ == '__main__':
    sys.exit(main())
