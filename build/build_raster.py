import math,numpy as np
from PIL import Image
W,E,S,N=138.620,138.835,35.275,35.445
LAT0=(S+N)/2
def tx(lon,z): return (lon+180)/360*2**z
def ty(lat,z): r=np.radians(lat); return (1-np.log(np.tan(r)+1/np.cos(r))/np.pi)/2*2**z
def mosaic(kind,z,ext):
    x0,x1=int(tx(W,z)),int(tx(E,z)); y0,y1=int(ty(N,z)),int(ty(S,z))
    M=np.zeros(((y1-y0+1)*256,(x1-x0+1)*256,3),np.uint8)
    for x in range(x0,x1+1):
        for y in range(y0,y1+1):
            im=np.array(Image.open(f'tiles/{kind}/{z}_{x}_{y}.{ext}').convert('RGB'))
            M[(y-y0)*256:(y-y0+1)*256,(x-x0)*256:(x-x0+1)*256]=im
    return M,x0,y0
def resample(M,x0,y0,z,w,h,interp=True):
    lon=W+(np.arange(w)+0.5)/w*(E-W); lat=N-(np.arange(h)+0.5)/h*(N-S)
    px=(tx(lon,z)-x0)*256-0.5; py=(ty(lat,z)-y0)*256-0.5
    PX,PY=np.meshgrid(px,py)
    if not interp: return M[np.round(PY).astype(int),np.round(PX).astype(int)]
    ix=np.floor(PX).astype(int); iy=np.floor(PY).astype(int); fx=(PX-ix)[...,None]; fy=(PY-iy)[...,None]
    a=M[iy,ix];b=M[iy,ix+1];c=M[iy+1,ix];d=M[iy+1,ix+1]
    return (a*(1-fx)*(1-fy)+b*fx*(1-fy)+c*(1-fx)*fy+d*fx*fy)
kmx=(E-W)*math.cos(math.radians(LAT0))*111320; kmy=(N-S)*110950
print('size m',kmx,kmy)
# DEM
M,x0,y0=mosaic('dem_png',14,'png')
v=(M[...,0].astype(np.int64)<<16)|(M[...,1].astype(np.int64)<<8)|M[...,2]
h=np.where(v<2**23,v*0.01,np.where(v==2**23,np.nan,(v-2**24)*0.01))
print('nan',np.isnan(h).sum(),np.nanmin(h),np.nanmax(h))
h=np.nan_to_num(h,nan=np.nanmin(h))
hw=1024; hh=round(1024*kmy/kmx)
H=resample(h[...,None],x0,y0,14,hw,hh)[...,0]
print('grid',hw,hh,H.min(),H.max())
np.save('out/h.npy',H)
dm=np.clip(np.round(H*10),0,65535).astype(np.uint16)
rgb=np.stack([dm>>8,dm&255,np.zeros_like(dm)],-1).astype(np.uint8)
Image.fromarray(rgb).save('out/terrain.png',optimize=True)
# photo
M,x0,y0=mosaic('seamlessphoto',15,'jpg')
tw=4096; th=round(4096*kmy/kmx)
T=resample(M.astype(np.float32),x0,y0,15,tw,th)
Image.fromarray(np.clip(T,0,255).astype(np.uint8)).save('out/photo_full.jpg',quality=92)
Image.fromarray(np.clip(T,0,255).astype(np.uint8)).resize((1024,round(1024*th/tw))).save('out/photo_small.jpg',quality=85)
open('out/meta.txt','w').write(f'{W} {E} {S} {N} {kmx} {kmy} {hw} {hh} {tw} {th}\n')
