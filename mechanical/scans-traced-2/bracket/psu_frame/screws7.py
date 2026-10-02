import json,numpy as np,sys,cv2
sys.path.insert(0,"../scanlib"); import scanlib
SX,SY=3.9509971295564403,3.93511116872863
g=cv2.GaussianBlur(cv2.imread("psu_frame_scan.jpeg",0).astype(float),(3,3),0.8)
seeds={"TL":(154.5,259.5),"TR":(521.5,267.5),"ML":(149.5,531.5),"MR":(516.5,538.5),"BL":(145.5,764.5),"BR":(512.5,771.5)}
S={}
for k,(x,y) in seeds.items():
    ox,oy,od,os_=scanlib.ring_fit(g,x,y,6,16,SX,SY,falling=True)
    ix,iy,idd,is_=scanlib.ring_fit(g,ox,oy,1.0,6.5,SX,SY,falling=False)
    S[k]=dict(px=[ox,oy],outer_d=od,outer_sd=os_,inner_px=[ix,iy],inner_d=idd,inner_sd=is_)
    print(k,round(ox,1),round(oy,1),"outerØ",round(od,2),round(os_,2),"innerØ",round(idd,2),round(is_,2),"dc",round((ix-ox)/SX,2),round((iy-oy)/SY,2))
io=json.load(open("../io_board/io_final.json"))["holes"]
keys=list(seeds)
B=np.array([[io[k]["x"],io[k]["y"]] for k in keys])
A=np.array([[S[k]["px"][0]/SX,-S[k]["px"][1]/SY] for k in keys])
for refl in (False,True):
    Am=A.copy()
    if refl: Am[:,0]*=-1
    R,t,rms,res=scanlib.procrustes(Am,B)
    print("mirror" if refl else "direct", "rms",round(rms,3),"rot",round(np.degrees(np.arctan2(R[1,0],R[0,0])),2), np.round(res,2).tolist())
# pattern dims
P={k:np.array([S[k]["px"][0]/SX,S[k]["px"][1]/SY]) for k in keys}
for a,b in [("TL","TR"),("ML","MR"),("BL","BR"),("TL","ML"),("ML","BL"),("TR","MR"),("MR","BR")]:
    print(a,b,round(np.linalg.norm(P[a]-P[b]),2))
json.dump(S,open("work/screws.json","w"),indent=1)
