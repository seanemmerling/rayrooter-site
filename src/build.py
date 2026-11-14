"""Builds the static site into public/. Run: python3 src/build.py"""
import html, json, pathlib, shutil, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from content import SITE, IMAGES, REVIEWS, SERVICES, CITIES, REDIRECTS

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "public"
e = html.escape

ICONS = {
    "pipe": '<path d="M3 9h7a3 3 0 0 1 3 3v9M3 15h4a2 2 0 0 1 2 2v4M17 3v6M21 3v6M15 9h8"/>',
    "water": '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/><path d="M9 14a3 3 0 0 0 3 3"/>',
    "jet": '<path d="M3 12h9"/><path d="M12 8v8l4-4z"/><path d="M17 7l4-2M17 12h5M17 17l4 2"/>',
    "camera": '<rect x="2" y="7" width="14" height="10" rx="2"/><path d="M16 11l6-3v8l-6-3"/><circle cx="9" cy="12" r="2.5"/>',
    "drain": '<circle cx="12" cy="12" r="9"/><path d="M8 12h8M12 8v8M9 9l6 6M15 9l-6 6"/>',
    "gas": '<path d="M12 3c2 3 5 5 5 9a5 5 0 0 1-10 0c0-2 1-3.5 2-4.5 0 2 1 3 2 3 0-3 1-5.5 1-7.5z"/>',
    "heat": '<path d="M6 21V5M10 21V5M14 21V5M18 21V5M4 21h16M4 5h16"/>',
    "phone": '<path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 5a2 2 0 0 1 2-2z"/>',
    "check": '<path d="M5 12l4 4L19 6"/>',
    "star": '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z" fill="currentColor" stroke="none"/>',
    "sms": '<path d="M4 5h16v11H8l-4 4z"/>',
}

def icon(name, cls="ic"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'

def stars(n=5):
    return '<span class="stars" aria-label="5 stars">' + icon("star", "st") * n + "</span>"

def call_btn(cls="btn btn-primary", label=None):
    return f'<a class="{cls}" href="{SITE["phone_href"]}">{icon("phone")}<span>{label or "Call " + SITE["phone"]}</span></a>'

NAV = [("/", "Home"), ("/services/", "Services"), ("/clients-one/", "Reviews"), ("/about-us/", "About"), ("/contact-us/", "Contact")]

def schema():
    return {
        "@context": "https://schema.org",
        "@type": "HomeAndConstructionBusiness",
        "name": SITE["name"],
        "url": SITE["domain"] + "/",
        "telephone": "+1-" + SITE["phone"],
        "email": SITE["email"],
        "image": SITE["domain"] + IMAGES["og"],
        "address": {"@type": "PostalAddress", "addressLocality": "Midland Park", "addressRegion": "NJ", "addressCountry": "US"},
        "areaServed": [f"{c} County, NJ" for c in SITE["counties"]],
        "aggregateRating": {"@type": "AggregateRating", "ratingValue": SITE["rating"], "bestRating": "5"},
        "sameAs": [SITE["google_reviews_url"]],
    }

def layout(path, title, desc, body, active="/"):
    nav = "".join(f'<a href="{h}"{" aria-current=page" if h == active else ""}>{t}</a>' for h, t in NAV)
    svc_links = "".join(f'<li><a href="{s["path"]}">{e(s["nav"])}</a></li>' for s in SERVICES[:5])
    area_links = "".join(f'<li><a href="{c["path"]}">{e(c["city"])}</a></li>' for c in CITIES)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE['domain']}{path}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{SITE['domain']}{IMAGES['og']}">
<meta property="og:type" content="website">
<link rel="icon" href="{IMAGES['favicon']}">
<link rel="preload" as="image" href="{IMAGES['hero']}"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
<script type="application/ld+json">{json.dumps(schema())}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="topbar"><div class="wrap">
  <span>Trenchless sewer &amp; water line specialists &middot; {e(", ".join(SITE['counties'][:3]))} &amp; {SITE['counties'][3]} County</span>
  <span>{SITE['hours']} &middot; Licensed &amp; Insured</span>
