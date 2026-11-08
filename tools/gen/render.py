#!/usr/bin/env python3
"""Render the PCW concept site from extracted content.

Design: document-grade engineering practice. Type, rules and captioned plates.
Output: /root/pcw-services-concept (45 routes). Source repo is never written.
"""
import json
from pathlib import Path
from posixpath import dirname, normpath

ROOT = Path('/root/pcw-services-concept')
DATA = json.loads((ROOT / 'tools/gen/content.json').read_text())

BASE = 'https://callmat3ai-cloud.github.io/pcw-services-concept/'
PHONE = '(949) 548-9969'
TEL = '+1' + '949' + '548' + '9969'
EMAIL = 'Customerservice@pcwservices.com'
ADDRESS = '981 W. 18th Street, Costa Mesa, CA 92627'
LICENSE = '#699611'

# ---------------------------------------------------------------- helpers


def split_title(title):
    """'Base // Accent' -> (base, accent)."""
    if ' // ' in title:
        base, accent = title.split(' // ', 1)
        return base.strip(), accent.strip()
    return title.strip(), ''


def esc(text):
    return (str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def attr(text):
    return esc(text).replace('"', '&quot;')


def norm(href, base_dir=''):
    """Resolve a source-relative href to a root-relative path (or #fragment)."""
    href = (href or '').strip()
    if not href or href.startswith(('http://', 'https://', 'mailto:', 'tel:', '#')):
        return href
    joined = normpath(('/' + base_dir.strip('/') + '/' + href).replace('//', '/'))
    joined = joined.lstrip('/')
    if joined in ('', '.'):
        return ''
    return joined


def url(href, depth):
    """Prefix a root-relative href for a page at `depth`."""
    if not href or href.startswith(('#', 'http', 'mailto:', 'tel:')):
        return href
    prefix = '../' * depth
    if href.endswith('/'):
        return prefix + href
    return prefix + href


def svc_anchor(href, base_dir=''):
    """Service page link from a card/modal href."""
    return norm(href, base_dir)


# ---------------------------------------------------------------- chrome

def head(title, description, depth, canonical, extra_css=''):
    p = '../' * depth
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{attr(description)}">
<meta name="robots" content="noindex, nofollow">
<meta name="pcw-preview" content="document-grade-concept-v2">
<link rel="canonical" href="{BASE}{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{attr(title)}">
<meta property="og:description" content="{attr(description)}">
<meta property="og:url" content="{BASE}{canonical}">
<meta property="og:image" content="{BASE}assets/images/pcw_hero.png">
<meta property="og:site_name" content="PCW Contracting Services">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{p}assets/images/PCW-logo-white.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{p}assets/css/site.css">{extra_css}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""


def utility(depth):
    return f"""<div class="utility">
  <div class="wrap utility__in">
    <div class="utility__left">Licensed California contractor {LICENSE} &nbsp;·&nbsp; Costa Mesa, California</div>
    <div class="utility__right">
      <a href="mailto:{EMAIL}">{EMAIL}</a>
      <span>Since 1989</span>
    </div>
  </div>
</div>
"""


def header(depth, active=''):
    nav = DATA['nav']
    items = []
    for item in nav:
        href = url(norm(item['href'], ''), depth)
        label = esc(item['label'])
        if item['children']:
            links = []
            for ch in item['children']:
                links.append(
                    f'<a class="item" href="{url(norm(ch["href"], ""), depth)}">{esc(ch["label"])}</a>')
            half = (len(links) + 1) // 2
            cols = (f'<div class="mega__cols"><div>{"".join(links[:half])}</div>'
                    f'<div>{"".join(links[half:])}</div></div>')
            note = esc(item['children'][0]['note']) if item['children'] else ''
            mega_cls = 'mega mega--sm' if len(item['children']) <= 3 else 'mega'
            title = 'Knowledge Hub' if label == 'Resources' else f'{label}'
            items.append(f"""<div class="nav__item">
  <a class="nav__link" href="{href}" aria-haspopup="true">{label}
    <svg viewBox="0 0 12 12" fill="none" aria-hidden="true"><path d="M2 4.5 6 8.5l4-4" stroke="currentColor" stroke-width="1.4"/></svg>
  </a>
  <div class="{mega_cls}">
    <div class="mega__head">
      <div><span class="mega__title">{title}</span><br><span class="mega__note">{note}</span></div>
      <a class="mega__all" href="{href}">All {esc(item['label'].split()[0].lower())} services</a>
    </div>
    {cols}
  </div>
</div>""")
        else:
            cls = 'nav__link' + (' is-active' if active == item['label'] else '')
            items.append(f'<div class="nav__item"><a class="{cls}" href="{href}">{label}</a></div>')

    drawer_groups = []
    for item in nav:
        links = ' '.join(f'<a href="{url(norm(c["href"], ""), depth)}">{esc(c["label"])}</a>' for c in item['children'])
        if links:
            drawer_groups.append(f'<div class="drawer__group"><span>{esc(item["label"])}</span>'
                                 f'<a href="{url(norm(item["href"], ""), depth)}">Overview</a>{links}</div>')
        else:
            drawer_groups.append(f'<div class="drawer__group"><span>Company</span>'
                                 f'<a href="{url(norm(item["href"], ""), depth)}">{esc(item["label"])}</a></div>')

    return f"""{utility(depth)}<header class="site-header">
  <div class="wrap header__in">
    <a class="brand" href="{url('', depth) or './'}" aria-label="PCW Contracting Services home">
      <img src="{ '../' * depth }assets/images/PCW-logo-white.png" alt="PCW Contracting Services" width="158" height="52">
    </a>
    <nav class="nav" aria-label="Main">
      {''.join(items)}
    </nav>
    <div class="header__actions">
      <a class="header__phone" href="tel:{TEL}">{PHONE}</a>
      <a class="btn btn--ghost" href="{url('contact/', depth)}">Request an estimate</a>
      <button class="burger" type="button" data-drawer-open aria-controls="drawer" aria-expanded="false" aria-label="Open menu"><span></span></button>
    </div>
  </div>
</header>
<div class="drawer" id="drawer" data-open="false" aria-hidden="true">
  <div class="drawer__top">
    <img src="{ '../' * depth }assets/images/PCW-logo-white.png" alt="PCW Contracting Services" width="120" height="40">
    <button class="drawer__close" type="button" data-drawer-close aria-label="Close menu">&times;</button>
  </div>
  {''.join(drawer_groups)}
  <div class="drawer__cta">
    <a class="btn" href="tel:{TEL}">Call {PHONE}</a>
    <a class="btn btn--ghost" href="{url('contact/', depth)}">Request an estimate</a>
  </div>
</div>
"""


def footer(depth):
    project = [c for c in DATA['nav'] if 'Project' in c['label']][0]['children'][:6]
    prop = [c for c in DATA['nav'] if 'Property' in c['label']][0]['children'][:6]
    pl = ''.join(f'<a href="{url(norm(c["href"], ""), depth)}">{esc(c["label"])}</a>' for c in project)
    ql = ''.join(f'<a href="{url(norm(c["href"], ""), depth)}">{esc(c["label"])}</a>' for c in prop)
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer__top">
      <div class="footer__brand">
        <img src="{ '../' * depth }assets/images/PCW-logo-dark.png" alt="PCW Contracting Services" width="150" height="49">
        <p>General contracting and specialized construction services for Southern California HOAs and commercial properties since 1989.</p>
      </div>
      <div class="footer__col">
        <h4>Project services</h4>
        {pl}
        <a href="{url('project-services/', depth)}">All project services</a>
      </div>
      <div class="footer__col">
        <h4>Property services</h4>
        {ql}
        <a href="{url('property-services/', depth)}">All property services</a>
      </div>
      <div class="footer__col">
        <h4>Company</h4>
        <a href="{url('about/', depth)}">About PCW</a>
        <a href="{url('our-work/', depth)}">Our work</a>
        <a href="{url('testimonials/', depth)}">Testimonials</a>
        <a href="{url('knowledge-hub/', depth)}">Knowledge Hub</a>
        <a href="{url('contact/', depth)}">Contact</a>
      </div>
    </div>
    <div class="footer__bottom">
      <span>PCW Contracting Services, Inc.</span>
      <span>CSLB {LICENSE} &nbsp; B, C39, C53, C27</span>
      <span>{ADDRESS}</span>
      <span><a href="tel:{TEL}">{PHONE}</a></span>
      <span>Concept preview. Not the live site.</span>
    </div>
  </div>
</footer>
<script src="{ '../' * depth }assets/js/main.js" defer></script>
<script src="{ '../' * depth }assets/js/site.js" defer></script>
"""


# ---------------------------------------------------------------- components

def spec_row(name, tagline, quote_href, page_href, depth, num='', quote_label='Quote'):
    page = url(page_href, depth)
    q = url(quote_href, depth)
    if page:
        name_html = f'<a class="spec__name" href="{page}">{esc(name)}</a>'
    else:
        name_html = f'<span class="spec__name">{esc(name)}</span>'
    action = f'<a class="chip" href="{q}">{quote_label}</a>' if q else ''
    return f"""<div class="spec__row">
      <div class="num">{esc(num)}</div>
      <div>{name_html}</div>
      <div class="spec__tag">{esc(tagline)}</div>
      <div class="spec__act">{action}</div>
    </div>"""


def cards_to_rows(cards, base_dir, depth):
    rows = []
    for i, c in enumerate(cards, 1):
        quote = next((l['href'] for l in c['links'] if l['href'].startswith('#')), '')
        page = next((l['href'] for l in c['links'] if not l['href'].startswith('#')), '')
        rows.append(spec_row(c['name'], c['tagline'], norm(quote, base_dir), norm(page, base_dir), depth, num=f'{i:02d}'))
    return ''.join(rows)


def rows_with_disclosure(cards, base_dir, depth, visible=8, more_label='Show all'):
    rows = []
    for i, c in enumerate(cards, 1):
        quote = next((l['href'] for l in c['links'] if l['href'].startswith('#')), '')
        page = next((l['href'] for l in c['links'] if not l['href'].startswith('#')), '')
        rows.append(spec_row(c['name'], c['tagline'], norm(quote, base_dir), norm(page, base_dir), depth, num=f'{i:02d}'))
    head = ('<div class="spec__head"><span></span><span>Service</span><span>Scope</span>'
            '<span style="text-align:right">Estimate</span></div>')
    if len(rows) <= visible:
        return head + ''.join(rows)
    first = ''.join(rows[:visible])
    rest = ''.join(rows[visible:])
    return (head + first +
            f'<details class="disclose"><summary>{esc(more_label)} — {len(rows)} in total</summary>{rest}</details>')


def modal(mod_id, m, base_dir, depth):
    bullets = ''.join(
        f'<li><span><strong>{esc(b["term"])}</strong> {esc(b["body"])}</span></li>'
        for b in m['bullets'])
    actions = []
    for a in m['actions']:
        href = norm(a['href'], base_dir)
        cls = 'btn' if 'primary' in a.get('class', '') else 'btn btn--ghost'
        actions.append(f'<a class="{cls}" href="{url(href, depth)}">{esc(a["label"])}</a>')
    return f"""<div class="modal" id="{attr(mod_id)}" role="dialog" aria-modal="true" aria-labelledby="{attr(mod_id)}-t">
  <div class="modal__card">
    <a class="modal__close" href="#" aria-label="Close">&times;</a>
    <p class="modal__label">{esc('Service detail')}</p>
    <h3 id="{attr(mod_id)}-t">{esc(m['title'])}</h3>
    <p class="modal__tag">{esc(m['tagline'])}</p>
    <ul class="modal__bullets">{bullets}</ul>
    <div class="modal__actions">{''.join(actions)}</div>
  </div>
</div>"""


def ledger(home):
    stats = ''.join(
        f'<div class="stat"><span class="stat__value">{esc(t["value"])}</span>'
        f'<span class="stat__label">{esc(t["label"])}</span></div>'
        for t in home['hero']['trust'])
    return f'<section class="ledger"><div class="wrap"><div class="ledger__grid">{stats}</div></div></section>'


def ctastrip(depth, heading='Schedule a property walkthrough', body='Speak with our technical estimators about an upcoming RFP, property assessment, or maintenance review.'):
    return f"""<section class="ctastrip">
  <div class="wrap ctastrip__in">
    <div>
      <h2>{esc(heading)}</h2>
      <p>{esc(body)}</p>
    </div>
    <div class="ctastrip__actions">
      <a class="btn" href="{url('contact/', depth)}">Request an estimate</a>
      <a class="btn btn--ghost" href="tel:{TEL}">{PHONE}</a>
    </div>
  </div>
</section>"""


def form_block(depth, fields, compact=False):
    """Render the approved estimate form, preserving ids and handler."""
    parts = []
    for f in fields:
        fid = f.get('id', '')
        label = f.get('label') or f.get('placeholder') or fid
        req = ' required' if f.get('required') else ''
        wide = ' field--wide' if f['tag'] == 'textarea' else ''
        if f['tag'] == 'select':
            opts = ''.join(f'<option>{esc(o)}</option>' for o in f.get('options', []))
            control = f'<select id="{fid}" name="{fid}"{req}>{opts}</select>'
        elif f['tag'] == 'textarea':
            control = (f'<textarea id="{fid}" name="{fid}" rows="4" placeholder="{attr(f.get("placeholder", ""))}"{req}></textarea>')
        else:
            control = (f'<input id="{fid}" name="{fid}" type="{f.get("type") or "text"}" '
                       f'placeholder="{attr(f.get("placeholder", ""))}"{req}>')
        parts.append(f'<div class="field{wide}"><label for="{fid}">{esc(label)}</label>{control}</div>')

    return f"""<form id="pcw-contact-form" class="formcard" onsubmit="handleFormSubmit(event)">
  <h3>Request an estimate</h3>
  <p>HOA or property name, contact details, gate codes and the work request. A PCW estimator follows up within 24 business hours.</p>
  <div class="formgrid">{''.join(parts)}</div>
  <div class="formfoot">
    <button class="btn" type="submit">Submit estimate request</button>
    <small>Prefer to talk? <a href="tel:{TEL}">{PHONE}</a></small>
  </div>
</form>
<div class="toast" id="success-toast" role="status" aria-live="polite">Thank you. Your estimate request has been received.</div>"""


# ---------------------------------------------------------------- pages

def page_home():
    h = DATA['home']
    hero = h['hero']
    title, accent = hero['title'], hero['title_accent']
    lead_title = title.replace(accent, '').strip().rstrip('.').strip() if accent else title
    project_rows = rows_with_disclosure(h['project_cards'], '', 0, visible=8,
                                        more_label='All project services')
    property_rows = rows_with_disclosure(h['property_cards'], '', 0, visible=8,
                                         more_label='All property services')
    modals = ''.join(modal(mid, m, '', 0) for mid, m in h['modals'].items())

    contents = [
        ('01', 'Project services', '20 disciplines', 'project-services/'),
        ('02', 'Property services', '16 disciplines', 'property-services/'),
        ('03', 'About PCW', '12 reasons', 'about/'),
        ('04', 'Our work', 'Projects and repairs', 'our-work/'),
        ('05', 'Testimonials', 'Seven client references', 'testimonials/'),
        ('06', 'Knowledge Hub', '30 resource topics', 'knowledge-hub/'),
        ('07', 'Contact', 'Estimate requests', 'contact/'),
    ]
    contents_rows = ''.join(
        f'<a href="{url(norm(href, ""), 0)}"><span class="n">{n}</span>'
        f'<span class="t">{esc(t)}<span class="c">{esc(c)}</span></span></a>'
        for n, t, c, href in contents)

    reasons = DATA['about']['reasons'][:4]
    principles = ''.join(
        f'<div class="principle"><span class="n">{esc(r["n"])}</span><div>'
        f'<h3>{esc(r["title"])}</h3><p>{esc(r["body"])}</p></div></div>' for r in reasons)

    reviews = h['testimonials']
    lead_review = reviews[0]
    other_reviews = ''.join(
        f'<article><blockquote>{esc(r["quote"])}</blockquote>'
        f'<p><strong>{esc(r["name"])}</strong><br>{esc(r["title"])}</p></article>'
        for r in reviews[1:])

    caps = DATA['home'].get('capabilities', {})
    cap_cards = ''.join(
        f'<article class="workcard"><h3>{esc(c["title"])}</h3><p>{esc(c["body"])}</p></article>'
        for c in caps.get('cards', []))

    hub_cards = ''.join(
        f'<a href="{url(norm(c["href"], ""), 0)}" style="display:grid;grid-template-columns:44px minmax(0,1fr) minmax(0,1.1fr);gap:24px;align-items:baseline;padding:16px 0;border-bottom:1px solid var(--line)">'
        f'<span class="n">{i:02d}</span><span class="rt" style="font:500 var(--step-1)/1.3 var(--sans)">{esc(c["title"])}</span>'
        f'<span class="rb" style="font-size:var(--step--1);color:var(--muted)">{esc(c["body"])[:150]}</span></a>'
        for i, c in enumerate(h['hub']['cards'], 1))

    fields = h['contact']['fields']

    return head(
        'PCW Contracting Services — General contracting for HOA and commercial properties',
        'PCW Contracting Services: general contracting, building-envelope repair, concrete, waterproofing and property maintenance for Southern California HOAs and commercial properties since 1989.',
        0, '',
    ) + header(0, active='') + f"""<main id="main">

<section class="cover">
  <div class="cover__panel">
    <div>
      <p class="cover__mark">Licensed general contractor in Costa Mesa, California since 1989</p>
      <h1><em>{esc(lead_title)}.</em><span>{esc(accent or 'Proven results.')}</span></h1>
      <p class="cover__lead">{esc(hero['lead'])} {esc(hero['subtitle'])}.</p>
      <div class="cover__actions">
        <a class="btn btn--amber" href="{url('contact/', 0)}">Request an estimate</a>
        <a class="linkline" href="{url('our-work/', 0)}">Recent projects</a>
      </div>
    </div>
    <dl class="cover__proof">
      {''.join(f'<div><dt>{esc(t["label"])}</dt><dd>{esc(t["value"])}</dd></div>' for t in hero['trust'])}
    </dl>
  </div>
  <figure class="cover__media">
    <img src="assets/images/pcw_hero.png" alt="PCW crew working on an occupied multi-storey concrete building" width="1024" height="1024" fetchpriority="high">
    <figcaption><span>Building envelope reconstruction on an occupied community</span><span>Project services</span></figcaption>
  </figure>
</section>

<section class="contents">
  <div class="wrap contents__grid">
    <div class="contents__head">
      <p class="eyebrow">Contents</p>
      <h2>Everything PCW does, in one document.</h2>
      <p style="font-size:var(--step--1);color:var(--muted)">Thirty-six licensed service classifications across two divisions, with technical scope, project experience and direct estimator contact.</p>
    </div>
    <div class="contents__list">{contents_rows}</div>
  </div>
</section>

<section class="chapter" id="project-services">
  <div class="wrap chapter__grid">
    <aside class="chapter__aside"><span class="n">01</span><span class="k">Project services</span></aside>
    <div>
      <div class="chapter__head">
        <h2>Major reconstruction, handled as one accountable scope.</h2>
        <p class="lead">{esc(h.get('project_lead', '').replace('Comprehensive Project Service Directory — ', ''))}</p>
      </div>
      <div class="spec">{project_rows}</div>
      <p style="margin-top:var(--s4)"><a class="linkline" href="{url('project-services/', 0)}">All project services and technical scope</a></p>
    </div>
  </div>
</section>

<section class="chapter chapter--dark" id="property-services">
  <div class="wrap chapter__grid">
    <aside class="chapter__aside"><span class="n">02</span><span class="k">Property services</span></aside>
    <div>
      <div class="chapter__head">
        <h2>Repair and maintenance for the work that never stops.</h2>
        <p class="lead" style="color:var(--on-dark-soft)">{esc(h.get('property_lead', '').replace('Comprehensive Property Service Directory — ', ''))}</p>
      </div>
      <div class="spec">{property_rows}</div>
      <p style="margin-top:var(--s4)"><a class="linkline" href="{url('property-services/', 0)}" style="color:var(--amber)">All property services and response times</a></p>
    </div>
  </div>
</section>

<section class="chapter chapter--ground" id="approach">
  <div class="wrap chapter__grid">
    <aside class="chapter__aside"><span class="n">03</span><span class="k">Approach</span></aside>
    <div>
      <div class="chapter__head">
        <h2>Boards hire us for judgement, not just crews.</h2>
        <p class="lead">{esc(DATA['home'].get('proof', {}).get('paragraphs', [''])[0])}</p>
      </div>
      <div class="principles">{principles}</div>
      <p style="margin-top:var(--s4)"><a class="linkline" href="{url('about/', 0)}">The twelve reasons boards choose PCW</a></p>
    </div>
  </div>
</section>

<section class="chapter" id="work">
  <div class="wrap chapter__grid">
    <aside class="chapter__aside"><span class="n">04</span><span class="k">Our work</span></aside>
    <div>
      <div class="chapter__head">
        <h2>{esc(caps.get('heading', 'Completed projects').replace(' // ', '. '))}</h2>
        <p class="lead">Recent repair and reconstruction experience across occupied communities, campuses and commercial assets.</p>
      </div>
      <div class="workgrid">
        <article class="workcard">
          <img src="assets/images/pcw_concrete.png" alt="Concrete and structural repair work" width="1024" height="1024" loading="lazy">
          <h3>{esc(caps.get('cards', [{}])[0].get('title', ''))}</h3>
          <p>{esc(caps.get('cards', [{}])[0].get('body', ''))}</p>
        </article>
        <article class="workcard">
          <img src="assets/images/pcw_decking.png" alt="Deck and waterproofing restoration" width="1024" height="1024" loading="lazy">
          <h3>{esc(caps.get('cards', [{}, {}])[1].get('title', ''))}</h3>
          <p>{esc(caps.get('cards', [{}, {}])[1].get('body', ''))}</p>
        </article>
      </div>
      <p style="margin-top:var(--s4)"><a class="linkline" href="{url('our-work/', 0)}">Full project and repair index</a></p>
    </div>
  </div>
</section>

<section class="chapter chapter--ground" id="testimonials">
  <div class="wrap chapter__grid">
    <aside class="chapter__aside"><span class="n">05</span><span class="k">Client references</span></aside>
    <div>
      <div class="chapter__head"><h2>What managers and boards say.</h2></div>
      <div class="quotes">
        <div class="quote quote--lead">
          <blockquote>{esc(lead_review['quote'])}</blockquote>
          <cite>{esc(lead_review['name'])}<span>{esc(lead_review['title'])} · {esc(lead_review['category'])}</span></cite>
        </div>
        <div class="quotelist">{other_reviews}</div>
      </div>
      <p style="margin-top:var(--s5)"><a class="linkline" href="{url('testimonials/', 0)}">All seven references</a></p>
    </div>
  </div>
</section>

<section class="chapter" id="resources">
  <div class="wrap chapter__grid">
    <aside class="chapter__aside"><span class="n">06</span><span class="k">Knowledge Hub</span></aside>
    <div>
      <div class="chapter__head">
        <h2>Practical guides for boards and property managers.</h2>
        <p class="lead">{esc(h['hub']['paragraphs'][0] if h['hub'].get('paragraphs') else '')}</p>
      </div>
      <div style="border-top:1px solid var(--line-strong)">{hub_cards}</div>
      <p style="margin-top:var(--s4)"><a class="linkline" href="{url('knowledge-hub/', 0)}">All thirty resource topics</a></p>
    </div>
  </div>
</section>

<section class="contact" id="contact">
  <div class="wrap contact__grid">
    <div>
      <p class="eyebrow label--dark">07 — Contact</p>
      <h2>Let’s discuss your property.</h2>
      <p>{esc(h['contact']['paragraphs'][0] if h['contact'].get('paragraphs') else '')}</p>
      <div class="contact__details">
        <div><span class="k">Office</span><span>{ADDRESS}</span></div>
        <div><span class="k">Phone</span><a href="tel:{TEL}">{PHONE}</a></div>
        <div><span class="k">Email</span><a href="mailto:{EMAIL}">{EMAIL}</a></div>
      </div>
    </div>
    {form_block(0, fields)}
  </div>
</section>

</main>
{footer(0)}
{modals}
</body>
</html>
"""


def page_division(key):
    d = DATA['divisions'][key]
    idx = d['index']
    title = idx['title']
    accent = ''
    if ' // ' in title:
        base, accent = title.split(' // ', 1)
    else:
        base = title
    rows = ('<div class="spec__head"><span></span><span>Service</span><span>Scope</span>'
            '<span style="text-align:right">Estimate</span></div>' + cards_to_rows(idx['cards'], '', 1))
    modals = ''.join(modal(mid, m, key and ('project-services/' if key == 'project' else 'property-services/'), 1)
                     for mid, m in idx['modals'].items())
    paras = ''.join(f'<p>{esc(p)}</p>' for p in idx['lead_paragraphs'])
    return head(
        f'{base} — PCW Contracting Services',
        idx['lead'], 1, ('project-services/' if key == 'project' else 'property-services/') + 'index.html'
    ) + header(1, active=base.split()[0] if base else '') + f"""<main id="main">
<section class="pagehead">
  <div class="wrap pagehead__grid">
    <div>
      <p class="crumbs"><a href="./" >Home</a><span>/</span><span>{esc(base)}</span></p>
      <h1>{esc(base)}</h1>
      {f'<p class="pagehead__tag">{esc(accent)}</p>' if accent else ''}
      <p class="pagehead__lead">{esc(idx['lead'])}</p>
    </div>
    <figure class="pagehead__figure">
      <img src="../assets/images/{'pcw_concrete.png' if key == 'property' else 'pcw_decking.png'}" alt="PCW {base.lower()} work" width="1024" height="1024" loading="lazy">
    </figure>
  </div>
</section>

<section class="chapter">
  <div class="wrap chapter__grid">
    <aside class="chapter__aside"><span class="n">{'01' if key == 'project' else '02'}</span><span class="k">{esc(base)}</span></aside>
    <div>
      <div class="chapter__head">
        <h2>{esc(str(len(idx['cards'])))} licensed classifications.</h2>
        <p class="lead">{paras}</p>
      </div>
      <div class="spec">{rows}</div>
    </div>
  </div>
</section>

{ctastrip(1)}
</main>
{footer(1)}
{modals}
</body>
</html>
"""


def page_service(svc):
    depth = 2
    rel = svc['path'].replace('index.html', '')
    crumbs = ''.join(
        f'<a href="{url(norm(p, rel), depth)}">{esc(t)}</a><span>/</span>'
        for t, p in zip(svc['crumbs'][:-1] or ['Home'], ['', 'project-services/' if svc['division'] == 'Project Services' else 'property-services/'])
    )

    body = []
    for block in svc['body']:
        if block['type'] == 'h2':
            body.append(f'<h2>{esc(block["text"])}</h2>')
        elif block['type'] == 'p':
            body.append(f'<p>{esc(block["text"])}</p>')
        elif block['type'] == 'list':
            items = ''.join(
                f'<li><dt>{esc(i["term"])}</dt><dd>{esc(i["body"])}</dd></li>' for i in block['items'])
            body.append(f'<dl class="deflist">{items}</dl>')

    facts = ''.join(
        f'<div><dt>{esc(f["label"])}</dt><dd>{esc(f["value"])}</dd></div>' for f in svc['facts'])
    related = ''.join(
        f'<li><a href="{url(norm(r["href"], rel), depth)}">{esc(r["label"])}</a></li>' for r in svc['related'])

    title = svc['title']
    return head(
        f'{title} — PCW Contracting Services',
        svc['lead'] or f'{title} services from PCW Contracting Services.',
        depth, rel + 'index.html'
    ) + header(depth, active=svc['division'].split()[0]) + f"""<main id="main">
<section class="pagehead">
  <div class="wrap pagehead__grid">
    <div>
      <p class="crumbs">{crumbs}<span>{esc(title)}</span></p>
      <h1>{esc(title)}</h1>
      {f'<p class="pagehead__tag">{esc(svc["tagline"])}</p>' if svc['tagline'] else ''}
      <p class="pagehead__lead">{esc(svc['lead'])}</p>
    </div>
    <figure class="pagehead__figure">
      <img src="{ '../' * depth }assets/images/{'pcw_decking.png' if any(k in rel for k in ('deck', 'water', 'roof', 'planter', 'pool')) else 'pcw_concrete.png'}" alt="PCW {esc(title.lower())} work" width="1024" height="1024" loading="lazy">
    </figure>
  </div>
</section>

<section class="detail">
  <div class="wrap detail__grid">
    <article class="detail__main">
      {''.join(body)}
    </article>
    <aside class="aside">
      <div class="sidecard">
        <h3>Service facts</h3>
        <dl>{facts}</dl>
      </div>
      <div class="sidecard sidecard--dark">
        <h3>Request an estimate</h3>
        <p>Submit your property address and requirements. A PCW technical estimator follows up within 24 business hours.</p>
        <a class="btn btn--onDark" href="{url('contact/', depth)}?service={esc(title)}">Request proposal</a>
        <small>Or call <a href="tel:{TEL}">{PHONE}</a></small>
      </div>
      <div class="sidecard">
        <h3>Related services</h3>
        <ul>{related}</ul>
      </div>
    </aside>
  </div>
</section>

{ctastrip(depth)}
</main>
{footer(depth)}
</body>
</html>
"""


def page_about():
    a = DATA['about']
    title = a['title']
    base, accent = (title.split(' // ', 1) + [''])[:2]
    reasons = ''.join(
        f'<div class="principle"><span class="n">{esc(r["n"])}</span><div>'
        f'<h3>{esc(r["title"])}</h3><p>{esc(r["body"])}</p></div></div>' for r in a['reasons'])
    return head(f'{base} — PCW Contracting Services', a['lead'], 1, 'about/index.html') + header(1, active='About') + f"""<main id="main">
<section class="pagehead">
  <div class="wrap pagehead__grid">
    <div>
      <p class="crumbs"><a href="../">Home</a><span>/</span><span>About</span></p>
      <h1>{esc(base)}</h1>
      {f'<p class="pagehead__tag">{esc(accent)}</p>' if accent else ''}
      <p class="pagehead__lead">{esc(a['lead'])}</p>
    </div>
    <figure class="pagehead__figure">
      <img src="../assets/images/pcw_decking.png" alt="PCW restoration work on an occupied property" width="1024" height="1024" loading="lazy">
    </figure>
  </div>
</section>

<section class="chapter">
  <div class="wrap chapter__grid">
    <aside class="chapter__aside"><span class="n">01</span><span class="k">Why boards choose PCW</span></aside>
    <div>
      <div class="chapter__head"><h2>{esc(a['heading'] or 'The twelve reasons boards choose PCW')}</h2></div>
      <div class="principles">{reasons}</div>
    </div>
  </div>
</section>

{ctastrip(1)}
</main>
{footer(1)}
</body>
</html>
"""


def page_work():
    w = DATA['work']
    base, accent = (w['title'].split(' // ', 1) + [''])[:2]
    rows = ''.join(
        f'<div class="projectlist__row"><span class="n">{i:02d}</span>'
        f'<span class="t">{esc(p["name"])}</span><span class="c">{esc(p["category"])}</span></div>'
        for i, p in enumerate(w['projects'], 1))
    return head(f'{base} — PCW Contracting Services', w['lead'], 1, 'our-work/index.html') + header(1, active='Our Work') + f"""<main id="main">
<section class="pagehead">
  <div class="wrap pagehead__grid">
    <div>
      <p class="crumbs"><a href="../">Home</a><span>/</span><span>Our work</span></p>
      <h1>{esc(base)}</h1>
      {f'<p class="pagehead__tag">{esc(accent)}</p>' if accent else ''}
      <p class="pagehead__lead">{esc(w['lead'] or w['intro'])}</p>
    </div>
    <figure class="pagehead__figure">
      <img src="../assets/images/pcw_concrete.png" alt="Completed PCW concrete and structural repair project" width="1024" height="1024" loading="lazy">
    </figure>
  </div>
</section>

<section class="chapter">
  <div class="wrap chapter__grid">
    <aside class="chapter__aside"><span class="n">01</span><span class="k">Project index</span></aside>
    <div>
      <div class="chapter__head">
        <h2>{esc(w['heading'] or 'Projects and repairs')}</h2>
        <p class="lead">{esc(w['intro'])}</p>
      </div>
      <div class="projectlist">{rows}</div>
    </div>
  </div>
</section>

{ctastrip(1)}
</main>
{footer(1)}
</body>
</html>
"""


def page_testimonials():
    t = DATA['testimonials']
    reviews = t['reviews']
    lead = reviews[0]
    rest = ''.join(
        f'<article><blockquote>{esc(r["quote"])}</blockquote>'
        f'<p><strong>{esc(r["name"])}</strong><br>{esc(r["title"])} · {esc(r["category"])}</p></article>'
        for r in reviews[1:])
    return head('Client testimonials — PCW Contracting Services', t['lead'], 1, 'testimonials/index.html') + header(1, active='Testimonials') + f"""<main id="main">
<section class="pagehead">
  <div class="wrap pagehead__grid">
    <div>
      <p class="crumbs"><a href="../">Home</a><span>/</span><span>Testimonials</span></p>
      <h1>{esc(t['title'])}</h1>
      <p class="pagehead__lead">{esc(t['lead'])}</p>
    </div>
  </div>
</section>

<section class="chapter">
  <div class="wrap chapter__grid">
    <aside class="chapter__aside"><span class="n">01</span><span class="k">References</span></aside>
    <div>
      <div class="quotes">
        <div class="quote quote--lead">
          <blockquote>{esc(lead['quote'])}</blockquote>
          <cite>{esc(lead['name'])}<span>{esc(lead['title'])} · {esc(lead['category'])}</span></cite>
        </div>
        <div class="quotelist">{rest}</div>
      </div>
    </div>
  </div>
</section>

{ctastrip(1)}
</main>
{footer(1)}
</body>
</html>
"""


def page_hub():
    h = DATA['hub']
    anchor_map = {
        'What a Vendor Needs': 'vendor',
        'Budget Options': 'budget',
        'Building Components': 'components',
        'Concrete Problems': 'concrete',
    }
    topics = ''.join(
        f'<article id="{anchor_map[esc(t["title"])] if t["title"] in anchor_map else ""}">'
        f'<span class="num">{i:02d}</span><h3>{esc(t["title"])}</h3><p>{esc(t["body"])}</p></article>'
        for i, t in enumerate(h['topics'], 1))
    return head('Knowledge Hub — PCW Contracting Services', h['lead'], 1, 'knowledge-hub/index.html') + header(1, active='Resources') + f"""<main id="main">
<section class="pagehead">
  <div class="wrap pagehead__grid">
    <div>
      <p class="crumbs"><a href="../">Home</a><span>/</span><span>Knowledge Hub</span></p>
      <h1>Knowledge Hub</h1>
      <p class="pagehead__lead">{esc(h['lead'])}</p>
    </div>
  </div>
</section>

<section class="chapter">
  <div class="wrap chapter__grid">
    <aside class="chapter__aside"><span class="n">01</span><span class="k">Resource topics</span></aside>
    <div>
      <div class="chapter__head"><h2>{esc(h['heading'] or 'Documented resource topics')}</h2></div>
      <div class="topicgrid">{topics}</div>
    </div>
  </div>
</section>

{ctastrip(1)}
</main>
{footer(1)}
</body>
</html>
"""


def page_elnino():
    e = DATA['elnino']
    base, accent = (e['title'].split(' // ', 1) + [''])[:2]
    guides = ''.join(
        f'<h2>{esc(g["heading"])}</h2><ol class="guide">' + ''.join(f'<li>{esc(i)}</li>' for i in g['items']) + '</ol>'
        for g in e['guides'])
    return head(f'{base} — PCW Contracting Services', e['lead'], 2, 'knowledge-hub/el-nino-prep/index.html') + header(2, active='Resources') + f"""<main id="main">
<section class="pagehead">
  <div class="wrap pagehead__grid">
    <div>
      <p class="crumbs"><a href="../../">Home</a><span>/</span><a href="../">Knowledge Hub</a><span>/</span><span>El Niño prep</span></p>
      <h1>{esc(base)}</h1>
      {f'<p class="pagehead__tag">{esc(accent)}</p>' if accent else ''}
      <p class="pagehead__lead">{esc(e['lead'])}</p>
    </div>
    <figure class="pagehead__figure">
      <img src="../../assets/images/pcw_decking.png" alt="Exterior repair and waterproofing preparation" width="1024" height="1024" loading="lazy">
    </figure>
  </div>
</section>

<section class="chapter">
  <div class="wrap chapter__grid">
    <aside class="chapter__aside"><span class="n">01</span><span class="k">El Niño preparation</span></aside>
    <div class="detail__main">{guides}</div>
  </div>
</section>

{ctastrip(2)}
</main>
{footer(2)}
</body>
</html>
"""


def page_contact():
    c = DATA['contact']
    base, accent = (c['title'].split(' // ', 1) + [''])[:2]
    return head(f'{base} — PCW Contracting Services', c['lead'], 1, 'contact/index.html') + header(1, active='Contact') + f"""<main id="main">
<section class="pagehead">
  <div class="wrap pagehead__grid">
    <div>
      <p class="crumbs"><a href="../">Home</a><span>/</span><span>Contact</span></p>
      <h1>{esc(base)}</h1>
      {f'<p class="pagehead__tag">{esc(accent)}</p>' if accent else ''}
      <p class="pagehead__lead">{esc(c['lead'])}</p>
    </div>
  </div>
</section>

<section class="contact">
  <div class="wrap contact__grid">
    <div>
      <h2>Estimates, scopes and walkthroughs.</h2>
      <p>{esc(c['paragraphs'][0] if c.get('paragraphs') else 'HOA or property name, contact details, gate codes and the work request. A PCW estimator follows up within 24 business hours.')}</p>
      <div class="contact__details">
        <div><span class="k">Office</span><span>{ADDRESS}</span></div>
        <div><span class="k">Phone</span><a href="tel:{TEL}">{PHONE}</a></div>
        <div><span class="k">Email</span><a href="mailto:{EMAIL}">{EMAIL}</a></div>
        <div><span class="k">Llicence</span><span>CSLB {LICENSE} · B, C39, C53, C27</span></div>
      </div>
    </div>
    {form_block(1, c['fields'])}
  </div>
</section>

{ctastrip(1)}
</main>
{footer(1)}
</body>
</html>
"""


def main():
    (ROOT / 'index.html').write_text(page_home())
    (ROOT / 'project-services').mkdir(exist_ok=True)
    (ROOT / 'project-services/index.html').write_text(page_division('project'))
    (ROOT / 'property-services').mkdir(exist_ok=True)
    (ROOT / 'property-services/index.html').write_text(page_division('property'))

    for svc in DATA['services']:
        out = ROOT / svc['path']
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page_service(svc))

    for folder, fn in [('about', page_about), ('our-work', page_work),
                       ('testimonials', page_testimonials), ('knowledge-hub', page_hub),
                       ('contact', page_contact)]:
        (ROOT / folder).mkdir(exist_ok=True)
        (ROOT / folder / 'index.html').write_text(fn())

    (ROOT / 'knowledge-hub/el-nino-prep').mkdir(parents=True, exist_ok=True)
    (ROOT / 'knowledge-hub/el-nino-prep/index.html').write_text(page_elnino())

    (ROOT / 'robots.txt').write_text('User-agent: *\nDisallow: /\n')
    (ROOT / '.nojekyll').touch()

    pages = list(ROOT.rglob('*.html'))
    pages = [p for p in pages if '_site' not in p.parts and 'audit' not in p.parts]
    print(json.dumps({'routes': len(pages), 'services': len(DATA['services'])}, indent=2))


if __name__ == '__main__':
    main()
