# Automated Blog Publishing

This folder runs the automated weekly blog system for columbia-properties.com. It publishes one pre-written, human-approved post per week with zero manual effort.

## How it works

1. **Queue** — Finished, ready-to-publish posts live in `_blog_engine/queue/` as `.html` files with a small front-matter block at the top. They publish in filename order (`01-...`, `02-...`, etc.).
2. **Weekly Action** — `.github/workflows/publish-blog.yml` runs every **Monday at 9:00 AM Phoenix time**. It runs `publish.py`, which takes the next queued post, dates it that day, renders it to `/blog/<slug>.html`, updates the blog index and `sitemap.xml`, and commits the change. GitHub Pages then redeploys automatically.
3. **Archive** — Published source files move to `_blog_engine/published_src/` so they are never published twice.
4. **Low-queue reminder** — When 2 or fewer posts remain, the Action opens a GitHub issue titled "Blog queue running low" so you know to refill.

## Refilling the queue

When the queue gets low, open Cowork and say: **"Refill the blog queue with N new posts."** New `.html` files get added to `queue/` and will publish automatically on the schedule. Each new post is written and reviewed before it ever enters the queue, which keeps quality high and avoids Google's "scaled content abuse" penalties for mass-produced AI content.

## Changing the cadence

Edit the `cron` line in `.github/workflows/publish-blog.yml`:
- Weekly (current): `0 16 * * 1`
- Every 2 weeks: `0 16 1,15 * *` (approx. — runs on the 1st and 15th)
- Twice a week: `0 16 * * 1,4`

Weekly is the recommended cadence for a local business.

## Manual controls

- **Publish now:** GitHub → Actions → "Publish weekly blog post" → Run workflow.
- **Preview the next post without publishing:** `python3 _blog_engine/publish.py --dry-run`
- **Rebuild the index/sitemap by hand:** `python3 _blog_engine/build.py`

## Files

| File | Purpose |
|------|---------|
| `queue/` | Ready-to-publish posts, in publish order |
| `published_src/` | Archived source of already-published posts |
| `published.json` | Manifest of all live posts (drives the blog index grid + sitemap) |
| `template_post.html` | The post page template (matches the site's blog styling) |
| `build.py` | Renders a post; regenerates `blog.html` grid and `sitemap.xml` |
| `publish.py` | Publishes the next queued post (run by the Action) |

> Note: `blog.html` has `<!-- BLOG_CARDS_START -->` / `<!-- BLOG_CARDS_END -->` markers. Everything between them is generated — edit posts via the manifest/queue, not by hand inside the markers.
