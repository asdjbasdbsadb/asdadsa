import sys,glob,os,re
sys.path.insert(0,os.path.dirname(__file__))
from pdx import *
def getall(b,k): return [v for kk,v,l in b if kk.lower()==k.lower()]
def load_techs(root='technologies'):
    techs={}
    for f in sorted(glob.glob(root+'/*.txt')):
        tree=parse(f)
        for k,blk,l in tree:
            if k!='technologies' or not isinstance(blk,list): continue
            var={kk:vv for kk,vv,_ in blk if kk.startswith('@')}
            def val(x):
                x=var.get(x,x)
                try: return float(x)
                except: return 0.0
            for name,t,line in blk:
                if name.startswith('@') or not isinstance(t,list): continue
                d={'name':name,'file':f,'line':line,'folders':{},'paths':[],'subs':[],'xor':[]}
                for fo in getall(t,'folder'):
                    p=get(fo,'position') or []
                    d['folders'][get(fo,'name')]=(val(get(p,'x') or 0),val(get(p,'y') or 0))
                for p in getall(t,'path'):
                    lt=get(p,'leads_to_tech')
                    if lt: d['paths'].append(lt)
                for s in getall(t,'sub_technologies'):
                    d['subs']+= [kk for kk,vv,_ in s]
                for s in getall(t,'xor'):
                    d['xor']+= [kk for kk,vv,_ in s]
                eq=getall(t,'enable_equipments')
                d['equip']=[kk for e in eq for kk,vv,_ in e]
                d['force_small']=str(get(t,'force_use_small_tech_layout')).lower()=='yes'
                d['allow_branch']=get(t,'allow_branch')
                d['is_special_project']=bool(get(t,'special_project_specialization')) or name.startswith('sp_')
                techs[name]=d
    return techs
if __name__=='__main__':
    t=load_techs()
    print(len(t))
    import collections
    c=collections.Counter(f for d in t.values() for f in d['folders'])
    print(c)
