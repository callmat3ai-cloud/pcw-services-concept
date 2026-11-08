#!/usr/bin/env python3
"""QA the rendered concept: links, assets, form ids, modals, content coverage."""
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse, unquote

from bs4 import BeautifulSoup

ROOT = Path('/root/pcw-services-concept')
SRC = Path('/root/pcw-services-preview')
PAGES = sorted(p for p in ROOT.rglob('*.html')
               if '_site' not in p.parts and 'audit' not in p.parts)

errors = []
warnings = []


def resolve(page, href):
    href = href.split('#')[0].split('?')[0]
    if not href or href.startswith(('mailto:', 'tel:', 'http://', 'https://')):
        return None
    target = (page.parent / unquote(href)).resolve()
    if href.endswith('/'):
        target = target / 'index.html'
    return target


def main():
    ids_by_page = {}
    for page in PAGES:
        soup = BeautifulSoup(page.read_text(), 'html.parser')
        ids_by_page[page] = {el.get('id') for el in soup.select('[id]')}

    for page in PAGES:
        soup = BeautifulSoup(page.read_text(), 'html.parser')
        rel = page.relative_to(ROOT)

        # links
        for a in soup.select('a[href]'):
            href = a['href'].strip()
            if href.startswith(('mailto:', 'tel:', 'http://', 'https://')):
                continue
            if href in ('#', ''):
                continue
            if href.startswith('#'):
                frag = href[1:]
                if frag and frag not in ids_by_page[page]:
                    errors.append(f'{rel}: missing fragment target #{frag}')
                continue
            target = resolve(page, href)
            if target and not target.exists():
                errors.append(f'{rel}: broken link {href}')
            if '#' in href:
                frag = href.split('#', 1)[1]
                if target and target.exists() and target.suffix == '.html':
                    tids = ids_by_page.get(target)
                    if tids is None:
                        tids = {el.get('id') for el in BeautifulSoup(target.read_text(), 'html.parser').select('[id]')}
                    if frag not in tids:
                        errors.append(f'{rel}: missing cross-page fragment {href}')

        # assets
        for el in soup.select('img[src], link[rel="stylesheet"][href], script[src]'):
            url = el.get('src') or el.get('href')
            if not url or url.startswith(('http://', 'https://', 'data:')):
                continue
            if not (page.parent / url).exists():
                errors.append(f'{rel}: missing asset {url}')

        # structure
        if not soup.select_one('h1'):
            errors.append(f'{rel}: no h1')
        for img in soup.select('img'):
            if not img.get('alt'):
                warnings.append(f'{rel}: image without alt ({img.get("src")})')

        # form on contact pages
        if rel.as_posix() in ('index.html', 'contact/index.html'):
            form = soup.select_one('form#pcw-contact-form')
            if not form:
                errors.append(f'{rel}: estimate form missing')
            else:
                fields = form.select('input[id], select[id], textarea[id]')
                if len(fields) < 16:
                    errors.append(f'{rel}: form has {len(fields)} fields, expected 16')
                if 'handleFormSubmit' not in (form.get('onsubmit') or ''):
                    errors.append(f'{rel}: form handler not wired')

    # modal coverage
    home = BeautifulSoup((ROOT / 'index.html').read_text(), 'html.parser')
    counts = {
        'home_modals': len(home.select('.modal')),
        'home_spec_rows': len(home.select('.spec__row')),
        'home_testimonials': len(home.select('.quotelist article')) + len(home.select('.quote--lead')),
        'project_modals': len(BeautifulSoup((ROOT / 'project-services/index.html').read_text(), 'html.parser').select('.modal')),
        'property_modals': len(BeautifulSoup((ROOT / 'property-services/index.html').read_text(), 'html.parser').select('.modal')),
        'service_pages': len(list((ROOT / 'services').glob('*/index.html'))),
        'about_reasons': len(BeautifulSoup((ROOT / 'about/index.html').read_text(), 'html.parser').select('.principle')),
        'work_projects': len(BeautifulSoup((ROOT / 'our-work/index.html').read_text(), 'html.parser').select('.projectlist__row')),
        'hub_topics': len(BeautifulSoup((ROOT / 'knowledge-hub/index.html').read_text(), 'html.parser').select('.topicgrid article')),
        'elnino_items': len(BeautifulSoup((ROOT / 'knowledge-hub/el-nino-prep/index.html').read_text(), 'html.parser').select('.guide li')),
    }

    # content coverage: every source service name + testimonial name must appear
    src_home = BeautifulSoup((SRC / 'index.html').read_text(), 'html.parser')
    home_text = home.get_text(' ', strip=True)
    missing = []
    for c in src_home.select('.dir-card'):
        name = c.select_one('h3').get_text(' ', strip=True)
        if name not in home_text:
            missing.append(f'service card: {name}')
    for r in src_home.select('.review-card .review-name'):
        name = r.get_text(' ', strip=True)
        if name not in home_text:
            missing.append(f'testimonial: {name}')

    report = {'pages': len(PAGES), 'counts': counts, 'errors': errors, 'warnings': warnings[:10],
              'missing_content': missing}
    print(json.dumps(report, indent=2))
    return 1 if (errors or missing) else 0


if __name__ == '__main__':
    sys.exit(main())
