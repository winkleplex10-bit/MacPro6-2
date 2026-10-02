import cv2, numpy as np, json, math
from scipy.optimize import least_squares
SX,SY=3.951014932149311,3.935159813393957
g=cv2.GaussianBlur(cv2.imread("io_frame_scan.jpeg",0).astype(np.float32),(3,3),0.8)
def sd_rrect(P,cx,cy,w,h,th,r):
    c,s=math.cos(th),math.sin(th); X=(P[:,0]-cx)*c+(P[:,1]-cy)*s; Y=-(P[:,0]-cx)*s+(P[:,1]-cy)*c
    qx=np.abs(X)-(w/2-r); qy=np.abs(Y)-(h/2-r)
    return np.hypot(np.maximum(qx,0),np.maximum(qy,0))+np.minimum(np.maximum(qx,qy),0)-r
def rr_pts(cx,cy,w,h,th,r,n=720):
    # points on rounded rect boundary
    pts=[];c,s=math.cos(th),math.sin(th)
    for k in range(n):
        a=2*math.pi*k/n; dx,dy=math.cos(a),math.sin(a)
        # march along ray to boundary
        lo,hi=0,max(w,h)
        for _ in range(40):
            m=(lo+hi)/2; p=np.array([[cx+m*(dx*c-dy*s),cy+m*(dx*s+dy*c)]])
            if sd_rrect(p,cx,cy,w,h,th,r)[0]<0: lo=m
            else: hi=m
        pts.append(p[0])
    return np.array(pts)
# initial (px): x 255-460, y 255-905, R 45
p0=[357.5,580,205,650,0.0,45]
pts=[]
B=rr_pts(*p0)
cen=np.array(p0[:2])
for b in B:
    d=b-cen; L=np.linalg.norm(d); u=d/L
    ts=np.arange(L-10,L+10,0.25); xs=cen[0]+ts*u[0]; ys=cen[1]+ts*u[1]
    v=cv2.remap(g,xs.astype(np.float32).reshape(1,-1),ys.astype(np.float32).reshape(1,-1),cv2.INTER_LINEAR)[0]
    k=int(np.argmin(v))
    if v[k]<70 and 4<k<len(v)-4: pts.append((xs[k],ys[k],v[k]))
P=np.array(pts)[:,:2]; print("pts",len(P))
f=lambda q: sd_rrect(P,*q)
q=least_squares(f,p0,loss="soft_l1",f_scale=1.5).x
r=f(q); k=np.abs(r)<3*np.median(np.abs(r))+0.5
q=least_squares(lambda z: sd_rrect(P[k],*z),q,loss="soft_l1",f_scale=1.0).x; r=sd_rrect(P[k],*q)
print("fit px",np.round(q,2),"theta deg",round(math.degrees(q[4]),3),"res sd",round(r.std(),2),"n",k.sum())
print("w mm",q[2]/SX,"h mm",q[3]/SY,"R mm",q[5]/SX)
json.dump({"rrect_px":q.tolist(),"pts":P[k].tolist(),"res_sd_px":float(r.std())},open("work/outline.json","w"))
