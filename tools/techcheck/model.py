import sys,os,collections
sys.path.insert(0,os.path.dirname(__file__))
from layout import *
from techs import load_techs
techs=load_techs(); top,folders=load_gui()
def folder_model(fname,mode,force_fmt=None):
    """mode: 'old' = no shift (what the mod used), 'new' = shift negative slot indices to 0 per tree.
    returns tech -> dict(slot=(px,py) slot origin, card=(x,y), size, small, root, grid)"""
    folder=folders[fname]; gb=gridboxes(folder); big,small=item_templates(top,fname)
    members={n:t for n,t in techs.items() if fname in t['folders']}
    inc=collections.defaultdict(list)
    for n,t in members.items():
        for c in t['paths']:
            if c in members: inc[c].append(n)
    tree={}
    for r in [n for n in members if not inc[n]]:
        st=[r]
        while st:
            n=st.pop()
            if n in tree: continue
            tree[n]=r; st+=[c for c in members[n]['paths'] if c in members]
    out={}
    byroot=collections.defaultdict(list)
    for n,r in tree.items(): byroot[r].append(n)
    for r,ns in byroot.items():
        g=gb[r+'_tree']; fmt=force_fmt or g['fmt']
        def hv(n):
            x,y=members[n]['folders'][fname]
            return (y,x) if fmt=='LEFT' else (x,y)
        mh=min(hv(n)[0] for n in ns); mv=min(hv(n)[1] for n in ns)
        sh=min(0,mh) if mode=='new' else 0; sv=min(0,mv) if mode=='new' else 0
        for n in ns:
            h,v=hv(n); t=members[n]
            sm=(not t['equip'] or t['force_small']) and small is not None
            tpl=small if sm else big
            px=g['x']+(h-sh)*g['sw']; py=g['y']+(v-sv)*g['sh']
            out[n]=dict(slot=(px,py),card=(px+tpl['pos'][0],py+tpl['pos'][1]),size=tpl['size'],small=sm,root=r,grid=g,fmt=fmt,shift=(-sh*g['sw'],-sv*g['sh']))
    if mode=='new':
        # the game shifts the whole folder so no tree has negative slots
        fx=max(d['shift'][0] for d in out.values()); fy=max(d['shift'][1] for d in out.values())
        for d in out.values():
            ox,oy=d['shift']
            d['slot']=(d['slot'][0]-ox+fx,d['slot'][1]-oy+fy); d['card']=(d['card'][0]-ox+fx,d['card'][1]-oy+fy); d['shift']=(fx,fy)
    return out,members
