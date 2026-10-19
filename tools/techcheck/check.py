"""Check mod1's research tree view against the game's own data.

Run from the repository root:  python tools/techcheck/check.py [--render OUTDIR]

It reads common/technologies (technologies/*.txt), the vanilla countrytechtreeview.gui
and the .gfx files, works out where the game places every tech, and reports:
  - cards that are missing, misplaced or the wrong size
  - sprites the interface uses that no .gfx file defines
  - scripted GUI keys that don't match an element in the interface
  - duplicate element names
With --render it also draws one preview PNG per folder.
"""
import sys,os,re,glob,collections
sys.path.insert(0,os.path.dirname(__file__))
from model import *
GUI='mod1/interface/mod1_research_tree_view.gui'
SG='mod1/common/scripted_guis/mod1_research_tree_scripted_gui.txt'
problems=0
def report(msg):
    global problems; problems+=1; print('  '+msg)
print('Card positions (expected from technologies/*.txt):')
mod=parse(GUI); mroot=mod[0][1][0][1]
cards={}
def walk(b,ox,oy,fn):
    for k,v,l in b:
        if isinstance(v,list) and k=='containerWindowType':
            n=name(v) or ''; x,y=pos(v)
            if n.startswith('mod1_card_'): cards[(fn,n[len('mod1_card_'+fn)+1:])]=(ox+x,oy+y,size(v),l)
            elif '_sub_' not in n: walk(v,ox+x,oy+y,fn)
for k,f,l in mroot:
    if k=='containerWindowType' and name(f).endswith(('folder','folder_')) or (k=='containerWindowType' and name(f) in ('mod1_mtgnavalfolder','mod1_mtgnavalsupportfolder')):
        walk(f,0,0,name(f)[5:])
for fn in folders:
    if fn=='folder_tabs': continue
    exp,_=folder_model(fn,'new')
    for t,e in exp.items():
        c=cards.get((fn,t))
        if not c: report(f'{fn}: {t} has no card'); continue
        if (round(e['card'][0]),round(e['card'][1]))!=(c[0],c[1]): report(f'{fn}: {t} at {c[:2]} (line {c[3]}), expected {tuple(round(v) for v in e["card"])}')
        if tuple(e['size'])!=c[2]: report(f'{fn}: {t} size {c[2]}, expected {tuple(e["size"])}')
    extra=[t for (f2,t) in cards if f2==fn and t not in exp]
    for t in extra: report(f'{fn}: card {t} is not a tech in this folder')
g=open(GUI,encoding='utf-8-sig').read(); s=open(SG,encoding='utf-8-sig').read()
print('Sprites:')
d=set()
for f in glob.glob('*.gfx'): d|={x.lower() for x in re.findall(r'name\s*=\s*"?(GFX_\w+)',open(f,encoding='utf-8-sig',errors='replace').read())}
CORE={'gfx_airwing_carrier_icon','gfx_button_123x34','gfx_closebutton','gfx_tiled_window_transparent_transparent'}  # defined in vanilla files not in this repo
for u in sorted(set(re.findall(r'(?:spriteType|quadTextureSprite)\s*=\s*"(GFX_\w+)"',g))):
    if u.lower() not in d and u.lower() not in CORE: report(f'{u} is not defined in any .gfx file')
print('Scripted GUI keys:')
names=collections.Counter(re.findall(r'name = "(mod1_\w+)"',g))
for k in re.findall(r'^\t\t\t(mod1_\w+?)_(?:visible|click_enabled|click) = \{',s,re.M):
    if k not in names: report(f'{k} has a trigger/effect but no interface element')
print('Element names:')
for n,c in names.items():
    if c>1: report(f'{n} is used {c} times')
print(f'\n{problems} problem(s) found')
if '--render' in sys.argv:
    out=sys.argv[sys.argv.index('--render')+1]
    os.system(f'{sys.executable} {os.path.join(os.path.dirname(__file__),"render.py")} {GUI} {out}')
sys.exit(1 if problems else 0)
