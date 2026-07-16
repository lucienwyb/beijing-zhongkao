#!/usr/bin/env python3
"""Shared helpers for the three build scripts (build_html / build_downloads / build_2026_math_viewer).

Extracted to eliminate copy-pasted favicon chains, OG meta tags, and magic
thresholds. Import from build scripts instead of duplicating HTML fragments.
"""
from pathlib import Path
import html as _html

REPO_ROOT = Path(__file__).resolve().parent

# ── Image content filter ──────────────────────────────────────────────
# Images below this size are marketing filler / spacers, not real exam
# content. Used by both build_downloads.count_2026_images() and
# build_2026_math_viewer.collect() so the figure counts they report always
# match what the viewer actually displays.
IMAGE_MIN_BYTES = 4096

# ── Badge size thresholds for the 2026 viewer ─────────────────────────
# Images <20 KB are typically cover/end pages (low information density).
# Images >300 KB are high-resolution scans worth highlighting.
VIEWER_BADGE_SMALL = 20_000
VIEWER_BADGE_HD = 300_000


def favicon_links(prefix: str) -> str:
    """Return the 3-link favicon fallback chain (ico → png → svg).

    Args:
        prefix: relative path to repo root, e.g. '../../' or '' for root-level pages.
    """
    return (
        f'<link rel="icon" href="{prefix}favicon.ico" sizes="any">'
        f'<link rel="icon" href="{prefix}favicon-32.png" type="image/png" sizes="32x32">'
        f'<link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml">'
    )


def og_tags(title: str, description: str, og_type: str = 'article') -> str:
    """Return Open Graph + Twitter + theme-color meta tags.

    Args:
        title: og:title content (should include site suffix, e.g. "X · 京考进阶").
        description: og:description content.
        og_type: 'article' for paper pages, 'website' for index/gallery pages.
    """
    return (
        f'<meta property="og:title" content="{_html.escape(title, quote=True)}">\n'
        f'<meta property="og:description" content="{_html.escape(description, quote=True)}">\n'
        f'<meta property="og:type" content="{og_type}">\n'
        f'<meta name="twitter:card" content="summary">\n'
        f'<meta name="theme-color" content="#14201d">'
    )
