import sys,os,collections
sys.path.insert(0,os.path.dirname(__file__))
from pdx import *
from techs import load_techs
def numv(s,ref):
    s=str(s)
    if s.endswith('%'): return ('pct',float(s.rstrip('%')))
    try: return float(s)
    except: return 0.0
def load_gui(path='countrytechtreeview.gui'):
    g=parse(path)[0][1]
    top={name(v):v for k,v,l in g if k=='containerWindowType' and isinstance(v,list)}
    root=top['countrytechtreeview']
    folders={}
    for k,v,l in root:
        if k=='containerWindowType' and isinstance(v,list): folders[name(v)]=v
    return top,folders
def gridboxes(folder):
    out={}
    def walk(b,ox,oy,chain):
        for k,v,l in b:
            if not isinstance(v,list): continue
            if k.lower() in('gridboxtype','containerwindowtype'):
                p=get(v,'position') or []
                px=str(get(p,'x') or 0).replace('%%','%'); py=str(get(p,'y') or 0).replace('%%','%')
                def f(s):
                    if s.endswith('%'): return 0.0, float(s[:-1])
                    try: return float(s),0.0
                    except: return 0.0,0.0
                (ax,apx),(ay,apy)=f(px),f(py)
                if k.lower()=='gridboxtype':
                    ss=get(v,'slotsize') or []
                    out[name(v)]=dict(x=ox+ax,y=oy+ay,pctx=apx,pcty=apy,chain=chain,
                        sw=num(get(ss,'width')),sh=num(get(ss,'height')),fmt=(get(v,'format') or 'UP').upper(),line=l)
                else:
                    walk(v,ox+ax,oy+ay,chain+[(name(v),ax,ay,apx,apy)])
    walk(folder,0,0,[])
    return out
def item_templates(top,folder):
    big=top.get(f'techtree_{folder}_item'); small=top.get(f'techtree_{folder}_small_item')
    def info(t):
        if not t: return None
        sub=[]
        for k,v,l in t:
            if k=='containerWindowType' and isinstance(v,list) and (name(v) or '').startswith('sub_technology_slot'):
                sub.append((name(v),pos(v),size(v)))
        return dict(pos=pos(t),size=size(t),subs=sub)
    return info(big),info(small)
def expected(techs,top,folders):
    res={}
    for fname,folder in folders.items():
        if fname in('folder_tabs',): continue
        members={n:t for n,t in techs.items() if fname in t['folders']}
        if not members: continue
        gb=gridboxes(folder)
        big,small=item_templates(top,fname)
        incoming=collections.defaultdict(list)
        for n,t in members.items():
            for c in t['paths']:
                if c in members: incoming[c].append(n)
        # assign each tech to a tree: walk from roots
        tree_of={}
        roots=[n for n in members if not incoming[n]]
        for r in roots:
            stack=[r]
            while stack:
                n=stack.pop()
                if n in tree_of: continue
                tree_of[n]=r
                stack+= [c for c in members[n]['paths'] if c in members]
        for n,t in members.items():
            r=tree_of.get(n)
            g=gb.get(f'{r}_tree') if r else None
            x,y=t['folders'][fname]
            is_small = (not t['equip'] or t['force_small']) and small is not None
            tpl= small if is_small else big
            if not g:
                res[(fname,n)]=dict(err=f'no gridbox {r}_tree',root=r,small=is_small); continue
            if g['fmt']=='LEFT': dx,dy=y*g['sw'],x*g['sh']
            else: dx,dy=x*g['sw'],y*g['sh']
            tx,ty=tpl['pos'] if tpl else (0,0)
            res[(fname,n)]=dict(x=g['x']+dx+tx,y=g['y']+dy+ty,pctx=g['pctx'],pcty=g['pcty'],chain=g['chain'],root=r,small=is_small,size=tpl['size'] if tpl else None,grid=g)
    return res
