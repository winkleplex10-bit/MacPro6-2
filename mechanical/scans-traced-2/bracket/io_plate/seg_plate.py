import cv2, numpy as np, json, sys
sys.path.insert(0,"../scanlib"); import scanlib
SX,SY=3.9507,3.9348
def seg(path, thr, name):
    g=cv2.imread(path,0); gb=cv2.GaussianBlur(g,(3,3),0)
    m=(gb<thr).astype(np.uint8)
    m[:, 640:]=0; m[960:,:]=0   # rulers region off
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,_=cv2.connectedComponentsWithStats(m); i=1+np.argmax(st[1:,4]); m=(lab==i).astype(np.uint8)
    cnts,hier=cv2.findContours(m,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)
    hier=hier[0]; out=[]
    ext=[k for k in range(len(cnts)) if hier[k][3]<0]; e=max(ext,key=lambda k:cv2.contourArea(cnts[k]))
    c=cnts[e]; x,y,w,h=cv2.boundingRect(c); r=cv2.minAreaRect(c)
    print(name,"outline bbox px",x,y,w,h,"mm %.2f x %.2f"%(w/SX,h/SY),"minAreaRect mm %.2f x %.2f ang %.2f"%(r[1][0]/SX,r[1][1]/SY,r[2]))
    holes=[]
    for k in range(len(cnts)):
        if hier[k][3]==e and cv2.contourArea(cnts[k])>40:
            hc=cnts[k]; bx,by,bw,bh=cv2.boundingRect(hc); M=cv2.moments(hc)
            cx,cy=M["m10"]/M["m00"],M["m01"]/M["m00"]
            circ=4*np.pi*cv2.contourArea(hc)/cv2.arcLength(hc,True)**2
            holes.append(dict(cx=cx,cy=cy,w=bw/SX,h=bh/SY,area=cv2.contourArea(hc)/(SX*SY),circ=circ,bbox=[bx,by,bw,bh]))
    holes.sort(key=lambda d:(d["cy"],d["cx"]))
    for d in holes: print("  hole px(%.1f,%.1f) %.2f x %.2f mm area %.1f circ %.2f"%(d["cx"],d["cy"],d["w"],d["h"],d["area"],d["circ"]))
    cv2.imwrite("work/mask_%s.png"%name,m*255)
    return dict(outline=c[:,0,:].tolist(), bbox=[x,y,w,h], holes=holes)
if __name__=="__main__":
    for thr in (70,90):
        r=seg("io_plate_outer_scan.jpeg",thr,"outer%d"%thr)
