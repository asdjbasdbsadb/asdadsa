import sys,os
sys.path.insert(0,os.path.dirname(__file__))
from pdx import *
from PIL import Image,ImageDraw
PATH=sys.argv[1]; OUT=sys.argv[2]; os.makedirs(OUT,exist_ok=True)
W=1920  # assumed folder width for % positions
mod=parse(PATH); root=mod[0][1][0][1]
def p(v,ref):
    pp=get(v,'position') or []
    def f(s,ref):
        s=str(s or 0).replace('%%','%')
        return float(s[:-1])*ref/100 if s.endswith('%') else num(s)
    return f(get(pp,'x'),ref),f(get(pp,'y'),1000)
for k,f,l in root:
    if k!='containerWindowType' or name(f)=='mod1_folder_tabs': continue
    fn=name(f)
    items=[]
    def walk(b,ox,oy):
        for kk,v,ll in b:
            if not isinstance(v,list): continue
            if kk in('iconType','containerWindowType','instantTextBoxType'):
                n=name(v) or ''; x,y=p(v,W)
                o=(get(v,'Orientation') or get(v,'orientation') or '').upper()
                if 'RIGHT' in o: continue
                items.append((kk,n,ox+x,oy+y,size(v),get(v,'spriteType'),get(v,'text')))
                if kk=='containerWindowType' and not n.startswith(('mod1_card_','mod1_sub_')): walk(v,ox+x,oy+y)
    walk(f,0,0)
    xs=[i[2]+max(i[4][0],80) for i in items if i[1].startswith('mod1_card_')]; ys=[i[3]+90 for i in items if i[1].startswith('mod1_card_')]
    w=int(max(xs+[1400]))+40; h=int(max(ys+[900]))+40
    off=20
    im=Image.new('RGB',(w+off,h+off),(30,33,38)); d=ImageDraw.Draw(im)
    for kk,n,x,y,s,sp,t in items:
        x+=off;y+=off
        if kk=='instantTextBoxType' and t and not n.startswith('mod1_nm_'): d.text((x,y),str(t)[:30],fill=(200,180,90))
        elif n.startswith('mod1_ln_'):
            key=(sp or '').replace('GFX_techtree_line_','').replace('GFX_techline_','')
            c=(120,170,230)
            if key in('left_states','right_states'): d.line([(x,y+8),(x+35,y+8)],fill=c,width=3)
            elif key in('up_states','down_states'): d.line([(x+8,y),(x+8,y+35)],fill=c,width=3)
            else: d.ellipse([(x+4,y+4),(x+12,y+12)],fill=(230,120,120))
    for kk,n,x,y,s,sp,t in items:
        x+=off;y+=off
        if n.startswith('mod1_card_'):
            ww,hh=s
            # industry/electronics cards draw as the small square tile
            if fn in('mod1_industry_folder','mod1_electronics_folder'): ww,hh=70,70
            d.rectangle([(x,y),(x+ww,y+hh)],fill=(70,80,60),outline=(220,220,220))
            d.text((x+3,y+3),n.split('_folder_')[-1][:24],fill=(255,255,255))
        elif n.startswith('mod1_sub_'):
            d.rectangle([(x,y),(x+s[0],y+s[1])],fill=(90,60,60),outline=(220,150,150))
    im.save(f'{OUT}/{fn[5:]}.png')
    print(fn,im.size)
