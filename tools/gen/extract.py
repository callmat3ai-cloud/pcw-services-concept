#!/usr/bin/env python3
"""Extract approved PCW content from the read-only source into structured JSON.

Source of truth: /root/pcw-services-preview (read only, never written).
Output: /root/pcw-services-concept/tools/gen/content.json
"""
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

SRC = Path('/root/pcw-services-preview')
OUT = Path('/root/pcw-services-concept/tools/gen/content.json')


def soup(path):
    return BeautifulSoup((SRC / path).read_text(), 'html.parser')


def clean(text):
    return re.sub(r'\s+', ' ', text or '').strip()


def txt(el):
    return clean(el.get_text(' ', strip=True)) if el else ''


def src(p):
    p = re.sub(r'^\.\./', '', p.strip())
    p = re.sub(r'^\./', '', p)
    p = p.split('#')[0]
    if p in ('', '/'):
        return 'index.html'
    if p.endswith('/'):
        return p + 'index.html'
    if not p.endswith('.html') and '.' not in Path(p).name:
        return p + '/index.html'
    return p


def nav(s):
    items = []
    for ni in s.select('.desktop-nav .nav-item'):
        link = ni.select_one('.nav-link')
        if not link:
            continue
        entry = {
            'label': clean(link.get_text(' ', strip=True)),
            'href': link.get('href', '#'),
            'children': [],
        }
        for a in ni.select('.dropdown-menu .dropdown-item'):
            strong = a.select_one('strong')
            span = a.select_one('span')
            entry['children'].append({
                'label': clean(strong.get_text(strip=True)) if strong else clean(a.get_text(' ', strip=True)),
                'note': clean(span.get_text(' ', strip=True)) if span else '',
                'href': a.get('href', '#'),
            })
        items.append(entry)
    return items


def footer(s):
    f = s.select_one('.site-footer')
    cols = []
    if f:
        for col in f.select('.footer-col'):
            title = col.select_one('.footer-col-title')
            links = [{'label': txt(a), 'href': a.get('href', '#')} for a in col.select('.footer-links a')]
            if title or links:
                cols.append({'title': txt(title), 'links': links})
    return cols


def contact_facts(s):
    """Pull the site-wide contact strings."""
    phone = email = address = license_no = ''
    m = s.select_one('.header-phone')
    if m:
        phone = txt(m)
    text = s.get_text(' ', strip=True)
    em = re.search(r'[\w.+-]+@[\w.-]+\.\w+', text)
    if em:
        email = em.group(0)
    ad = re.search(r'(\d+\s+W\.?\s*18th\s+Street[^|,]*Costa Mesa,\s*CA\s*\d{5})', text)
    if ad:
        address = clean(ad.group(1))
    lic = re.search(r'#\s?699611', text)
    if lic:
        license_no = '#699611'
    return {'phone': phone, 'email': email, 'address': address, 'license': license_no}


def spec_rows(s):
    rows = []
    for r in s.select('.spec-row'):
        rows.append({'label': txt(r.select_one('.spec-label')), 'value': txt(r.select_one('.spec-val'))})
    return rows


def service_page(path):
    s = soup(path)
    hero = s.select_one('.subpage-hero')
    h1 = hero.select_one('h1') if hero else None
    span = h1.select_one('span') if h1 else None
    tagline = txt(span) if span else ''
    title = clean(h1.get_text(' ', strip=True)) if h1 else ''
    if tagline and title.endswith(tagline):
        title = clean(title[: -len(tagline)]).rstrip('/ ').strip()
    crumbs = [txt(a) for a in (hero.select('.breadcrumbs a') if hero else [])]
    division = ''
    km = hero.select_one('.kicker') if hero else None
    if km:
        division = txt(km).replace(' Division', '')
    lead = txt(hero.select_one('.subpage-lead')) if hero else ''
    body = []
    main = s.select_one('.service-main-content')
    if main:
        for child in main.find_all(recursive=False):
            if child.name == 'h2':
                body.append({'type': 'h2', 'text': txt(child)})
            elif child.name == 'p':
                body.append({'type': 'p', 'text': txt(child)})
            elif child.name == 'ul':
                items = []
                for li in child.select('li'):
                    strong = li.select_one('strong')
                    items.append({
                        'term': txt(strong).rstrip(' –-').strip() if strong else '',
                        'body': txt(li.select_one('span')) if li.select_one('span') else txt(li),
                    })
                body.append({'type': 'list', 'items': items})
    related = []
    side = s.select_one('.service-sidebar')
    if side:
        for a in side.select('.sidebar-links-list a'):
            related.append({'label': txt(a), 'href': a.get('href', '#')})
    facts = []
    for card in (side.select('.sidebar-card') if side else []):
        t = txt(card.select_one('.sidebar-title'))
        if t == 'Service Facts':
            facts = spec_rows(card)
    cta = s.select_one('.cta-strip-section')
    return {
        'path': path,
        'title': title,
        'tagline': tagline,
        'division': division,
        'crumbs': crumbs,
        'lead': lead,
        'body': body,
        'facts': facts,
        'related': related,
        'cta': {
            'eyebrow': txt(cta.select_one('.kicker')) if cta else '',
            'heading': txt(cta.select_one('h2')) if cta else '',
            'body': txt(cta.select_one('p')) if cta else '',
        },
    }


