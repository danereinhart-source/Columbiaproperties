#!/usr/bin/env python3
"""
publish.py — publishes the NEXT queued blog post.

It picks the lexicographically-first file in _blog_engine/queue/, renders it
to /blog/<slug>.html, dates it today (America/Phoenix), prepends it to
published.json, regenerates the blog index + sitemap, and archives the queue
file to _blog_engine/published_src/.

Run by the weekly GitHub Action, but also runnable locally:
    python3 _blog_engine/publish.py            # publish next
    python3 _blog_engine/publish.py --dry-run  # show what would publish
"""
import os
import sys
import glob
import shutil
from datetime import datetime, timezone, timedelta

import build  # local module

HERE = os.path.dirname(os.path.abspath(__file__))
QUEUE_DIR = os.path.join(HERE, "queue")
ARCHIVE_DIR = os.path.join(HERE, "published_src")

# America/Phoenix is UTC-7 year-round (no DST).
PHOENIX = timezone(timedelta(hours=-7))


def parse_queue_file(path):
    """Parse a queue file: simple `key: value` front matter, then '---', then HTML body."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if not text.startswith("---"):
        raise ValueError(f"{path}: must start with a '---' front-matter block")
    _, fm, body = text.split("---", 2)
    meta = {}
    for line in fm.strip().splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, val = line.split(":", 1)
        val = val.strip()
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
        meta[key.strip()] = val
    required = ["slug", "title", "meta_title", "meta_description",
                "breadcrumb", "image", "excerpt"]
    missing = [k for k in required if k not in meta]
    if missing:
        raise ValueError(f"{path}: missing front-matter keys: {missing}")
    meta.setdefault("read_time", "6 min read")
    meta.setdefault("alt", meta["breadcrumb"])
    return meta, body


def next_queue_file():
    files = sorted(glob.glob(os.path.join(QUEUE_DIR, "*.html")))
    return files[0] if files else None


def main():
    dry = "--dry-run" in sys.argv
    nxt = next_queue_file()
    if not nxt:
        print("::notice::Blog queue is EMPTY. Nothing to publish. Ask Claude to refill the queue.")
        return 0

    meta, body = parse_queue_file(nxt)
    today = datetime.now(PHOENIX)
    meta["date_iso"] = today.strftime("%Y-%m-%d")
    meta["date_display"] = today.strftime("%B %-d, %Y")

    remaining = len(glob.glob(os.path.join(QUEUE_DIR, "*.html"))) - 1

    if dry:
        print(f"[DRY RUN] Would publish: {os.path.basename(nxt)}")
        print(f"           slug:  {meta['slug']}")
        print(f"           title: {meta['title']}")
        print(f"           date:  {meta['date_display']}")
        print(f"           queue remaining after: {remaining}")
        return 0

    # Render the post page.
    out = build.render_post(meta, body)

    # Prepend to published.json (newest first).
    posts = build.load_published()
    posts = [p for p in posts if p["slug"] != meta["slug"]]  # avoid dupes
    posts.insert(0, {
        "slug": meta["slug"],
        "title": meta["title"],
        "excerpt": meta["excerpt"],
        "image": meta["image"],
        "alt": meta["alt"],
        "date_iso": meta["date_iso"],
        "date_display": meta["date_display"],
    })
    build.save_published(posts)

    # Regenerate index + sitemap.
    build.rebuild_index(posts)
    build.rebuild_sitemap(posts)

    # Archive the source so it is not published again.
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    shutil.move(nxt, os.path.join(ARCHIVE_DIR, os.path.basename(nxt)))

    print(f"Published: {meta['slug']} -> {os.path.relpath(out, build.ROOT)}")
    print(f"Queue remaining: {remaining}")
    if remaining <= 2:
        print(f"::warning::Blog queue is running low ({remaining} left). Ask Claude to refill it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
