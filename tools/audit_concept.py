#!/usr/bin/python3
"""Offline content, routes, dialogs, form and CSS acceptance audit."""
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Comment
from collections import Counter
from urllib.parse import urlsplit,unquote
import json,re,tinycss2,hashlib
P=Path(__file__).resolve().parents[1];S=Path('/root/pcw-services-preview')
def dom(p): return BeautifulSoup(p.read_text(),'html.parser')
def texts(s):return Counter(str(t).strip() for t in s.find_all(string=True) if not isinstance(t,Comment) and t.parent.name not in ['script','style'] and str(t).strip())
inv=json.loads((P/'audit/source-inventory.json').read_text());errors=[];coverage=[];links=0;modal_count=0
for row in inv:
 f=P/row['file'];a=dom(S/row['file']);b=dom(f)
 missing=texts(a.body)-texts(b.body)
 if missing:errors.append({'route':row['file'],'missing_text':dict(missing)})
 ids={x['id'] for x in b.select('[id]')}; old_ids={x['id'] for x in a.select('[id]')}
 if old_ids-ids:errors.append({'route':row['file'],'missing_ids':sorted(old_ids-ids)})
 for x in a.select('.modal'):
  new=b.find(id=x['id']); modal_count+=1
  if not new or x.get_text(' ',strip=True)!=new.get_text(' ',strip=True):errors.append({'route':row['file'],'modal_changed':x['id']})
 if [str(x) for x in a.select('form')] != [str(x) for x in b.select('form')]:errors.append({'route':row['file'],'form_changed':True})
 # Header markup must match except sole root path repair.
 for selector in ['.site-header','.mobile-drawer']:
  x=a.select_one(selector);y=b.select_one(selector)
  for el in x.select('[href="/"]'):el['href']='../'*(len(Path(row['file']).parts)-1) or './'
  if str(x)!=str(y):errors.append({'route':row['file'],'header_changed':selector})
 if b.select_one('meta[name="robots"]')['content']!='noindex, nofollow':errors.append({'route':row['file'],'indexable':True})
 for el in b.select('[href],[src]'):
  u=el.get('href',el.get('src'));part=urlsplit(u)
  if part.scheme or part.netloc or not u or u.startswith('data:'):continue
  links+=1
  if part.path.startswith('/'):errors.append({'route':row['file'],'escaping_root_link':u});continue
  target=f.parent/unquote(part.path) if part.path else f
  if target.is_dir():target=target/'index.html'
  target=target.resolve()
  if not target.exists():errors.append({'route':row['file'],'missing_target':u});continue
  if part.fragment and target.suffix=='.html':
   d=b if target==f.resolve() else dom(target)
   if not d.find(id=unquote(part.fragment)):errors.append({'route':row['file'],'broken_fragment':u})
 for c in b.select('.dir-card:has(.dir-btn-quote)'):
  quote=c.select_one('.dir-btn-quote');learn=c.select_one('.dir-btn-learn')
  if not quote or not learn or not quote['href'].startswith('#') or not b.find(id=quote['href'][1:]) or '/services/' not in '/'+learn['href']:errors.append({'route':row['file'],'service_actions':c.get_text(' ',strip=True)})
 coverage.append({'route':row['file'],'source_text_nodes':sum(texts(a.body).values()),'preserved':not missing,'modals':len(b.select('.modal'))})
css_errors=[];cycles=[];undefined=[]
allcss='\n'.join(x.read_text() for x in (P/'assets/css').glob('*.css'))
for f in (P/'assets/css').glob('*.css'):
 for rule in tinycss2.parse_stylesheet(f.read_text(),skip_whitespace=True,skip_comments=True):
  if rule.type=='error':css_errors.append(str(rule))
  if rule.type=='qualified-rule':
   for d in tinycss2.parse_declaration_list(rule.content,skip_whitespace=True,skip_comments=True):
    if d.type=='error':css_errors.append(f'{f.name}:{d.message}')
for name,val in re.findall(r'(--[\w-]+)\s*:\s*([^;}{]+)',allcss):
 if re.search(r'var\(\s*'+re.escape(name)+r'\s*[,)]',val):cycles.append(name)
defined=set(re.findall(r'(--[\w-]+)\s*:',allcss));used=set(re.findall(r'var\(\s*(--[\w-]+)',allcss));undefined=sorted(used-defined)
js=(P/'assets/js/main.js').read_text();sourcejs=(S/'assets/js/main.js').read_text();start=sourcejs.index('async function handleFormSubmit');end=sourcejs.index('/* PCW interactive polish')
handler_preserved=sourcejs[start:end].strip()==js[js.index('async function handleFormSubmit'):].strip()
report={'routes':len(coverage),'services_routes':len([x for x in coverage if x['route'].startswith('services/')]),'home_services':len(dom(P/'index.html').select('.dir-card')),'home_testimonials':len(dom(P/'index.html').select('.review-card')),'preserved_modal_instances':modal_count,'local_links_assets_fragments_checked':links,'coverage':coverage,'errors':errors,'css_parse_errors':css_errors,'css_self_cycles':cycles,'undefined_css_variables':undefined,'original_handler_preserved':handler_preserved,'source_unchanged':all(hashlib.sha256((S/r['file']).read_bytes()).hexdigest()==r['sha256'] for r in inv),'form_note':'Source handler submits six keys only: name/email/phone/service/message/source_url. Additional displayed fields are not separately serialized in source; handler preserved as explicitly required. No real test submission performed.'}
(P/'audit/acceptance.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='coverage'},indent=2));raise SystemExit(bool(errors or css_errors or cycles or undefined or not handler_preserved))