def cards(s, selector):
    out = []
    for c in s.select(selector):
        h3 = c.select_one('h3')
        tag = c.select_one('.dir-tag')
        links = [{'label': clean(a.get_text(' ', strip=True)), 'href': a.get('href', '')} for a in c.select('a')]
        out.append({'name': txt(h3), 'tagline': txt(tag), 'links': links})
    return out


def modal_map(s):
    """modal id -> service page href and body text blocks"""
    modals = {}
    for m in s.select('.modal'):
        mid = m.get('id', '')
        title = txt(m.select_one('h3'))
        tag = txt(m.select_one('.modal-tag'))
        bullets = []
        for li in m.select('.service-bullets li'):
            strong = li.select_one('strong')
            bullets.append({'term': txt(strong).rstrip(' –-').strip() if strong else '',
                            'body': txt(li.select_one('span')) if li.select_one('span') else txt(li)})
        actions = [{'label': clean(a.get_text(' ', strip=True)), 'href': a.get('href', ''), 'class': ' '.join(a.get('class', []))}
                   for a in m.select('.modal-actions a')]
        modals[mid] = {'title': title, 'tagline': tag, 'bullets': bullets, 'actions': actions}
    return modals


def division_blocks(s):
    out = {}
    for key, sel in [('project', '.division-gateway-section.division-project'), ('property', '.division-gateway-section.division-property')]:
        sec = s.select_one(sel)
        if not sec:
            continue
        h2 = sec.select_one('.section-h2')
        span = h2.select_one('span') if h2 else None
        out[key] = {
            'heading': txt(h2),
            'accent': txt(span) if span else '',
            'lead': txt(sec.select_one('.dir-lead')),
            'cta': [{'label': txt(a), 'href': a.get('href', '')} for a in sec.select('.division-text a.btn')],
        }
    return out


def main_content(page):
    s = soup(page)
    return s


