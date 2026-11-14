# rayrooter.com

Static site for Ray Rooter Trenchless, hosted on Render.

- Edit copy in `src/content.py`, styles in `src/style.css`, templates in `src/build.py`.
- Build: `python3 src/build.py` (writes `public/`). Render runs this on every push.
- `render.yaml` holds the 301 redirects from old WordPress URLs.

## Before pointing the domain at Render
1. Copy images into `public/assets/img/` (they're still loaded from the old Bluehost site; see `IMG` in `src/content.py`).
2. Confirm where email for rayrooter.com is hosted, and keep its MX records.
3. Add the redirect routes from `render.yaml`.
4. Add rayrooter.com and www.rayrooter.com as custom domains in Render, then update DNS.
