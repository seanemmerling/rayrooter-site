"""Builds the static site into public/. Run: python3 src/build.py"""
import html, json, pathlib, shutil, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from content import TRENCHLESS, SITE, IMAGES, REVIEWS, REVIEWS_CAPTURED, FEATURED_REVIEWERS, SERVICES, CITIES, COUNTIES, REDIRECTS
import re, datetime

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
    "stack": '<path d="M10 2v20M14 2v20M7 6h10M7 18h10M17 10h4v4"/>',
    "star": '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z" fill="currentColor" stroke="none"/>',
    "sms": '<path d="M4 5h16v11H8l-4 4z"/>',
}

def icon(name, cls="ic"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'

def stars(n=5):
    return '<span class="stars" aria-label="5 stars">' + icon("star", "st") * n + "</span>"

def call_btn(cls="btn btn-primary", label=None):
    return f'<a class="{cls}" href="{SITE["phone_href"]}">{icon("phone")}<span>{label or "Call " + SITE["phone"]}</span></a>'

NAV = [("/", "Home"), ("/trenchless/", "Trenchless"), ("/services/", "Services"), ("/service-areas/", "Service Areas"), ("/clients-one/", "Reviews"), ("/about-us/", "About"), ("/contact-us/", "Contact")]

BIZ_ID = SITE["domain"] + "/#business"

def page_type(path):
    if path == "/": return "home"
    if path.startswith("/trenchless"): return "trenchless_landing"
    if "/trenchless-sewer-repair-" in path: return "city"
    if path.startswith("/service-areas/") and path != "/service-areas/": return "service_area"
    if path.startswith("/services/") and path != "/services/": return "service"
    return {"/contact-us/": "contact", "/get-appointment/": "contact", "/clients-one/": "reviews"}.get(path, "other")

def analytics_head(path, title):
    gid = SITE["ga4_id"]
    dl = json.dumps({"page_type": page_type(path), "page_title": title.split(" | ")[0]})
    return (f'<script async src="https://www.googletagmanager.com/gtag/js?id={gid}"></script>'
            f'<script>window.dataLayer=window.dataLayer||[];dataLayer.push({dl});'
            f'function gtag(){{dataLayer.push(arguments);}}gtag("js",new Date());'
            f'gtag("config","{gid}",{{page_type:"{page_type(path)}"}});</script>')

TRACK_JS = """<script>
(function(){
  var pt=(window.dataLayer&&window.dataLayer[0]||{}).page_type||'other';
  function where(a){
    if(a.classList.contains('mobile-call')) return 'sticky_mobile_bar';
    if(a.closest('.site-header')) return 'header';
    if(a.closest('.hero,.page-hero')) return 'hero';
    if(a.closest('.cta-band')) return 'bottom_cta_band';
    if(a.closest('.side-cta')) return 'sidebar_estimate_box';
    if(a.closest('.svc-cta')) return 'not_sure_card';
    if(a.closest('.contact-card')) return 'contact_page_card';
    if(a.closest('footer')) return 'footer';
    return 'in_content';
  }
  document.addEventListener('click',function(e){
    var a=e.target.closest('a'); if(!a) return;
    var h=a.getAttribute('href')||'', ev=null;
    if(h.indexOf('tel:')===0) ev='phone_click';
    else if(h.indexOf('sms:')===0) ev='text_click';
    else if(h.indexOf('mailto:')===0) ev='email_click';
    else if(h.indexOf('maps.google.com')>-1) ev='google_reviews_click';
    if(!ev) return;
    var p={cta_location:where(a), cta_text:(a.innerText||'').replace(/\\s+/g,' ').trim().slice(0,60),
           page_type:pt, page_path:location.pathname};
    if(typeof gtag==='function') gtag('event',ev,p);
    window.dataLayer.push(Object.assign({event:'lead_'+ev},p));
  });
})();
</script>"""

def schema():
    return {
        "@context": "https://schema.org",
        "@type": ["HomeAndConstructionBusiness", "Plumber"],
        "@id": BIZ_ID,
        "name": SITE["name"],
        "url": SITE["domain"] + "/",
        "telephone": "+1-" + SITE["phone"],
        "email": SITE["email"],
        "image": SITE["domain"] + IMAGES["og"],
        "logo": SITE["domain"] + IMAGES["logo"],
        "address": {"@type": "PostalAddress", "streetAddress": "230 Rock St #2", "addressLocality": "Midland Park",
                    "addressRegion": "NJ", "postalCode": "07432", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 40.9953604, "longitude": -74.152213},
        "hasMap": SITE["google_reviews_url"],
        "areaServed": [{"@type": "AdministrativeArea", "name": f"{c} County, NJ"} for c in SITE["counties"]]
                      + [{"@type": "City", "name": n} for n in ("Montclair, NJ", "Nutley, NJ")],
        "aggregateRating": {"@type": "AggregateRating", "ratingValue": SITE["rating"], "reviewCount": SITE["review_count"], "bestRating": "5"},
        "sameAs": [SITE["google_reviews_url"]],
        "knowsAbout": ["Trenchless sewer repair", "Cured-in-place pipe lining", "Hydro jetting", "Sewer camera inspection",
                       "Soil stack lining", "Trenchless water line replacement"],
    }

def page_schemas(path, title, desc, home):
    out = [schema()]
    if home:
        out.append({"@context": "https://schema.org", "@type": "WebSite", "name": SITE["name"], "url": SITE["domain"] + "/"})
        return out
    name = title.split(" | ")[0]
    parts = [p for p in path.strip("/").split("/") if p]
    crumbs = [("Home", "/")]
    if len(parts) > 1:
        sec = {"services": ("Services", "/services/"), "service-areas": ("Service Areas", "/service-areas/")}.get(parts[0])
        if sec:
            crumbs.append(sec)
    crumbs.append((name, path))
    out.append({"@context": "https://schema.org", "@type": "BreadcrumbList",
                "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE["domain"] + u} for i, (n, u) in enumerate(crumbs)]})
    if (path.startswith("/services/") and len(parts) == 2) or (path.startswith("/service-areas/") and len(parts) == 2):
        out.append({"@context": "https://schema.org", "@type": "Service", "name": name, "description": desc,
                    "provider": {"@id": BIZ_ID}, "url": SITE["domain"] + path,
                    "areaServed": {"@type": "State", "name": "New Jersey"}})
    return out

def layout(path, title, desc, body, active="/", canonical=None, extra_head="", home=False, noindex=False):
    if len(title) > 62:
        title = title.replace(" | Ray Rooter Trenchless", " | Ray Rooter")
    ld = "".join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in page_schemas(path, title, desc, home))
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    nav = "".join(f'<a href="{h}"{" aria-current=page" if h == active else ""}>{t}</a>' for h, t in NAV)
    svc_links = "".join(f'<li><a href="{href(s)}">{e(s["nav"])}</a></li>' for s in SERVICES[:5])
    area_links = "".join(f'<li><a href="/service-areas/{c["slug"]}/">{e(c["name"])}</a></li>' for c in COUNTIES)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE['domain']}{canonical or path}">{robots}{extra_head}
{analytics_head(path, title)}
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{SITE['domain']}{IMAGES['og']}">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE['domain']}{canonical or path}">
<meta property="og:site_name" content="{SITE['name']}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0B0D10">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/img/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preload" as="image" href="{IMAGES['hero']}"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="topbar"><div class="wrap">
  <span>Trenchless no-dig sewer repair &middot; Northern New Jersey</span>
  <span>{SITE['hours']} &middot; Licensed &amp; Insured</span>
</div></div>
<header class="site-header"><div class="wrap hdr">
  <a class="brand" href="/" aria-label="{SITE['name']} home">
    <img src="{IMAGES['logo']}" alt="Ray Rooter Trenchless" width="160" height="58">
  </a>
  <nav class="nav" id="site-nav" aria-label="Main">{nav}</nav>
  {call_btn("btn btn-primary hdr-call", SITE["phone"])}
  <button class="menu-toggle" type="button" aria-controls="site-nav" aria-expanded="false" aria-label="Open menu"><span></span><span></span><span></span></button>
</div></header>
<main id="main">
{body}
</main>
<section class="cta-band"><div class="wrap cta-inner">
  <div><h2>Sewer or water line problem?</h2><p>Call or text for a free estimate. Camera inspections available. {SITE['hours']}.</p></div>
  <div class="cta-actions">{call_btn("btn btn-light")}<a class="btn btn-ghost-light" href="{SITE['sms_href']}">{icon("sms")}<span>Text us</span></a></div>
</div></section>
<footer class="site-footer"><div class="wrap foot">
  <div>
    <a class="brand brand-foot" href="/"><img src="{IMAGES['logo']}" alt="Ray Rooter Trenchless" width="160" height="58"></a>
    <p>No-dig sewer and water line repair for North Jersey homes and businesses. Licensed &amp; insured. Owner and Licensed Master Plumber Steven Ray is on every job site.</p>
  </div>
  <div><h3>Services</h3><ul>{svc_links}</ul></div>
  <div><h3>Service areas</h3><ul>{area_links}</ul></div>
  <div><h3>Contact</h3><ul>
    <li><a href="{SITE['phone_href']}">{SITE['phone']}</a></li>
    <li><a href="mailto:{SITE['email']}">{SITE['email']}</a></li>
    <li>{SITE['hours']}</li>
    <li>Based in {SITE['base_town']}</li>
  </ul><a class="btn btn-primary foot-cta" href="{SITE['phone_href']}">Request an estimate</a></div>
</div>
<div class="wrap legal"><span>&copy; {datetime.date.today().year} Ray Rooter Trenchless. All rights reserved.</span><span>230 Rock St #2, Midland Park, NJ 07432 &middot; Licensed &amp; insured</span></div>
</footer>
<script>
(function(){{var b=document.querySelector('.menu-toggle'),n=document.getElementById('site-nav');
b.addEventListener('click',function(){{var o=n.classList.toggle('open');b.setAttribute('aria-expanded',o);b.setAttribute('aria-label',o?'Close menu':'Open menu');document.body.classList.toggle('menu-open',o);}});
document.addEventListener('keydown',function(e){{if(e.key==='Escape'&&n.classList.contains('open'))b.click();}});}})();
</script>
{TRACK_JS}
<a class="mobile-call" href="{SITE['phone_href']}">{icon("phone")} Call {SITE['phone']}</a>
</body>
</html>
"""

def href(s):
    return s.get("card_href", s["path"])

def service_card(s):
    return f'''<a class="card svc" href="{href(s)}">
  <span class="svc-ic">{icon(s["icon"])}</span>
  <h3>{e(s["nav"])}</h3><p>{e(s["summary"])}</p><span class="more">Learn more &rarr;</span>
</a>'''

def review_year(rel):
    base = datetime.date.fromisoformat(REVIEWS_CAPTURED)
    m = re.search(r"(\d+|an?)\s+(day|week|month|year)", rel)
    if not m:
        return base.year
    n = 1 if m.group(1) in ("a", "an") else int(m.group(1))
    days = {"day": 1, "week": 7, "month": 30, "year": 365}[m.group(2)] * n
    return (base - datetime.timedelta(days=days)).year

def review_card(r, clamp=True):
    name, s, rel, text = r
    initial = e(name.strip()[0].upper())
    cls = "card review clamp" if clamp else "card review"
    return f'''<figure class="{cls}">
  <div class="rv-head"><span class="avatar">{initial}</span><div><figcaption>{e(name)}</figcaption><span class="rv-meta">{stars(s)} <span>{review_year(rel)} &middot; Google</span></span></div><svg class="g" viewBox="0 0 24 24" aria-label="Google review"><path fill="#4285F4" d="M23 12.3c0-.8-.1-1.6-.2-2.3H12v4.4h6.2a5.3 5.3 0 0 1-2.3 3.5v2.9h3.7c2.2-2 3.4-5 3.4-8.5z"/><path fill="#34A853" d="M12 23.5c3.1 0 5.7-1 7.6-2.8l-3.7-2.9c-1 .7-2.4 1.1-3.9 1.1-3 0-5.5-2-6.4-4.7H1.8v3A11.5 11.5 0 0 0 12 23.5z"/><path fill="#FBBC05" d="M5.6 14.2a6.9 6.9 0 0 1 0-4.4v-3H1.8a11.5 11.5 0 0 0 0 10.4z"/><path fill="#EA4335" d="M12 5.1c1.7 0 3.2.6 4.4 1.7l3.3-3.3A11.5 11.5 0 0 0 1.8 6.8l3.8 3c.9-2.8 3.4-4.7 6.4-4.7z"/></svg></div>
  <blockquote>{e(text)}</blockquote>
</figure>'''

def rating_summary():
    return f'''<div class="rating-sum"><span class="big">{SITE["rating"]}</span><div>{stars()}<p>{SITE["review_count"]} Google reviews</p></div>
<a class="btn btn-outline" href="{SITE["google_reviews_url"]}" rel="noopener" target="_blank">View on Google Maps</a></div>'''

def featured():
    by = {r[0]: r for r in REVIEWS}
    return [by[n] for n in FEATURED_REVIEWERS if n in by]

def reviews_block(limit=3, heading=True):
    cards = "".join(review_card(r) for r in featured()[:limit])
    head = f'''<div class="sec-head"><p class="eyebrow">Reviews</p><h2>What North Jersey homeowners say</h2></div>{rating_summary()}''' if heading else ""
    return f'''<section class="sec reviews-sec"><div class="wrap">{head}
<div class="grid g3">{cards}</div>
<p class="center"><a class="btn btn-primary" href="/clients-one/">Read more reviews</a></p>
</div></section>'''

def cred_bar():
    items = [("Licensed Master Plumber", "Owner on every job site"),
             ("Licensed &amp; insured", "Residential &amp; commercial"),
             (f'{SITE["rating"]} on Google', f'{SITE["review_count"]} Google reviews'),
             ("Camera inspections", "Video before and after")]
    cells = "".join(f'<li><b>{t}</b><span>{d}</span></li>' for t, d in items)
    return f'<section class="cred" aria-label="Credentials"><ul class="wrap cred-grid">{cells}</ul></section>'

def num(n):
    return f"{int(n):02d}"

def home():
    trust = "".join(f'<li>{icon("check")}<span>{t}</span></li>' for t in ["No digging up your yard", "Owner &amp; Licensed Master Plumber on every job site", "Free estimates", "Licensed &amp; insured"])
    steps = [("1", "Camera inspection", "We run an HD camera through the line and show you what's wrong."),
             ("2", "Clean the line", "High pressure hydro jetting clears roots, grease, and scale."),
             ("3", "Fix it without digging", "We reline or replace the pipe from small access points, usually in a day."),
             ("4", "Show you the result", "A final camera run confirms the fix. You get the video.")]
    steps_html = "".join(f'<li class="step"><span class="num">{num(n)}</span><h3>{t}</h3><p>{d}</p></li>' for n, t, d in steps)
    core = "".join(service_card(s) for s in SERVICES[:5]) + f'''<a class="card svc svc-cta" href="/services/sewer-line-camera/"><span class="svc-ic">{icon("phone")}</span><h3>Not sure what you need?</h3><p>Start with a sewer camera inspection. You'll see the condition of the line before we quote a repair.</p><span class="more">Book a camera inspection &rarr;</span></a>'''
    areas = "".join(f'<a class="chip" href="/service-areas/{c["slug"]}/">{e(c["name"])}</a>' for c in COUNTIES) + "".join(f'<a class="chip" href="{c["path"]}">{e(c["city"])}</a>' for c in CITIES if c["city"] in ("Montclair, NJ", "Nutley, NJ"))
    segs = [("Homeowners", "Sewer and water lines repaired without tearing up the yard, driveway, or finished basement."),
            ("Home buyers", "Pre-purchase sewer camera inspections with video, so you know before you close."),
            ("Landlords &amp; property managers", "Multi-family laterals, soil stacks, and roof drains lined with minimal disruption to tenants."),
            ("Commercial properties", "Restaurants, offices, and commercial buildings, including manhole and parking lot work.")]
    segments = "".join(f'<div class="seg-card"><h3>{t}</h3><p>{d}</p></div>' for t, d in segs)
    body = f'''
<section class="hero" style="--hero:url('{IMAGES["hero"]}')"><div class="wrap hero-inner">
  <p class="eyebrow light">{stars()} Rated {SITE["rating"]} on Google</p>
  <h1>Trenchless No Dig Sewer Repair in New Jersey</h1>
  <p class="lead">Sewer line repair for cracked, broken, and root-filled pipe, done without digging up your yard, driveway, or basement. Most jobs take about a day, with camera video before and after.</p>
  <div class="hero-actions">{call_btn("btn btn-primary", "Free estimate: " + SITE["phone"])}<a class="btn btn-ghost-light" href="/trenchless/">How trenchless repair works</a></div>
  <ul class="trust">{trust}</ul>
</div></section>
{cred_bar()}

<section class="sec dark"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">What we do</p><h2>Our services</h2>
  <p>Trenchless sewer repair, high pressure hydro jetting, and HD sewer camera inspections.</p></div>
  <div class="grid g3 svc-grid">{core}</div>
</div></section>

<section class="sec alt"><div class="wrap split">
  <div>
    <p class="eyebrow">Why trenchless</p>
    <h2>How trenchless repair compares to digging</h2>
    <p>Traditional sewer replacement involves excavating a trench from the house to the street and restoring the yard, driveway, or floor afterward. Trenchless repair works through existing cleanouts and small access points instead.</p>
    <table class="compare"><thead><tr><th></th><th>Trenchless</th><th>Dig &amp; replace</th></tr></thead><tbody>
      <tr><td>Excavation</td><td>1&ndash;2 small access points</td><td>Full trench</td></tr>
      <tr><td>Typical time</td><td>About a day</td><td>Several days or more</td></tr>
      <tr><td>Lawn, driveway, basement</td><td>Left intact</td><td>Torn up and restored</td></tr>
      <tr><td>Finished pipe</td><td>Seamless, no joints</td><td>Jointed pipe</td></tr>
    </tbody></table>
  </div>
  <div class="stats">
    <div class="stat"><b>1 day</b><span>typical trenchless repair</span></div>
    <div class="stat"><b>6</b><span>North Jersey counties served</span></div>
    <div class="stat"><b>50 yr</b><span>design life of a CIPP liner</span></div>
    <div class="stat"><b>{SITE["rating"]}&#9733;</b><span>Google rating</span></div>
  </div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">How it works</p><h2>Our process</h2></div>
  <ol class="steps">{steps_html}</ol>
</div></section>

<section class="sec seg-sec"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">Who we serve</p><h2>Residential and commercial work</h2>
  <p>We work on single-family homes, multi-family buildings, and commercial properties, from house laterals to multi-story soil stacks.</p></div>
  <div class="grid g4 seg">{segments}</div>
</div></section>

{reviews_block(3)}

<section class="sec alt"><div class="wrap split">
  <div class="photo"><img src="{IMAGES["trailer"]}" alt="Ray Rooter Trenchless pipe lining trailer at a customer's home" loading="lazy"></div>
  <div>
    <p class="eyebrow">Local &amp; owner-operated</p>
    <h2>Owner &amp; Licensed Master Plumber Steven Ray on every job site</h2>
    <p>Ray Rooter Trenchless is a local company based in {SITE["base_town"]}. Steve is the owner and a Licensed Master Plumber with more than 15 years of experience on residential and commercial sewer jobs, and he's on site for every job. The work is done by our own crew, not a subcontractor. Estimates are based on a camera inspection, you get the price before work starts, and you receive a copy of the footage.</p>
    <p>We serve homeowners, home buyers, landlords, and commercial properties including restaurants, offices, and multi-family buildings.</p>
    <p class="chips">{areas}</p>
    <a class="btn btn-outline" href="/about-us/">About us</a>
  </div>
</div></section>
'''
    return layout("/", "Ray Rooter Trenchless | No Dig Sewer Repair in Northern NJ",
                  "Trenchless no-dig sewer repair, pipe lining, hydro jetting, and sewer camera inspections in northern NJ. Fix your sewer line without digging up your yard.", body, "/", home=True)

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
    links = "".join(f'<li><a href="{href(s)}">{e(s["nav"])}</a></li>' for s in SERVICES)
    return f'''<aside class="side">
  <div class="card side-cta"><h3>Free estimate</h3><p>Call or text to describe the problem. Camera inspection available.</p><p class="small"><b>Owner &amp; Licensed Master Plumber on every job site.</b></p>{call_btn("btn btn-primary btn-block")}<a class="btn btn-outline btn-block" href="{SITE["sms_href"]}">Text us</a><p class="small">{SITE["hours"]}</p></div>
  <div class="card"><h3>Services</h3><ul class="side-links">{links}</ul></div>
</aside>'''

def figure(s):
    if not s.get("img"):
        return ""
    src, alt = s["img"]
    return f'<figure class="svc-photo"><img src="{src}" alt="{e(alt)}" loading="lazy"></figure>'

def photos(s):
    if not s.get("photos"):
        return ""
    imgs = "".join(f'<img src="{u}" alt="{e(a)}" loading="lazy">' for u, a in s["photos"])
    return f'<h2>Recent jobs</h2><div class="svc-photos">{imgs}</div><p><a href="/gallery/">See all job photos</a></p>'

def service_page(s):
    body = page_hero(s["title"], s["summary"], '<a href="/services/">Services</a>') + f'''
<section class="sec"><div class="wrap content-grid"><article class="prose">{figure(s)}{render_body(s["body"])}{photos(s)}</article>{aside()}</div></section>
{reviews_block(3)}'''
    return layout(s["path"], s["seo_title"], s["desc"], body, "/services/", canonical=s.get("canonical"))

def city_page(c):
    blocks = [("p", c["intro"]), ("p", c["local"]),
              ("h2", f"Trenchless services in {c['city']}"),
              ("ul", ["Trenchless sewer line repair and pipelining (CIPP)", "High pressure hydro jetting and root removal",
                      "Sewer camera inspections, including pre-purchase inspections", "Trenchless water line replacement"]),
              ("h2", "Benefits of trenchless repair"),
              ("ul", ["No trench through your yard, driveway, or basement", "Usually completed in a day",
                      "Owner and Licensed Master Plumber Steven Ray on every job site", "Seamless liner with no joints, designed to last 50 years", "Camera video before and after the work"])]
    title = f"Trenchless Sewer Repair in {c['city']}"
    body = page_hero(title, "Sewer line repair for roots, cracks, and broken pipe, usually without excavating.", '<a href="/services/">Services</a>') + f'''
<section class="sec"><div class="wrap content-grid"><article class="prose">{render_body(blocks)}</article>{aside()}</div></section>
{reviews_block(3)}'''
    return layout(c["path"], c["seo_title"], c["desc"], body, "/services/")

def services_index(path):
    cards = "".join(service_card(s) for s in SERVICES)
    areas = "".join(f'<a class="chip" href="/service-areas/{c["slug"]}/">{e(c["name"])}</a>' for c in COUNTIES)
    body = page_hero("Our Services", "Trenchless sewer and water line repair, hydro jetting, and camera inspections.") + f'''
<section class="sec dark"><div class="wrap"><div class="grid g3 svc-grid">{cards}</div>
<div class="sec-head" style="margin-top:3rem"><h2>Service areas</h2></div><p class="chips center">{areas}</p></div></section>'''
    return layout(path, "Trenchless Sewer & Water Line Services | Ray Rooter Trenchless",
                  "Trenchless sewer repair, pipelining, hydro jetting, sewer camera inspection, and trenchless water line replacement in North NJ.", body, "/services/", canonical="/services/")

def trenchless_page():
    T = TRENCHLESS
    signs = "".join(f"<li>{e(x)}</li>" for x in T["signs"])
    fixes = "".join(f"<li>{e(x)}</li>" for x in T["fixes"])
    faq = "".join(f'<details class="faq"><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in T["faq"])
    by = {r[0]: r for r in REVIEWS}
    revs = "".join(review_card(by[n], clamp=False) for n in T["review_names"] if n in by)
    steps = [("1", "HD camera inspection", "We scope the line, find the damage, and measure it. You see the video."),
             ("2", "Hydro jet the pipe", "Roots, scale, and debris are cleared so the liner bonds to clean pipe."),
             ("3", "Install the liner", "A resin liner goes in through a cleanout or the toilet flange and cures into a new pipe inside the old one."),
             ("4", "Camera it again", "We run the camera through the finished pipe so you can see the result.")]
    inside_html = "".join(f'<figure class="inside"><img src="{u}" alt="{e(a)}" loading="lazy"><figcaption>{e(cap)}</figcaption></figure>' for u, a, cap in IMAGES["inside"])
    steps_html = "".join(f'<li class="step"><span class="num">{num(n)}</span><h3>{t}</h3><p>{d}</p></li>' for n, t, d in steps)
    faq_schema = {"@context": "https://schema.org", "@type": "FAQPage",
                  "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in T["faq"]]}
    svc_schema = {"@context": "https://schema.org", "@type": "Service", "serviceType": "Trenchless sewer repair",
                  "name": "Trenchless No Dig Sewer Repair", "provider": {"@type": "HomeAndConstructionBusiness", "name": SITE["name"], "telephone": "+1-" + SITE["phone"]},
                  "areaServed": ["Northern New Jersey"]}
    svc_schema["provider"] = {"@id": BIZ_ID}
    head = f'<script type="application/ld+json">{json.dumps(faq_schema)}</script><script type="application/ld+json">{json.dumps(svc_schema)}</script>'
    trust = "".join(f'<li>{icon("check")}<span>{t}</span></li>' for t in ["No digging in most cases", "Owner &amp; Licensed Master Plumber on every job site", "Usually done in a day", "Free estimates"])
    body = f'''
<section class="hero" style="--hero:url('{IMAGES["basement_rig"]}')"><div class="wrap hero-inner">
  <p class="eyebrow light">{stars()} Rated {SITE["rating"]} on Google &middot; {SITE["review_count"]} reviews</p>
  <h1>Trenchless No Dig Sewer Repair</h1>
  <p class="lead">We fix cracked, root-filled, and broken sewer lines from the inside, without tearing up your lawn, driveway, or finished basement. Serving northern New Jersey, from Montclair and Nutley to Ridgewood, Wayne, and Hoboken.</p>
  <div class="hero-actions">{call_btn("btn btn-primary", "Free estimate: " + SITE["phone"])}<a class="btn btn-ghost-light" href="{SITE["sms_href"]}">{icon("sms")}<span>Text us photos</span></a></div>
  <ul class="trust">{trust}</ul>
</div></section>
{cred_bar()}

<section class="sec"><div class="wrap split">
  <div class="prose">
    <p class="eyebrow">Is your sewer line failing?</p>
    <h2>Signs you need sewer line repair</h2>
    <ul class="checks">{signs}</ul>
    <p>Not sure? A <a href="/services/sewer-line-camera/">sewer camera inspection</a> shows the condition of the line before you decide on a repair.</p>
  </div>
  <div class="photo"><img src="{IMAGES["street_job"]}" alt="Ray Rooter crew on a trenchless sewer repair job" loading="lazy"></div>
</div></section>

<section class="sec dark"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">How no-dig repair works</p><h2>A new pipe inside the old one, usually in a day</h2>
  <p>Cured-in-place pipe (CIPP) lining creates a seamless pipe inside your existing sewer line, installed through a cleanout instead of a trench.</p></div>
  <ol class="steps steps-dark">{steps_html}</ol>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">Access points</p><h2>Where the liner is installed</h2>
  <p>The lining machine connects to the pipe at an existing cleanout, the toilet flange, a floor drain, or a manhole. Inside the house, floors are covered. Outside, no excavation is needed in most cases.</p></div>
  <div class="grid g3 inside-grid">{inside_html}</div>
  <p class="center"><a href="/gallery/">See more job photos</a></p>
</div></section>

<section class="sec alt"><div class="wrap split">
  <div>
    <p class="eyebrow">Comparison</p>
    <h2>Trenchless vs. digging</h2>
    <table class="compare"><thead><tr><th></th><th>Trenchless</th><th>Dig &amp; replace</th></tr></thead><tbody>
      <tr><td>Excavation</td><td>Usually none: cleanout or toilet flange</td><td>Full trench</td></tr>
      <tr><td>Typical time</td><td>About a day</td><td>Several days or more</td></tr>
      <tr><td>Lawn, driveway, basement</td><td>Left intact</td><td>Torn up and restored</td></tr>
      <tr><td>Finished pipe</td><td>Seamless, no joints</td><td>Jointed pipe</td></tr>
      <tr><td>Street permits &amp; police detail</td><td>Usually avoided</td><td>Often required</td></tr>
    </tbody></table>
  </div>
  <div class="prose">
    <h2>What we fix without digging</h2>
    <ul class="checks">{fixes}</ul>
  </div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">Reviews</p><h2>Customer reviews</h2></div>
  {rating_summary()}
  <div class="masonry">{revs}</div>
  <p class="center"><a class="btn btn-primary" href="/clients-one/">Read more reviews</a></p>
</div></section>

<section class="sec alt"><div class="wrap narrow-wrap">
  <div class="sec-head"><p class="eyebrow">FAQ</p><h2>Trenchless sewer repair questions</h2></div>
  {faq}
</div></section>

<section class="sec dark"><div class="wrap">
  <div class="sec-head"><h2>Related services</h2><p>Camera inspection and hydro jetting are part of every lining job.</p></div>
  <div class="grid g3 svc-grid">{"".join(service_card(s) for s in SERVICES[1:4])}</div>
</div></section>
'''
    return layout("/trenchless/", T["seo_title"], T["desc"], body, "/trenchless/", extra_head=head)

def about():
    body = page_hero("About Ray Rooter Trenchless", "A licensed sewer and water line contractor based in Midland Park, NJ.") + f'''
<section class="sec"><div class="wrap split">
  <div class="prose">
    <p>Ray Rooter Trenchless repairs and replaces sewer and water lines using trenchless methods, along with high pressure hydro jetting and HD sewer camera inspections. Owner Steven Ray, a Licensed Master Plumber with more than 15 years of experience on residential and commercial jobs, is on every job site.</p>
    <p>Estimates are based on a camera inspection, and you get the price before any work starts. We are licensed and insured.</p>
    <ul class="checks"><li>Owner &amp; Licensed Master Plumber on every job site</li><li>Licensed &amp; insured</li><li>Free estimates</li><li>Camera footage before and after</li><li>Locally owned and operated in {SITE["base_town"]}</li></ul>
  </div>
  <div class="photo"><img src="{IMAGES["trailer_2"]}" alt="Ray Rooter pipe lining trailer in a residential driveway" loading="lazy"></div>
</div></section>
{reviews_block(3)}'''
    return layout("/about-us/", "About Ray Rooter Trenchless | Sewer & Water Line Contractor in North NJ",
                  "Licensed, insured trenchless sewer and water line contractor. Owner and Licensed Master Plumber Steven Ray is on every job. Based in Midland Park, NJ.", body, "/about-us/")

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
  <p><strong>{SITE["hours"]}.</strong> Serving {SITE["area_line"]} from {SITE["base_town"]}.</p>
</div></section>'''
    return layout(path, "Contact Ray Rooter Trenchless | Free Sewer Line Estimate",
                  f"Call {SITE['phone']} for a free estimate on trenchless sewer repair, hydro jetting, or sewer camera inspection. {SITE['hours']}.", body, "/contact-us/", canonical="/contact-us/")

def reviews_page():
    cards = "".join(review_card(r, clamp=False) for r in REVIEWS)
    body = page_hero("Customer Reviews", f"Rated {SITE['rating']} stars from {SITE['review_count']} Google reviews.") + f'''
<section class="sec"><div class="wrap">{rating_summary()}<div class="masonry">{cards}</div>
<p class="center small-note">Reviews shown as posted on our Google Business Profile.</p></div></section>'''
    return layout("/clients-one/", "Customer Reviews | Ray Rooter Trenchless",
                  f"Read {SITE['review_count']} Google reviews from North Jersey homeowners who used Ray Rooter Trenchless for sewer repair, pipelining, jetting, and camera inspections.", body, "/clients-one/")

def gallery():
    imgs = "".join(f'<img src="{u}" alt="{e(a)}" loading="lazy">' for u, a in IMAGES["gallery"])
    body = page_hero("Project Gallery", "A look at our trenchless and sewer work.") + f'<section class="sec"><div class="wrap gallery">{imgs}</div></section>'
    return layout("/gallery/", "Project Gallery | Ray Rooter Trenchless", "Photos of trenchless sewer repair, hydro jetting, and camera inspection projects in North NJ.", body)

def not_found():
    body = page_hero("Page not found", "That page has moved. Here's where to go next.") + f'<section class="sec"><div class="wrap grid g3 svc-grid">{"".join(service_card(s) for s in SERVICES[:3])}</div></section>'
    return layout("/404.html", "Page not found | Ray Rooter Trenchless", "This page has moved. Find trenchless sewer repair, hydro jetting, and camera inspection services from Ray Rooter Trenchless.", body, noindex=True)

def county_page(c):
    towns = "".join(f'<li>{e(t)}</li>' for t in c["towns"])
    pages = c.get("city_pages") or ([(c["city_page"], "this area")] if c.get("city_page") else [])
    extra = ("<p>See also: " + ", ".join(f'<a href="{u}">trenchless sewer repair in {e(n)}</a>' for u, n in pages) + ".</p>") if pages else ""
    blocks = [("p", c["intro"]), ("p", c["local"]),
              ("h2", f"Trenchless services in {c['name']}"),
              ("ul", ["Trenchless sewer line repair and pipelining (CIPP)", "High pressure hydro jetting and root removal",
                      "Sewer camera inspections, including pre-purchase inspections", "Trenchless water line replacement",
                      "Main sewer line cleaning"])]
    st = c.get("state", "NJ")
    body = page_hero(f"Trenchless Sewer Repair in {c['name']}, {st}", "Sewer and water lines fixed without digging up your property.", '<a href="/service-areas/">Service Areas</a>') + f'''
<section class="sec"><div class="wrap content-grid"><article class="prose">{render_body(blocks)}
<h2>{c.get("place_label", "Towns")} we serve in {e(c["name"])}</h2><ul class="towns">{towns}</ul>
<p>{"Call " + SITE["phone"] + " with your address and we'll confirm." if c.get("state") == "NY" else "Don't see your town? If it's in " + e(c["name"]) + ", we cover it. Call " + SITE["phone"] + "."}</p>{extra}</article>{aside()}</div></section>
{reviews_block(3)}'''
    return layout(f"/service-areas/{c['slug']}/", f"Trenchless Sewer Repair in {c['name']}, {st} | Ray Rooter Trenchless",
                  f"No-dig sewer repair, pipe lining, hydro jetting, and camera inspections in {c['name']}, {st}: {', '.join(c['towns'][:3])}, and more. Free estimates.", body, "/service-areas/")

def areas_index():
    cards = "".join(f'''<a class="card svc" href="/service-areas/{c["slug"]}/"><h3>{e(c["name"])}</h3><p>{e(", ".join(c["towns"][:6]))}, and more.</p><span class="more">See towns &rarr;</span></a>''' for c in COUNTIES)
    city = "".join(f'<a class="chip" href="{c["path"]}">{e(c["city"])}</a>' for c in CITIES)
    body = page_hero("Service Areas", "Trenchless sewer and water line service across northern New Jersey.") + f'''
<section class="sec dark"><div class="wrap"><div class="grid g3 svc-grid">{cards}</div>
<div class="sec-head" style="margin-top:3rem"><h2>Local pages</h2></div><p class="chips center">{city}</p></div></section>'''
    return layout("/service-areas/", "Service Areas in Northern New Jersey | Ray Rooter Trenchless",
                  "Trenchless sewer repair, hydro jetting, and camera inspections across Bergen, Essex, Hudson, Morris, Passaic, and Sussex County, NJ.", body, "/service-areas/")

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
    shutil.copy(ROOT / "src" / "img" / "favicon.ico", OUT / "favicon.ico")
    pages = [write("/", home())]
    for p in ("/services/", "/all-services/"):
        pages.append(write(p, services_index(p)))
    for s in SERVICES:
        pages.append(write(s["path"], service_page(s)))
    for c in CITIES:
        pages.append(write(c["path"], city_page(c)))
    pages.append(write("/trenchless/", trenchless_page()))
    pages.append(write("/service-areas/", areas_index()))
    for c in COUNTIES:
        pages.append(write(f"/service-areas/{c['slug']}/", county_page(c)))
    pages.append(write("/about-us/", about()))
    for p in ("/contact-us/", "/get-appointment/"):
        pages.append(write(p, contact(p)))
    pages.append(write("/clients-one/", reviews_page()))
    pages.append(write("/gallery/", gallery()))
    write("/404.html", not_found())
    urls = "".join(f"<url><loc>{SITE['domain']}{p}</loc></url>" for p in pages if p not in ("/get-appointment/", "/all-services/", "/services/pipelining/"))
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE['domain']}/sitemap.xml\n")
    print(f"Built {len(pages)} pages into {OUT}")

if __name__ == "__main__":
    main()
