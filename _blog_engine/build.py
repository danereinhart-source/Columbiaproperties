#!/usr/bin/env python3
"""
build.py — regenerates the blog index grid (blog.html) and sitemap.xml
from _blog_engine/published.json. Safe to run any time; it is idempotent.

Usage:
    python3 _blog_engine/build.py
"""
import json
import os
import html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOMAIN = "https://columbia-properties.com"

PUBLISHED_JSON = os.path.join(HERE, "published.json")
BLOG_INDEX = os.path.join(ROOT, "blog.html")
SITEMAP = os.path.join(ROOT, "sitemap.xml")
TEMPLATE = os.path.join(HERE, "template_post.html")

CARDS_START = "<!-- BLOG_CARDS_START -->"
CARDS_END = "<!-- BLOG_CARDS_END -->"

# Static pages to include in the sitemap (relative paths, served at root).
STATIC_PAGES = [
    ("", "1.0"),
    ("index.html", "1.0"),
    ("management.html", "0.9"),
    ("home-watching.html", "0.8"),
    ("pricing.html", "0.9"),
    ("free-rental-analysis.html", "0.9"),
    ("switch.html", "0.8"),
    ("faq.html", "0.7"),
    ("about.html", "0.7"),
    ("blog.html", "0.8"),
    ("northern-arizona.html", "0.8"),
    ("tucson.html", "0.8"),
    ("privacy.html", "0.3"),
]


def load_published():
    with open(PUBLISHED_JSON, encoding="utf-8") as f:
        return json.load(f)


def save_published(posts):
    with open(PUBLISHED_JSON, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
        f.write("\n")


def card_html(p):
    title = html.escape(p["title"])
    excerpt = html.escape(p["excerpt"])
    alt = html.escape(p.get("alt", ""))
    return f"""        <article class="blog-card">
            <img src="{p['image']}" alt="{alt}">
            <div class="blog-card-content">
                <p class="date">{p['date_display']}</p>
                <h3><a href="blog/{p['slug']}.html">{title}</a></h3>
                <p>{excerpt}</p>
                <a href="blog/{p['slug']}.html" class="read-more">Read More <i class="fas fa-arrow-right" style="font-size: 0.75rem;"></i></a>
            </div>
        </article>"""


def rebuild_index(posts):
    with open(BLOG_INDEX, encoding="utf-8") as f:
        contents = f.read()
    if CARDS_START not in contents or CARDS_END not in contents:
        raise SystemExit("ERROR: card markers not found in blog.html")
    pre, rest = contents.split(CARDS_START, 1)
    _, post = rest.split(CARDS_END, 1)
    cards = "\n\n".join(card_html(p) for p in posts)
    new = f"{pre}{CARDS_START}\n{cards}\n        {CARDS_END}{post}"
    with open(BLOG_INDEX, "w", encoding="utf-8") as f:
        f.write(new)


def rebuild_sitemap(posts):
    urls = []
    for path, prio in STATIC_PAGES:
        loc = f"{DOMAIN}/{path}" if path else f"{DOMAIN}/"
        urls.append((loc, None, prio))
    for p in posts:
        loc = f"{DOMAIN}/blog/{p['slug']}.html"
        urls.append((loc, p.get("date_iso"), "0.6"))

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, lastmod, prio in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{html.escape(loc)}</loc>")
        if lastmod:
            lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append(f"    <priority>{prio}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    with open(SITEMAP, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def render_post(meta, body):
    with open(TEMPLATE, encoding="utf-8") as f:
        tpl = f.read()
    replacements = {
        "{{META_TITLE}}": html.escape(meta["meta_title"]),
        "{{META_DESCRIPTION}}": html.escape(meta["meta_description"]),
        "{{SLUG}}": meta["slug"],
        "{{BREADCRUMB}}": html.escape(meta["breadcrumb"]),
        "{{TITLE}}": html.escape(meta["title"]),
        "{{DATE_DISPLAY}}": meta["date_display"],
        "{{READ_TIME}}": html.escape(meta.get("read_time", "5 min read")),
        "{{BODY}}": body.strip("\n"),
    }
    for k, v in replacements.items():
        tpl = tpl.replace(k, v)
    out = os.path.join(ROOT, "blog", f"{meta['slug']}.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(tpl)
    return out


def main():
    posts = load_published()
    rebuild_index(posts)
    rebuild_sitemap(posts)
    print(f"Rebuilt blog.html and sitemap.xml from {len(posts)} published posts.")


if __name__ == "__main__":
    main()
