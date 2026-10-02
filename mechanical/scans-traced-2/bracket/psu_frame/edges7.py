import cv2, numpy as np, json
SX,SY=3.9509971295564403,3.93511116872863
g=cv2.GaussianBlur(cv2.imread("psu_frame_scan.jpeg",0).astype(float),(5,5),1.2)
def cross(p,t):  # first index where p goes below t (p starts in bg)
    i=int(np.argmax(p<t)); return i-1+(p[i-1]-t)/(p[i-1]-p[i])
pts={"L":[],"R":[],"T":[],"B":[]}
for y in range(250,800,3):
    bg=np.median(g[y,95:112]); p=g[y,105:165]; pts["L"].append((105+cross(p,(bg+100)/2),y))
    bg=np.median(g[y,565:590]); p=g[y,520:575][::-1]; pts["R"].append((574-cross(p,(bg+100)/2),y))
for x in range(185,485,3):
    bg=np.median(g[150:170,x]); p=g[160:215,x]; pts["T"].append((x,160+cross(p,(bg+100)/2)))
    bg=np.median(g[895:915,x]); p=g[850:905,x][::-1]; pts["B"].append((x,904-cross(p,(bg+100)/2)))
fits={}
for k,P in pts.items():
    P=np.array(P); u,v=(1,0) if k in "LR" else (0,1)
    for it in range(3):
        a,b=np.polyfit(P[:,u],P[:,v],1); r=P[:,v]-(a*P[:,u]+b)
        P=P[np.abs(r)<max(1.0,3*np.std(r))]
    fits[k]=(a,b,float(np.std(r)),len(P)); print(k,round(a,4),round(b,2),round(np.std(r),2),len(P))
json.dump({"fits":fits,"pts":{k:np.array(v).tolist() for k,v in pts.items()}},open("work/edges.json","w"))
