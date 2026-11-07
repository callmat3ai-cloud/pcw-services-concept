#!/usr/bin/python3
"""Build a separate content-preserving PCW alternative; never writes source."""
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString
import json, shutil, re, hashlib, posixpath
SRC=Path('/root/pcw-services-preview'); OUT=Path('/root/pcw-services-concept')
BASE='https://callmat3ai-cloud.github.io/pcw-services-concept/'
def soup(t): return BeautifulSoup(t,'html.parser')
def textnodes(s):
 return [str(t).strip() for t in s.find_all(string=True) if t.parent.name not in ['script','style'] and isinstance(t,NavigableString) and t.__class__.__name__!='Comment' and str(t).strip()]
inventory=[]
for f in sorted(SRC.rglob('*.html')):
 if '.git' in f.parts:continue
 s=soup(f.read_text());inventory.append({'file':str(f.relative_to(SRC)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'title':s.title.get_text(),'text':textnodes(s.body),'ids':[x['id'] for x in s.select('[id]')],'modals':{x['id']:x.get_text(' ',strip=True) for x in s.select('.modal')},'services':[{'name':x.h3.get_text(),'tagline':x.select_one('.dir-tag').get_text() if x.select_one('.dir-tag') else '', 'links':[a['href'] for a in x.select('a')]} for x in s.select('.dir-card')],'forms':[str(x) for x in s.select('form')]})
(OUT/'audit').mkdir(exist_ok=True)
(OUT/'audit/source-inventory.json').write_text(json.dumps(inventory,indent=2,ensure_ascii=False))
shutil.copytree(SRC/'assets',OUT/'assets',dirs_exist_ok=True)
for item in inventory:
 rel=item['file']; f=SRC/rel; s=soup(f.read_text());depth=len(Path(rel).parts)-1;prefix='../'*depth
 # Preserve header exactly; adapt only home URL for project Pages.
 for a in s.select('[href]'):
  if a['href']=='/':a['href']=prefix or './'
 for meta in s.select('meta[name="robots"]'):meta.decompose()
 meta=s.new_tag('meta',attrs={'name':'robots','content':'noindex, nofollow'});s.head.append(meta)
 s.head.append(s.new_tag('meta',attrs={'name':'pcw-preview','content':'architectural-complete-v1'}))
 for el in s.select('link[rel="canonical"], meta[property="og:url"]'):
  attr='href' if el.name=='link' else 'content';el[attr]=BASE+(rel[:-10] if rel.endswith('index.html') else rel)
 # Disable unused ambient Three.js; no custom cursor or third-party decorative runtime.
 for el in s.select('script[src]'):
  if 'three' in el['src']:el.decompose()
 s.head.append(s.new_tag('link',rel='stylesheet',href=prefix+'assets/css/concept.css'))
 s.head.append(s.new_tag('script',src=prefix+'assets/js/concept.js',defer=True))
 s.body['class']=s.body.get('class',[])+['concept-home' if rel=='index.html' else 'concept-inner']
 if rel.startswith('services/'):
  s.body['class'].append('concept-service')
  hero=s.select_one('.subpage-hero')
  if hero:
   image=s.new_tag('img',src=prefix+'assets/images/'+('pcw_decking.png' if any(x in rel for x in ['deck','water','roof','planter']) else 'pcw_concrete.png'),alt='PCW contracting and reconstruction',attrs={'class':'service-hero-photo','width':'1024','height':'1024'})
   hero.append(image)
 # Service cards stay fully intact, presented as an editorial directory.
 if rel=='index.html':
  hero=s.select_one('.hero-section');hero.select_one('.hero-three-container')['hidden']=''
  # Architectural masthead: type above a panoramic image, not a split-hero template.
  content=hero.select_one('.hero-content');title=content.select_one('h1').extract();lead=content.select_one('.hero-lead').extract();actions=content.select_one('.hero-actions').extract();subtitle=content.select_one('.hero-subtitle').extract();trustline=content.select_one('.kicker').extract();image=hero.select_one('.hero-bg-photo').extract()
  masthead=s.new_tag('div',attrs={'class':'hero-masthead'});masthead.append(title);intro=s.new_tag('div',attrs={'class':'hero-intro'});intro.append(lead);intro.append(actions);masthead.append(intro)
  stage=s.new_tag('div',attrs={'class':'hero-stage'});stage.append(image);caption=s.new_tag('div',attrs={'class':'hero-caption'});caption.append(subtitle);caption.append(trustline);stage.append(caption)
  holder=hero.select_one('.container');holder.insert(0,masthead);holder.insert(1,stage)
  # Lift proof into a quiet separate horizontal ledger, retaining all approved text.
  trust=hero.select_one('.hero-trust-bar').extract(); ledger=s.new_tag('section',attrs={'class':'concept-ledger'}); wrap=s.new_tag('div',attrs={'class':'container'});wrap.append(trust);ledger.append(wrap);hero.insert_after(ledger)
  for selector,href,label in [('.division-project','project-services/','View project services'),('.division-property','property-services/','View property services')]:
   section=s.select_one(selector);link=s.new_tag('a',href=href,attrs={'class':'chapter-link'});link.string=label;section.select_one('.division-text').append(link)
  # Directories are native progressive disclosure, independently usable without JS.
  for ident,label in [('proj-grid','Explore all project services'),('prop-grid','Explore all property services')]:
   sec=s.select_one('#'+ident);sec['class']=sec.get('class',[])+['concept-directory']
   details=s.new_tag('details',attrs={'class':'service-explorer'});summary=s.new_tag('summary');summary.string=label;details.append(summary)
   grid=sec.select_one('.dir-grid')
   if not grid: grid=sec.select_one('.container').find_all('div',recursive=False)[-1]
   grid.wrap(details)
   tools=s.new_tag('div',attrs={'class':'explorer-tools'});label=s.new_tag('label',attrs={'for':ident+'-search'});label.string='Find a service';field=s.new_tag('input',attrs={'type':'search','id':ident+'-search','class':'explorer-search','placeholder':'Search by service or tagline','autocomplete':'off'});tools.append(label);tools.append(field);status=s.new_tag('p',attrs={'class':'explorer-status','role':'status','aria-live':'polite'});status.string='';tools.append(status);summary.insert_after(tools)
  # Show complete company introduction, with all differentiators available on demand.
  proof=s.select_one('.proof-section');grid=proof.select_one('.differentiator-grid');details=s.new_tag('details',attrs={'class':'company-disclosure'});summary=s.new_tag('summary');summary.string='Why choose PCW';details.append(summary);grid.wrap(details)
  for sel in ['.license-block','.client-strip']:
   x=proof.select_one(sel)
   if x:details.append(x.extract())
  # All seven testimonials stay in home DOM and on their dedicated route.
  reviews=s.select_one('.review-grid');cards=reviews.select('.review-card');first=cards[0];first['class'].append('featured-review')
  details=s.new_tag('details',attrs={'class':'reviews-disclosure'});summary=s.new_tag('summary');summary.string='Read all client testimonials';details.append(summary);more=s.new_tag('div',attrs={'class':'review-grid'});details.append(more)
  for c in cards[1:]:more.append(c.extract())
  reviews.insert_after(details)
  # Keep contact intro visible; move only long form into disclosure, auto-open anchors.
  form=s.select_one('#pcw-contact-form');details=s.new_tag('details',attrs={'class':'estimate-disclosure'});summary=s.new_tag('summary');summary.string='Start your estimate request';details.append(summary);form.wrap(details)
 if rel=='knowledge-hub/index.html':
  anchor_titles={'vendor':'What a Vendor Needs','budget':'Budget Options','components':'Building Components','concrete':'Concrete Problems'}
  for ident,title in anchor_titles.items():
   heading=next((h for h in s.select('h3') if h.get_text(' ',strip=True)==title),None)
   if heading:heading['id']=ident
 # Complete quote dialog keyboard behavior is provided by concept.js; original fragment IDs stay.
 for dialog in s.select('.modal'):
  dialog['tabindex']='-1';dialog['aria-hidden']='true'
 # Keep paragraph text; soften visual labels instead of silently editing approved copy.
 dest=OUT/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(str(s))
# Original handler and endpoint preserved byte-for-byte. Remove ONLY optional polish IIFE by its exact marker.
js=(SRC/'assets/js/main.js').read_text();marker='/* PCW interactive polish: cursor glow + scroll reveal + card tilt-safe hover (desktop only) */'
if marker in js:js=js[:js.index(marker)]
(OUT/'assets/js/main.js').write_text(js)
(OUT/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
# Narrow, parsed mechanical repairs to legacy CSS; no copy/token substitution.
import tinycss2
css_path=OUT/'assets/css/main.css'
rules=tinycss2.parse_stylesheet(css_path.read_text(),skip_comments=False,skip_whitespace=False)
transition_selectors={'.btn','.dropdown-item i','.sidebar-link-item','.gallery-filter-btn','.dir-open','.dir-btn'}
grid_values={'.division-grid':'minmax(0, 1fr) minmax(0, 1fr)', '.capabilities-teaser-grid':'repeat(3, minmax(0, 1fr))', '.footer-top-grid':'minmax(0,1.6fr) minmax(0,1.2fr) minmax(0,1.2fr) minmax(0,1fr)'}
for rule in rules:
 if rule.type=='qualified-rule':
  selector=tinycss2.serialize(rule.prelude).strip();decls=tinycss2.parse_declaration_list(rule.content,skip_comments=False,skip_whitespace=False);changed=False
  for d in decls:
   if d.type!='declaration':continue
   val=tinycss2.serialize(d.value).strip();replacement=None
   if selector in transition_selectors and d.name=='transition' and val.startswith('all '):replacement='color .2s ease, background-color .2s ease, border-color .2s ease, box-shadow .2s ease, transform .2s ease'
   if selector in grid_values and d.name=='grid-template-columns':replacement=grid_values[selector]
   if selector=='.reveal' and d.name=='opacity':replacement='1'
   if selector=='.reveal' and d.name=='transform':replacement='none'
   if replacement is not None:d.value=tinycss2.parse_component_value_list(replacement);changed=True
  if changed:rule.content=tinycss2.parse_component_value_list(tinycss2.serialize(decls))
legacy=tinycss2.serialize(rules)
for old,new in [('  .division-grid {\n    grid-template-columns: 1fr;', '  .division-grid {\n    grid-template-columns: minmax(0, 1fr);'),('  .footer-top-grid {\n    grid-template-columns: 1fr 1fr;', '  .footer-top-grid {\n    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);'),('  .footer-top-grid {\n    grid-template-columns: 1fr;', '  .footer-top-grid {\n    grid-template-columns: minmax(0, 1fr);')]:
 legacy=legacy.replace(old,new)
css_path.write_text(legacy)
(OUT/'.nojekyll').touch()
print(json.dumps({'routes':len(inventory),'home_services':len(inventory[[i['file'] for i in inventory].index('index.html')]['services']),'source_read_only':True}))