</div></div>
<header class="site-header"><div class="wrap hdr">
  <a class="brand" href="/" aria-label="{SITE['name']} home">
    <img src="{IMAGES['logo']}" alt="Ray Rooter Trenchless" width="160" height="58">
  </a>
  <nav class="nav" aria-label="Main">{nav}</nav>
  {call_btn("btn btn-primary hdr-call", SITE["phone"])}
</div></header>
<main id="main">
{body}
</main>
<section class="cta-band"><div class="wrap cta-inner">
  <div><h2>Sewer or water line problem?</h2><p>Talk to a trenchless specialist today. Free estimates, camera inspection available. {SITE['hours']}.</p></div>
  <div class="cta-actions">{call_btn("btn btn-light")}<a class="btn btn-ghost-light" href="{SITE['sms_href']}">{icon("sms")}<span>Text us</span></a></div>
</div></section>
<footer class="site-footer"><div class="wrap foot">
  <div>
    <a class="brand brand-foot" href="/"><img src="{IMAGES['logo']}" alt="Ray Rooter Trenchless" width="160" height="58"></a>
    <p>No-dig sewer and water line repair for North Jersey homes and businesses. Licensed &amp; insured, led by Licensed Master Plumber Steven Ray.</p>
  </div>
  <div><h3>Services</h3><ul>{svc_links}</ul></div>
  <div><h3>Service areas</h3><ul>{area_links}</ul></div>
  <div><h3>Contact</h3><ul>
    <li><a href="{SITE['phone_href']}">{SITE['phone']}</a></li>
    <li><a href="mailto:{SITE['email']}">{SITE['email']}</a></li>
    <li>{SITE['hours']}</li>
    <li>Based in {SITE['base_town']}</li>
  </ul></div>
