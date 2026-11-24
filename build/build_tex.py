import numpy as np, math
from PIL import Image, ImageFilter
H=np.load('out/h.npy'); hh,hw=H.shape
W,E,S,N,kmx,kmy,*_=map(float,open('out/meta.txt').read().split())
tw=4096; th=round(tw*hh/hw)
# upsample height to texture res (bicubic via PIL on float)
Hi=np.array(Image.fromarray(H.astype(np.float32)).resize((tw,th),Image.BICUBIC))
dx=kmx/tw; dy=kmy/th
gy,gx=np.gradient(Hi,dy,dx)
# hillshade, light from NW-ish, alt 40
az=math.radians(315); alt=math.radians(42)
slope=np.arctan(np.hypot(gx,gy)); aspect=np.arctan2(-gx,gy)
hs=np.sin(alt)*np.cos(slope)+np.cos(alt)*np.sin(slope)*np.cos(az-aspect)
hs=np.clip(hs,0,1)
# vegetation: elevation-based treeline, lower on the SE (Hoei / Gotemba scoria fields)
P=np.array(Image.open('out/photo_full.jpg').resize((tw,th))).astype(np.float32)
r,g,b=P[...,0],P[...,1],P[...,2]
X=(np.arange(tw)+0.5)/tw*kmx; Y=(np.arange(th)+0.5)/th*kmy
XX,YY=np.meshgrid(X,Y)
sx=(138.7274-W)/(E-W)*kmx; sy=(N-35.3606)/(N-S)*kmy
bear=(np.degrees(np.arctan2(XX-sx,-(YY-sy)))+360)%360
def bump(c,w): d=np.abs((bear-c+180)%360-180); return np.clip(1-d/w,0,1)**1.5
rng=np.random.default_rng(3)
nz=rng.random((th//32+2,tw//32+2)).astype(np.float32)
nz=np.array(Image.fromarray(nz).resize((tw,th),Image.BICUBIC))
nz2=np.array(Image.fromarray(rng.random((th//8+2,tw//8+2)).astype(np.float32)).resize((tw,th),Image.BICUBIC))
treeline=2480-900*bump(128,45)-250*bump(200,40)+260*(nz-0.5)+120*(nz2-0.5)
from scipy.ndimage import gaussian_filter as _gf
veg=_gf(np.clip((treeline-Hi)/260,0,1),5)
def lerp(a,b,t): return a+(b-a)*t[...,None]
forest=np.array([52,74,50],np.float32); meadow=np.array([118,122,82],np.float32)
scoria_lo=np.array([128,104,88],np.float32); scoria_hi=np.array([112,82,72],np.float32)
summit=np.array([136,128,122],np.float32)
t1=np.clip((Hi-2200)/1200,0,1)
bare=lerp(scoria_lo,scoria_hi,t1)
bare=lerp(bare,summit,np.clip((Hi-3450)/300,0,1))
low=lerp(meadow,forest,np.clip(veg*1.5-0.3+0.3*(nz2-0.5),0,1))
base=lerp(bare,low,np.clip(veg*1.3,0,1)*np.clip((2700-Hi)/400,0,1)+np.clip((1700-Hi)/400,0,1)*0.6)
# subtle photo detail luminance
lum=(0.3*r+0.59*g+0.11*b); lum=lum/np.mean(lum)
det=1.0+0.0*lum
from scipy.ndimage import gaussian_filter
cur=gaussian_filter(Hi,6)-Hi
shade=(0.55+0.6*hs)*np.clip(1+cur/60,0.75,1.15)
col=base*shade[...,None]
Image.fromarray(np.clip(col,0,255).astype(np.uint8)).save('out/relief.jpg',quality=84,optimize=True,progressive=True)
Image.fromarray(np.clip(P,0,255).astype(np.uint8)).resize((3072,round(3072*th/tw)),Image.LANCZOS).save('out/photo.jpg',quality=82,optimize=True,progressive=True)
Image.fromarray(np.clip(col,0,255).astype(np.uint8)).resize((1024,round(1024*th/tw))).save('out/relief_small.jpg')
