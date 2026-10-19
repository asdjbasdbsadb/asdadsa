import re,sys
TOK=re.compile(r'"[^"]*"|[{}=]|[^\s{}="#]+|#[^\n]*')
def parse(path):
    src=open(path,encoding='utf-8-sig',errors='replace').read()
    toks=[];line=1;pos=0
    for m in TOK.finditer(src):
        line+=src.count('\n',pos,m.start());pos=m.start()
        t=m.group(0)
        if t.startswith('#'):continue
        toks.append((t,line))
    i=0
    def block():
        nonlocal i
        items=[]
        while i<len(toks):
            t,l=toks[i]
            if t=='}': i+=1; return items
            if i+1<len(toks) and toks[i+1][0]=='=':
                i+=2
                if toks[i][0]=='{':
                    i+=1; items.append((t,block(),l))
                else:
                    items.append((t,toks[i][0].strip('"'),l)); i+=1
            elif t=='{':
                i+=1; items.append(('',block(),l))
            else:
                items.append((t,None,l)); i+=1
        return items
    return block()
def get(b,k):
    for kk,v,l in b:
        if kk.lower()==k.lower(): return v
def name(b): 
    n=get(b,'name'); return n
def num(s):
    try: return int(float(s))
    except: return 0
def pos(v):
    p=get(v,'position')
    if not isinstance(p,list): return (0,0)
    return (num(get(p,'x')),num(get(p,'y')))
def size(v):
    s=get(v,'size')
    if not isinstance(s,list): return (0,0)
    return (num(get(s,'width')),num(get(s,'height')))
