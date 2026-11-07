#!/usr/bin/env python3
"""Stage only public static files; never publish audit/tools/project metadata."""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'_site'
if DEST.exists():shutil.rmtree(DEST)
DEST.mkdir()
for name in ['index.html','robots.txt','.nojekyll','assets','about','contact','project-services','property-services','our-work','testimonials','knowledge-hub','services']:
 src=ROOT/name; dst=DEST/name
 if src.is_dir():shutil.copytree(src,dst)
 else:shutil.copy2(src,dst)
assert len(list(DEST.rglob('*.html')))==45
assert not list(DEST.rglob('CNAME'))
print('Staged 45 HTML routes and public assets only; no audit/tools/config/domain metadata.')