</div>
<div class="wrap legal">&copy; Ray Rooter Trenchless. All rights reserved.</div>
</footer>
<a class="mobile-call" href="{SITE['phone_href']}">{icon("phone")} Call {SITE['phone']}</a>
</body>
</html>
"""

def service_card(s):
    return f'''<a class="card svc" href="{s["path"]}">
  <span class="svc-ic">{icon(s["icon"])}</span>
  <h3>{e(s["nav"])}</h3><p>{e(s["summary"])}</p><span class="more">Learn more &rarr;</span>
</a>'''

def reviews_block(limit=6, heading=True):
    cards = "".join(f'<figure class="card review">{stars()}<blockquote>{e(t)}</blockquote><figcaption>{e(n)} <span>Google review</span></figcaption></figure>' for n, t in REVIEWS[:limit])
    head = f'''<div class="sec-head"><p class="eyebrow">{stars()} {SITE["rating"]} on Google</p><h2>What North Jersey homeowners say</h2></div>''' if heading else ""
    return f'''<section class="sec reviews-sec"><div class="wrap">{head}
<div class="grid g3">{cards}</div>
<p class="center"><a class="btn btn-outline" href="{SITE["google_reviews_url"]}" rel="noopener" target="_blank">Read all reviews on Google</a></p>
</div></section>'''

def home():
    trust = "".join(f'<li>{icon("check")}<span>{t}</span></li>' for t in ["No digging up your yard", "Free estimates", "Licensed &amp; insured", "HD camera on every job"])
    steps = [("1", "Camera inspection", "We run an HD camera through the line and show you exactly what's wrong."),
             ("2", "Clean the line", "High pressure hydro jetting clears roots, grease, and scale."),
             ("3", "Fix it without digging", "We reline or replace the pipe from small access points, usually in a day."),
             ("4", "Show you the result", "A final camera run confirms the fix. You get the video.")]
    steps_html = "".join(f'<li class="step"><span class="num">{n}</span><h3>{t}</h3><p>{d}</p></li>' for n, t, d in steps)
    core = "".join(service_card(s) for s in SERVICES[:5]) + f'''<a class="card svc svc-cta" href="{SITE["phone_href"]}"><span class="svc-ic">{icon("phone")}</span><h3>Not sure what you need?</h3><p>Start with a camera inspection. We'll show you exactly what's going on before quoting anything.</p><span class="more">Call {SITE["phone"]} &rarr;</span></a>'''
    areas = "".join(f'<a class="chip" href="{c["path"]}">{e(c["city"])}</a>' for c in CITIES)
    body = f'''
<section class="hero" style="--hero:url('{IMAGES["hero"]}')"><div class="wrap hero-inner">
  <p class="eyebrow light">{stars()} Rated {SITE["rating"]} on Google</p>
  <h1>Sewer &amp; water lines fixed <span class="hl">without digging up your yard.</span></h1>
  <p class="lead">Trenchless sewer repair, pipelining, hydro jetting, camera inspections, and water line replacement across Bergen, Passaic, Morris, and Hudson County.</p>
  <div class="hero-actions">{call_btn()}<a class="btn btn-ghost-light" href="/contact-us/">Get a free estimate</a></div>
  <ul class="trust">{trust}</ul>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">What we do</p><h2>Trenchless specialists, not general plumbers</h2>
  <p>We focus on one thing: diagnosing and fixing sewer and water lines with the least possible disruption to your property.</p></div>
  <div class="grid g3 svc-grid">{core}</div>
</div></section>

<section class="sec alt"><div class="wrap split">
  <div>
    <p class="eyebrow">Why trenchless</p>
    <h2>The fix happens underground. Your yard stays put.</h2>
    <p>Traditional sewer replacement means an excavator, a trench from your house to the street, and weeks of restoration. Trenchless repair works through existing cleanouts and small access points instead.</p>
    <table class="compare"><thead><tr><th></th><th>Trenchless</th><th>Dig &amp; replace</th></tr></thead><tbody>
      <tr><td>Excavation</td><td>1&ndash;2 small access points</td><td>Full trench</td></tr>
      <tr><td>Typical time</td><td>About a day</td><td>Several days or more</td></tr>
      <tr><td>Lawn, driveway, basement</td><td>Left intact</td><td>Torn up and restored</td></tr>
      <tr><td>Finished pipe</td><td>Seamless, root-proof</td><td>Jointed pipe</td></tr>
    </tbody></table>
  </div>
  <div class="stats">
    <div class="stat"><b>1 day</b><span>typical trenchless repair</span></div>
    <div class="stat"><b>0</b><span>trenches through your yard</span></div>
    <div class="stat"><b>50 yr</b><span>design life of a CIPP liner</span></div>
    <div class="stat"><b>10 yr</b><span>manufacturer's warranty</span></div>
  </div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">How it works</p><h2>From diagnosis to done, usually in a day</h2></div>
  <ol class="steps">{steps_html}</ol>
</div></section>

{reviews_block(3)}

<section class="sec alt"><div class="wrap split">
  <div class="photo"><img src="{IMAGES["street_job"]}" alt="Ray Rooter crew on a trenchless job in North Jersey" loading="lazy"></div>
  <div>
    <p class="eyebrow">Local &amp; owner-operated</p>
    <h2>Led by Licensed Master Plumber Steven Ray</h2>
    <p>Ray Rooter Trenchless is a local company based in {SITE["base_town"]}. Steve has more than 15 years of experience on residential and commercial sewer jobs, and he's on every job. You get a straight diagnosis, a firm price before we start, and the camera footage to back it up.</p>
    <p>We serve homeowners, home buyers, landlords, and commercial properties including restaurants, offices, and multi-family buildings.</p>
    <p class="chips">{areas}</p>
    <a class="btn btn-outline" href="/about-us/">About us</a>
  </div>
</div></section>
'''
    return layout("/", "Trenchless Sewer Repair & Hydro Jetting in North NJ | Ray Rooter Trenchless",
                  "No-dig sewer line repair, pipelining, hydro jetting, sewer camera inspection, and trenchless water line replacement in Bergen, Passaic, Morris, and Hudson County NJ. Free estimates.", body, "/")

def render_body(blocks):
    out = []
    for kind, val in blocks:
        if kind in ("ul", "ol"):
            items = "".join(f"<li>{e(i)}</li>" for i in val)
            cls = ' class="checks"' if kind == "ul" else ' class="numbered"'
            out.append(f"<{kind}{cls}>{items}</{kind}>")
        else:
            out.append(f"<{kind}>{e(val)}</{kind}>")
    return "\n".join(out)

def page_hero(title, sub, crumb=None):
    c = f'<p class="crumb"><a href="/">Home</a> / {crumb}</p>' if crumb else ""
    return f'<section class="page-hero"><div class="wrap">{c}<h1>{e(title)}</h1><p class="lead">{e(sub)}</p><div class="hero-actions">{call_btn()}</div></div></section>'

def aside():
    links = "".join(f'<li><a href="{s["path"]}">{e(s["nav"])}</a></li>' for s in SERVICES)
    return f'''<aside class="side">
  <div class="card side-cta"><h3>Free estimate</h3><p>Call or text to describe the problem. Camera inspection available.</p>{call_btn("btn btn-primary btn-block")}<a class="btn btn-outline btn-block" href="{SITE["sms_href"]}">Text us</a><p class="small">{SITE["hours"]}</p></div>
  <div class="card"><h3>Services</h3><ul class="side-links">{links}</ul></div>
</aside>'''

def figure(s):
    if not s.get("img"):
        return ""
    src, alt = s["img"]
    return f'<figure class="svc-photo"><img src="{src}" alt="{e(alt)}" loading="lazy"></figure>'

def service_page(s):
    body = page_hero(s["title"], s["summary"], '<a href="/services/">Services</a>') + f'''
<section class="sec"><div class="wrap content-grid"><article class="prose">{figure(s)}{render_body(s["body"])}</article>{aside()}</div></section>
{reviews_block(3)}'''
    return layout(s["path"], s["seo_title"], s["desc"], body, "/services/")

def city_page(c):
    blocks = [("p", c["intro"]), ("p", c["local"]),
              ("h2", f"Trenchless services in {c['city']}"),
              ("ul", ["Trenchless sewer line repair and pipelining (CIPP)", "High pressure hydro jetting and root removal",
                      "Sewer camera inspections, including pre-purchase inspections", "Trenchless water line replacement"]),
              ("h2", "Why homeowners choose trenchless"),
              ("ul", ["No trench through your yard, driveway, or basement", "Usually completed in a day",
                      "Seamless, root-proof pipe with a 10-year manufacturer's warranty", "Camera video before and after the work"])]
    title = f"Trenchless Sewer Repair in {c['city']}"
    body = page_hero(title, "Fix roots, cracks, and collapsed pipe without excavating.", '<a href="/services/">Services</a>') + f'''
<section class="sec"><div class="wrap content-grid"><article class="prose">{render_body(blocks)}</article>{aside()}</div></section>
{reviews_block(3)}'''
    return layout(c["path"], c["seo_title"], c["desc"], body, "/services/")

def services_index(path):
    cards = "".join(service_card(s) for s in SERVICES)
    areas = "".join(f'<a class="chip" href="{c["path"]}">{e(c["city"])}</a>' for c in CITIES)
    body = page_hero("Our Services", "Trenchless sewer and water line repair, hydro jetting, and camera inspections.") + f'''
<section class="sec"><div class="wrap"><div class="grid g3 svc-grid">{cards}</div>
<div class="sec-head" style="margin-top:3rem"><h2>Service areas</h2></div><p class="chips center">{areas}</p></div></section>'''
    return layout(path, "Trenchless Sewer & Water Line Services | Ray Rooter Trenchless",
                  "Trenchless sewer repair, pipelining, hydro jetting, sewer camera inspection, and trenchless water line replacement in North NJ.", body, "/services/")

def about():
    body = page_hero("About Ray Rooter Trenchless", "Local, licensed, and focused on sewer and water lines.") + f'''
<section class="sec"><div class="wrap split">
  <div class="prose">
    <p>Ray Rooter Trenchless specializes in one thing: fixing sewer and water lines without digging up your property. Led by Steven Ray, a Licensed Master Plumber with more than 15 years of experience on residential and commercial jobs, our crew uses trenchless pipelining, high pressure hydro jetting, and HD sewer cameras to find the problem and fix it right the first time.</p>
    <p>Because we focus on trenchless work, we bring the right equipment to every job and give you a straight answer and a firm price before we start. We are local, licensed, insured, and we stand behind our work.</p>
    <ul class="checks"><li>Licensed Master Plumber on every job</li><li>Licensed &amp; insured</li><li>Free estimates</li><li>Camera footage before and after</li><li>Locally owned and operated in {SITE["base_town"]}</li></ul>
  </div>
  <div class="photo"><img src="{IMAGES["basement_rig"]}" alt="Trenchless equipment set up in a finished basement with floors protected" loading="lazy"></div>
</div></section>
{reviews_block(3)}'''
    return layout("/about-us/", "About Ray Rooter Trenchless | North NJ Sewer Line Specialists",
                  "Licensed and insured trenchless sewer and water line specialists led by Master Plumber Steven Ray, serving Bergen, Passaic, Morris, and Hudson County NJ.", body, "/about-us/")

def contact(path):
    body = page_hero("Get a Free Estimate", "The fastest way to reach us is a call or text.") + f'''
<section class="sec"><div class="wrap contact-grid">
  <a class="card contact-card" href="{SITE["phone_href"]}">{icon("phone")}<h3>Call</h3><p>{SITE["phone"]}</p></a>
  <a class="card contact-card" href="{SITE["sms_href"]}">{icon("sms")}<h3>Text</h3><p>Send a photo or describe the problem</p></a>
  <a class="card contact-card" href="mailto:{SITE["email"]}?subject=Estimate%20request">{icon("drain")}<h3>Email</h3><p>{SITE["email"]}</p></a>
</div>
<div class="wrap prose narrow">
  <h2>What to include</h2>
  <ul class="checks"><li>Your town and the property type (house, multi-family, commercial)</li><li>What's happening: backups, slow drains, low water pressure, wet spots</li><li>Whether you're buying the home and need a pre-purchase inspection</li></ul>
  <p><strong>{SITE["hours"]}.</strong> Serving Bergen, Passaic, Morris, and Hudson County from {SITE["base_town"]}.</p>
</div></section>'''
    return layout(path, "Contact Ray Rooter Trenchless | Free Sewer Line Estimate",
                  f"Call {SITE['phone']} for a free estimate on trenchless sewer repair, hydro jetting, or sewer camera inspection. {SITE['hours']}.", body, "/contact-us/")

def reviews_page():
    body = page_hero("Customer Reviews", f"Rated {SITE['rating']} stars on Google by North Jersey homeowners.") + reviews_block(len(REVIEWS), heading=False)
    return layout("/clients-one/", "Customer Reviews | Ray Rooter Trenchless",
                  "Read Google reviews from North Jersey homeowners who used Ray Rooter Trenchless for sewer repair, pipelining, jetting, and camera inspections.", body, "/clients-one/")

def gallery():
    imgs = "".join(f'<img src="{u}" alt="Ray Rooter Trenchless job photo" loading="lazy">' for u in IMAGES["gallery"])
    body = page_hero("Project Gallery", "A look at our trenchless and sewer work.") + f'<section class="sec"><div class="wrap gallery">{imgs}</div></section>'
    return layout("/gallery/", "Project Gallery | Ray Rooter Trenchless", "Photos of trenchless sewer repair, hydro jetting, and camera inspection projects in North NJ.", body)

def not_found():
    body = page_hero("Page not found", "That page has moved. Here's where to go next.") + f'<section class="sec"><div class="wrap grid g3 svc-grid">{"".join(service_card(s) for s in SERVICES[:3])}</div></section>'
    return layout("/404.html", "Page not found | Ray Rooter Trenchless", "Page not found.", body)

def write(path, text):
    p = OUT / (path.strip("/") + "/index.html" if not path.endswith(".html") else path.strip("/"))
    if path == "/":
        p = OUT / "index.html"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return path

def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    shutil.copy(ROOT / "src" / "style.css", OUT / "assets" / "style.css")
    shutil.copytree(ROOT / "src" / "img", OUT / "assets" / "img")
    pages = [write("/", home())]
    for p in ("/services/", "/all-services/"):
        pages.append(write(p, services_index(p)))
    for s in SERVICES:
        pages.append(write(s["path"], service_page(s)))
    for c in CITIES:
        pages.append(write(c["path"], city_page(c)))
    pages.append(write("/about-us/", about()))
    for p in ("/contact-us/", "/get-appointment/"):
        pages.append(write(p, contact(p)))
    pages.append(write("/clients-one/", reviews_page()))
    pages.append(write("/gallery/", gallery()))
    write("/404.html", not_found())
    urls = "".join(f"<url><loc>{SITE['domain']}{p}</loc></url>" for p in pages if p != "/get-appointment/")
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE['domain']}/sitemap.xml\n")
    print(f"Built {len(pages)} pages into {OUT}")

if __name__ == "__main__":
    main()
