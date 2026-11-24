import math,os,subprocess,sys
from concurrent.futures import ThreadPoolExecutor
W,E,S,N=138.620,138.835,35.275,35.445
def tx(lon,z): return (lon+180)/360*2**z
def ty(lat,z): r=math.radians(lat); return (1-math.log(math.tan(r)+1/math.cos(r))/math.pi)/2*2**z
jobs=[]
for kind,z,ext in [('dem_png',14,'png'),('seamlessphoto',15,'jpg')]:
    x0,x1=int(tx(W,z)),int(tx(E,z)); y0,y1=int(ty(N,z)),int(ty(S,z))
    print(kind,z,x0,x1,y0,y1,(x1-x0+1)*(y1-y0+1))
    os.makedirs(f'tiles/{kind}',exist_ok=True)
    for x in range(x0,x1+1):
        for y in range(y0,y1+1):
            f=f'tiles/{kind}/{z}_{x}_{y}.{ext}'
            if not os.path.exists(f): jobs.append((f,f'https://cyberjapandata.gsi.go.jp/xyz/{kind}/{z}/{x}/{y}.{ext}'))
def get(j):
    f,u=j
    for a in range(3):
        r=subprocess.run(['curl','-s','-m','40','-o',f,'-w','%{http_code}',u],capture_output=True,text=True)
        if r.stdout=='200': return 0
    return u
bad=[b for b in ThreadPoolExecutor(12).map(get,jobs) if b]
print('failed',len(bad),bad[:5])