def build():
    data = {'site': {}, 'nav': [], 'footer': [], 'home': {}, 'divisions': {}, 'services': [],
            'about': {}, 'work': {}, 'testimonials': {}, 'hub': {}, 'elnino': {}, 'contact': {}}

    home = soup('index.html')
    data['site'] = contact_facts(home)
    data['nav'] = nav(home)
    data['footer'] = footer(home)

    # ---------- homepage ----------
    hero = home.select_one('.hero-section')
    h1 = hero.select_one('h1')
    h1_span = h1.select_one('span') if h1 else None
    data['home']['hero'] = {
        'title': txt(h1),
        'title_accent': txt(h1_span) if h1_span else '',
        'subtitle': txt(hero.select_one('.hero-subtitle')),
        'lead': txt(hero.select_one('.hero-lead')),
        'trust': [{'value': txt(t.select_one('.trust-item-value')), 'label': txt(t.select_one('.trust-item-label'))}
                  for t in hero.select('.hero-trust-bar .trust-item')],
        'actions': [{'label': clean(a.get_text(' ', strip=True)), 'href': a.get('href', ''), 'class': ' '.join(a.get('class', []))}
                    for a in hero.select('.hero-actions a')],
    }

    data['divisions'] = division_blocks(home)
    data['home']['project_cards'] = cards(home, '#proj-grid .dir-card')
    data['home']['project_lead'] = txt(home.select_one('#proj-grid .dir-lead'))
    data['home']['property_lead'] = txt(home.select_one('#prop-grid .dir-lead'))
    data['home']['property_cards'] = cards(home, '#prop-grid .dir-card')
    data['home']['modals'] = modal_map(home)

    proof = home.select_one('.proof-section')
    if proof:
        data['home']['proof'] = {
            'heading': txt(proof.select_one('.section-h2')),
            'paragraphs': [txt(p) for p in proof.select('.proof-text p, .section-p')],
            'differentiators': [
                {'title': txt(d.select_one('h3')), 'body': txt(d.select_one('p'))}
                for d in proof.select('.differentiator-card, .differentiator-item')
            ],
            'license_block': txt(proof.select_one('.license-block')),
            'client_strip': txt(proof.select_one('.client-strip')),
        }

    caps = home.select_one('.capabilities-teaser-section')
    if caps:
        data['home']['capabilities'] = {
            'heading': txt(caps.select_one('.section-h2')),
            'paragraphs': [txt(p) for p in caps.select('.section-p')],
            'cards': [{'title': txt(c.select_one('h3')), 'body': txt(c.select_one('p'))} for c in caps.select('.cap-card, .capability-card, .work-card')],
        }

    reviews = home.select_one('.review-grid')
    data['home']['testimonials'] = [
        {'quote': txt(r.select_one('p')),
         'name': txt(r.select_one('.review-name')),
         'title': txt(r.select_one('.review-title')),
         'category': txt(r.select_one('.review-cat'))}
        for r in (reviews.select('.review-card') if reviews else [])
    ]

    hub = home.select_one('.knowledge-hub-preview-section')
    if hub:
        data['home']['hub'] = {
            'heading': txt(hub.select_one('.section-h2')),
            'paragraphs': [txt(p) for p in hub.select('.section-p')],
            'cards': [{'title': txt(c.select_one('h3')), 'body': txt(c.select_one('p')), 'href': (c.get('href') or (c.select_one('a').get('href') if c.select_one('a') else ''))}
                      for c in hub.select('.hub-topic-card')],
        }

    contact = home.select_one('.contact-section')
    if contact:
        form = contact.select_one('form')
        fields = []
        if form:
            for el in form.select('input, select, textarea'):
                fields.append({
                    'tag': el.name, 'id': el.get('id', ''), 'name': el.get('name', ''),
                    'type': el.get('type', ''), 'label': txt(contact.select_one(f'label[for="{el.get("id","")}"]')),
                    'required': el.has_attr('required'), 'placeholder': el.get('placeholder', ''),
                    'options': [txt(o) for o in el.select('option')] if el.name == 'select' else [],
                })
        data['home']['contact'] = {
            'heading': txt(contact.select_one('.section-h2')),
            'paragraphs': [txt(p) for p in contact.select('.section-p')],
            'details': [txt(d) for d in contact.select('.contact-details-list div')],
            'fields': fields,
        }

    # ---------- division index pages ----------
    for key, page in [('project', 'project-services/index.html'), ('property', 'property-services/index.html')]:
        s = soup(page)
        hero = s.select_one('.subpage-hero')
        data['divisions'].setdefault(key, {})
        data['divisions'][key]['index'] = {
            'path': page,
            'title': txt(hero.select_one('h1')) if hero else '',
            'lead': txt(hero.select_one('.subpage-lead')) if hero else '',
            'lead_paragraphs': [txt(p) for p in s.select('.dir-lead, .section-p')],
            'cards': cards(s, '.dir-card'),
            'modals': modal_map(s),
        }

    # ---------- service pages ----------
    for path in sorted((SRC / 'services').glob('*/index.html')):
        data['services'].append(service_page(str(path.relative_to(SRC))))

    # ---------- about ----------
    s = soup('about/index.html')
    hero = s.select_one('.subpage-hero')
    about_sec = None
    for sec in s.select('main > section'):
        cls = ' '.join(sec.get('class', []))
        if cls.startswith('subpage-hero') or cls.startswith('cta-strip'):
            continue
        about_sec = sec
    data['about'] = {
        'title': txt(hero.select_one('h1')) if hero else '',
        'accent': txt(hero.select_one('h1 span')) if hero and hero.select_one('h1 span') else '',
        'eyebrow': txt(hero.select_one('.kicker')) if hero else '',
        'lead': txt(hero.select_one('.subpage-lead')) if hero else '',
        'heading': txt(about_sec.select_one('h2')) if about_sec else '',
        'reasons': [
            {'n': txt(d.select_one('.differentiator-num')), 'title': txt(d.select_one('h3')), 'body': txt(d.select_one('p'))}
            for d in (about_sec.select('.differentiator-card') if about_sec else [])
        ],
    }

    # ---------- work ----------
    s = soup('our-work/index.html')
    hero = s.select_one('.subpage-hero')
    work_sec = None
    for sec in s.select('main > section'):
        cls = ' '.join(sec.get('class', []))
        if cls.startswith('subpage-hero') or cls.startswith('cta-strip'):
            continue
        work_sec = sec
    data['work'] = {
        'title': txt(hero.select_one('h1')) if hero else '',
        'accent': txt(hero.select_one('h1 span')) if hero and hero.select_one('h1 span') else '',
        'eyebrow': txt(hero.select_one('.kicker')) if hero else '',
        'lead': txt(hero.select_one('.subpage-lead')) if hero else '',
        'heading': txt(work_sec.select_one('h2')) if work_sec else '',
        'intro': txt(work_sec.select_one('.section-p')) if work_sec else '',
        'projects': [{'name': txt(c.select_one('h3')), 'category': txt(c.select_one('.dir-tag'))}
                     for c in (work_sec.select('.dir-card') if work_sec else [])],
    }

    # ---------- testimonials ----------
    s = soup('testimonials/index.html')
    hero = s.select_one('.subpage-hero')
    data['testimonials'] = {
        'title': txt(hero.select_one('h1')) if hero else '',
        'eyebrow': txt(hero.select_one('.kicker')) if hero else '',
        'lead': txt(hero.select_one('.subpage-lead')) if hero else '',
        'reviews': [{'quote': txt(r.select_one('p')), 'name': txt(r.select_one('.review-name')),
                     'title': txt(r.select_one('.review-title')), 'category': txt(r.select_one('.review-cat'))}
                    for r in s.select('.review-card')],
    }

    # ---------- knowledge hub ----------
    s = soup('knowledge-hub/index.html')
    hero = s.select_one('.subpage-hero')
    data['hub'] = {
        'title': txt(hero.select_one('h1')) if hero else '',
        'accent': '',
        'eyebrow': txt(hero.select_one('.kicker')) if hero else '',
        'lead': txt(hero.select_one('.subpage-lead')) if hero else '',
        'heading': txt(s.select_one('main > section .section-h2')),
        'topics': [{'title': txt(c.select_one('h3')), 'body': txt(c.select_one('p')), 'href': c.get('href', '')}
                   for c in s.select('.hub-topic-card')],
    }

    # ---------- el nino ----------
    s = soup('knowledge-hub/el-nino-prep/index.html')
    hero = s.select_one('.subpage-hero')
    body = s.select_one('main > section:not(.subpage-hero):not(.cta-strip-section)')
    guides = []
    if body:
        cur = None
        for el in body.find_all(['h2', 'ol'], recursive=True):
            if el.find(['ol']):
                continue
            if el.name == 'h2':
                cur = {'heading': txt(el), 'items': []}
                guides.append(cur)
            elif el.name == 'ol' and cur is not None:
                cur['items'] = [txt(li) for li in el.select('li')]
    data['elnino'] = {
        'title': txt(hero.select_one('h1')) if hero else '',
        'accent': txt(hero.select_one('h1 span')) if hero and hero.select_one('h1 span') else '',
        'eyebrow': txt(hero.select_one('.kicker')) if hero else '',
        'lead': txt(hero.select_one('.subpage-lead')) if hero else '',
        'guides': guides,
    }

    # ---------- contact ----------
    s = soup('contact/index.html')
    hero = s.select_one('.subpage-hero')
    contact_sec = s.select_one('.contact-section')
    fields = []
    if contact_sec:
        for el in contact_sec.select('form input, form select, form textarea'):
            fields.append({'tag': el.name, 'id': el.get('id', ''), 'name': el.get('name', ''), 'type': el.get('type', ''),
                           'required': el.has_attr('required'), 'placeholder': el.get('placeholder', ''),
                           'options': [txt(o) for o in el.select('option')] if el.name == 'select' else []})
    data['contact'] = {
        'title': txt(hero.select_one('h1')) if hero else '',
        'lead': txt(hero.select_one('.subpage-lead')) if hero else '',
        'paragraphs': [txt(p) for p in contact_sec.select('.section-p, .contact-intro p')] if contact_sec else [],
        'fields': fields,
        'form_html': str(contact_sec.select_one('form')) if contact_sec and contact_sec.select_one('form') else '',
    }

    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    return data


if __name__ == '__main__':
    d = build()
    print(json.dumps({
        'services': len(d['services']),
        'home_project_cards': len(d['home'].get('project_cards', [])),
        'home_property_cards': len(d['home'].get('property_cards', [])),
        'modals_home': len(d['home'].get('modals', {})),
        'testimonials_home': len(d['home'].get('testimonials', [])),
        'testimonials_page': len(d['testimonials'].get('reviews', [])),
        'nav_items': len(d['nav']),
        'about_blocks': len(d['about'].get('sections', [])),
        'work_blocks': len(d['work'].get('blocks', [])),
        'hub_blocks': len(d['hub'].get('blocks', [])),
        'elnino_blocks': len(d['elnino'].get('blocks', [])),
        'contact_fields': len(d['contact'].get('fields', [])),
    }, indent=2))
