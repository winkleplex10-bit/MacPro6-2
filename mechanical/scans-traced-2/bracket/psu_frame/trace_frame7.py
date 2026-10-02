import cv2, numpy as np, json
SX,SY=3.9509971295564403,3.93511116872863
g=cv2.GaussianBlur(cv2.imread("psu_frame_scan.jpeg",0).astype(float),(5,5),1.2)
gx=cv2.Sobel(g,cv2.CV_64F,1,0,ksize=3); gy=cv2.Sobel(g,cv2.CV_64F,0,1,ksize=3)
def sub(p,i):
    if 0<i<len(p)-1:
        d=p[i-1]-2*p[i]+p[i+1]
        return i+(0.5*(p[i-1]-p[i+1])/d if d!=0 else 0)
    return i
E={}
L=[];R=[];T=[];B=[]
for y in range(250,800,4):
    p=-gx[y,112:150]; i=int(np.argmax(p)); L.append((112+sub(p,i),y))
    p=gx[y,522:560]; i=int(np.argmax(p)); R.append((522+sub(p,i),y))
for x in range(190,480,4):
    p=-gy[172:200,x]; i=int(np.argmax(p)); T.append((x,172+sub(p,i)))
    p=gy[862:895,x]; i=int(np.argmax(p)); B.append((x,862+sub(p,i)))
def fitx(P):  # x = a*y+b
    P=np.array(P); a,b=np.polyfit(P[:,1],P[:,0],1); r=P[:,0]-(a*P[:,1]+b)
    k=np.abs(r)<2.5*np.median(np.abs(r))+0.5; a,b=np.polyfit(P[k,1],P[k,0],1); r=P[k,0]-(a*P[k,1]+b)
    return a,b,float(np.std(r)),int(k.sum())
def fity(P):
    P=np.array(P); a,b=np.polyfit(P[:,0],P[:,1],1); r=P[:,1]-(a*P[:,0]+b)
    k=np.abs(r)<2.5*np.median(np.abs(r))+0.5; a,b=np.polyfit(P[k,0],P[k,1],1); r=P[k,1]-(a*P[k,0]+b)
    return a,b,float(np.std(r)),int(k.sum())
for n,P,f in [("L",L,fitx),("R",R,fitx),("T",T,fity),("B",B,fity)]:
    E[n]=f(P); print(n,[round(v,4) for v in E[n][:3]],E[n][3])
json.dump({k:list(v) for k,v in E.items()},open("work/edges.json","w"))
