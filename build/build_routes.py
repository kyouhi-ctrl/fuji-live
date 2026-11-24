import glob,json,math,heapq,xml.etree.ElementTree as ET
import numpy as np
W,E,S,N,kmx,kmy,hw,hh,tw,th=map(float,open('out/meta.txt').read().split()); hw=int(hw);hh=int(hh)
H=np.load('out/h.npy')
nodes={};ways={}
for f in sorted(glob.glob('dl/osm*.xml')):
    for e in ET.parse(f).getroot():
        t={k.get('k'):k.get('v') for k in e.findall('tag')}
        if e.tag=='node': nodes[e.get('id')]=(float(e.get('lat')),float(e.get('lon')))
        elif e.tag=='way': ways[e.get('id')]=([n.get('ref') for n in e.findall('nd')],t)
LAT0=(S+N)/2
def xy(la,lo): return ((lo-W)*math.cos(math.radians(LAT0))*111320, (N-la)*110950)
def elev(x,y):
    u=x/kmx*hw-0.5; v=y/kmy*hh-0.5
    i=int(np.clip(math.floor(u),0,hw-2)); j=int(np.clip(math.floor(v),0,hh-2)); fu=u-i; fv=v-j
    return float(H[j,i]*(1-fu)*(1-fv)+H[j,i+1]*fu*(1-fv)+H[j+1,i]*(1-fu)*fv+H[j+1,i+1]*fu*fv)
adj={}
OK=('path','footway','track','steps','bridleway')
for wid,(nd,t) in ways.items():
    if t.get('highway') not in OK: continue
    nd=[n for n in nd if n in nodes]
    for a,b in zip(nd,nd[1:]):
        pa,pb=xy(*nodes[a]),xy(*nodes[b]); d=math.dist(pa,pb)
        adj.setdefault(a,[]).append((b,d,t.get('name') or '',t.get('highway')))
        adj.setdefault(b,[]).append((a,d,t.get('name') or '',t.get('highway')))
comp={};cid=0
for n0 in adj:
    if n0 in comp: continue
    cid+=1;st=[n0];comp[n0]=cid
    while st:
        u=st.pop()
        for v,*_ in adj[u]:
            if v not in comp: comp[v]=cid;st.append(v)
from collections import Counter
big=Counter(comp.values()).most_common(1)[0][0]
main=[n for n in adj if comp[n]==big]
print('main comp',len(main),'of',len(adj))
def snap(la,lo):
    p=xy(la,lo); return min(main,key=lambda n: math.dist(xy(*nodes[n]),p))
def _old(la,lo):
    p=xy(la,lo); return min(adj,key=lambda n: math.dist(xy(*nodes[n]),p))
def route(a,b,prefer,avoid=()):
    dist={a:0};prev={};pq=[(0,a)]
    while pq:
        d,u=heapq.heappop(pq)
        if u==b: break
        if d>dist[u]: continue
        for v,w,name,hwy in adj[u]:
            m=1.0
            if any(p in name for p in prefer): m=0.4
            elif name=='' : m=1.6
            if any(p in name for p in avoid): m=6
            nd_=d+w*m
            if nd_<dist.get(v,1e18): dist[v]=nd_;prev[v]=u;heapq.heappush(pq,(nd_,v))
    path=[b]
    while path[-1]!=a: path.append(prev[path[-1]])
    return path[::-1]
def chain(wps,prefer,avoid=()):
    ids=[snap(*w) for w in wps]; out=[]
    for a,b in zip(ids,ids[1:]):
        seg=route(a,b,prefer,avoid); out+=seg if not out else seg[1:]
    return out
SUM_Y=(35.3657,138.7330); SUM_F=(35.3596,138.7312)
R={}
R['yoshida_up']=chain([(35.3936,138.7337),(35.3903,138.7416),(35.3858,138.7459),(35.3853,138.7477),(35.3790,138.7445),(35.3693,138.7391),SUM_Y],['吉田','河口湖'],['下り','富士上吉田'])
_d=chain([SUM_Y,(35.3699,138.7411),(35.3766,138.7507),(35.3836,138.7477),(35.3853,138.7477)],['下り','吉田','河口湖'],['上り','登り','富士上吉田'])
_u=R['yoshida_up']; _j=_u.index(_d[-1]) if _d[-1] in _u else min(range(len(_u)),key=lambda i: math.dist(xy(*nodes[_u[i]]),xy(*nodes[_d[-1]])))
R['yoshida_down']=_d+_u[:_j][::-1]
R['subashiri_up']=chain([(35.3661,138.7785),(35.3691,138.7424),(35.3693,138.7391),SUM_Y],['須走ルート「登り」','須走ルート','上り'],['下り'])
R['subashiri_down']=chain([SUM_Y,(35.3699,138.7411),(35.3668,138.7507),(35.3679,138.7676),(35.3661,138.7785)],['須走ルート「下り」','下り','須走'],['上り','登り'])
R['fujinomiya']=chain([(35.3366,138.7341),(35.3447,138.7364),SUM_F],['富士宮'])
R['gotemba_up']=chain([(35.3357,138.7947),(35.3449,138.7656),(35.3541,138.7453),SUM_F],['御殿場ルート 「登り」','御殿場'],['下り'])
g=ways['148863455'][0]; print('gotemba down way ends',nodes[g[0]],nodes[g[-1]])
R['ohachi']=chain([(35.3657,138.7330),(35.3606,138.7274),(35.3596,138.7312),(35.3649,138.7334)],['お鉢'])
R['prince']=chain([(35.3366,138.7341),(35.3392,138.7383),(35.3430,138.7475),(35.3541,138.7453)],['宝永','Loop'])
json.dump({k:v for k,v in R.items()},open('out/route_ids.json','w'))
def stats(ids):
    P=[xy(*nodes[n]) for n in ids]; Z=[elev(*p) for p in P]
    L=sum(math.dist((*a,za),(*b,zb)) for a,b,za,zb in zip(P,P[1:],Z,Z[1:]))
    up=sum(max(0,b-a) for a,b in zip(Z,Z[1:]))
    return len(ids),round(L),round(Z[0]),round(Z[-1]),round(min(Z)),round(max(Z))
for k,v in R.items(): print(k,stats(v))

R['gotemba_down']=chain([SUM_F,(35.3541,138.7453),(35.3497,138.7496),(35.3369,138.7903),(35.3357,138.7947)],['御殿場ルート「下り」','下り','御殿場'],['登り'])
print('gotemba_down',stats(R['gotemba_down']))
def pts(ids):
    out=[];last=None
    for n in ids:
        p=xy(*nodes[n])
        if last and math.dist(p,last)<6: continue
        out.append([round(p[0],1),round(p[1],1)]);last=p
    return out
data={'meta':{'W':W,'E':E,'S':S,'N':N,'kmx':kmx,'kmy':kmy,'hw':hw,'hh':hh,'lat0':LAT0},'paths':{k:pts(v) for k,v in R.items()}}
json.dump(data,open('out/paths.json','w'),ensure_ascii=False,separators=(',',':'))
print({k:len(v) for k,v in data['paths'].items()})
