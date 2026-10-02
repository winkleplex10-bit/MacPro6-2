"""Scan 8 -> I/O plate carrier/trim frame. Output in I/O board back-view frame (same as io_plate.json), mm.
Registration: scan mirrored, rigid fit of frame openings to io_plate openings (TB columns, USB pairs, audio, HDMI, ETH)."""
import cv2, numpy as np, json, math, sys, ezdxf
sys.path.insert(0,"../scanlib"); import scanlib
SX,SY=3.951014932149311,3.935159813393957
g0=cv2.imread("io_frame_scan.jpeg",0); g=cv2.GaussianBlur(g0,(3,3),0)
pl=json.load(open("../io_plate/io_plate.json")); O={o["id"]:o for o in pl["openings_outer"]}
C=lambda k: np.array(O[k]["centre"]); m=lambda *ks: np.mean([C(k) for k in ks],0)
# ---- segment openings (bright through-holes inside frame)
thr=118
mk=np.zeros_like(g); mk[240:915,240:480]=(g[240:915,240:480]>thr)*255
mk=cv2.morphologyEx(mk,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
cnts,_=cv2.findContours(mk,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
comps=[]
for c in cnts:
    a=cv2.contourArea(c)
    if a<120: continue
    M=cv2.moments(c); cx,cy=M["m10"]/M["m00"],M["m01"]/M["m00"]; x,y,w,h=cv2.boundingRect(c)
    comps.append(dict(c=c,a=a,cx=cx,cy=cy,bb=(x,y,w,h)))
def find(x,y,tol=12):
    k=[d for d in comps if abs(d["cx"]-x)<tol and abs(d["cy"]-y)<tol]; return k[0] if k else None
named={"BIG_L":(345.8,406),"SMALL_R1":(399,457),"SMALL_R2":(397.6,518.7),"TALL_L":(313.7,618.2),"TALL_R":(397,620),
 "SQ_L":(300.3,729.2),"SQ_R":(395,731.4),"ROUND_L":(310.7,802.6),"ROUND_R":(392.6,804.2),"BOTTOM":(350.8,865.8),
 "HOLE_C1":(356.2,581.8),"HOLE_C2":(354.1,648.9),"CORNER_TL":(274.7,289.7),"CORNER_TR":(449.6,294.3),"CORNER_BL":(262.9,822.7),"CORNER_BR":(437.5,827.2)}
F={}
for k,(x,y) in named.items():
    d=find(x,y,15)
    if d is None: print("missing",k); continue
    F[k]=d
# ---- registration (mirror view: (-x,-y))
def pre(p): p=np.atleast_2d(np.asarray(p,float)); return np.c_[-p[:,0]/SX,-p[:,1]/SY]
pairs=[("TALL_R",m("TB_H1","TB_H2","TB_H3")),("SQ_R",m("USB_H1","USB_H2")),("ROUND_R",C("AUDIO_H")),("SMALL_R1",C("HDMI")),("SMALL_R2",C("ETH_H1")),
       ("TALL_L",m("TB_O1","TB_O2","TB_O3")),("ROUND_L",C("AUDIO_O"))]
A=pre([(F[k]["cx"],F[k]["cy"]) for k,_ in pairs]); Bm=np.array([b for _,b in pairs])
R,t,rms,res=scanlib.procrustes(A,Bm)
rot=math.degrees(math.atan2(R[1,0],R[0,0]))
T=lambda p: pre(p)@R.T+t
def Tinv(q): q=np.atleast_2d(q); a=(q-t)@R; return np.c_[-a[:,0]*SX,-a[:,1]*SY]
print("reg rms",round(rms,3),"rot",round(rot,2),[(k,np.round(r,2).tolist()) for (k,_),r in zip(pairs,res)])
# ---- outline (rounded rect fitted in px) -> mm
ol=json.load(open("work/outline.json")); q=ol["rrect_px"]
cxy=T((q[0],q[1]))[0]; th_img=q[4]
# angle of frame long axis in board frame
ax=T((q[0]+100*math.cos(th_img),q[1]+100*math.sin(th_img)))[0]-cxy
ang=math.degrees(math.atan2(ax[1],ax[0]))
outline=dict(cx=float(cxy[0]),cy=float(cxy[1]),w=q[2]/SX,h=q[3]/SY,R=q[5]/SX,angle_deg_in_board_frame=float(((ang+90)%180)-90),fit_res_sd_mm=ol["res_sd_px"]/SX)
Pmm=T(np.array(ol["pts"])); outline["x_range"]=[float(Pmm[:,0].min()),float(Pmm[:,0].max())]; outline["y_range"]=[float(Pmm[:,1].min()),float(Pmm[:,1].max())]
# ---- features in mm
feat={}
for k,d in F.items():
    cm=T((d["cx"],d["cy"]))[0]; poly=T(d["c"][:,0,:].astype(float))
    rect=cv2.minAreaRect(poly.astype(np.float32)); (rw,rh)=sorted(rect[1])
    # axis-aligned extents in frame-local orientation (rotate by -angle)
    a=-math.radians(outline["angle_deg_in_board_frame"]); Rm=np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
    pl_=(poly-cm)@Rm.T
    feat[k]=dict(cx=float(cm[0]),cy=float(cm[1]),w=float(np.ptp(pl_[:,0])),h=float(np.ptp(pl_[:,1])),area_mm2=float(d["a"]/(SX*SY)),
                 eq_d=float(2*math.sqrt(d["a"]/(SX*SY)/math.pi)),poly=poly.tolist())
# L-shape notch: corner where right part ends
L=feat["BIG_L"]; P=np.array(L["poly"])
def xr_at(y,band=0.6):
    s=P[np.abs(P[:,1]-y)<band]; return (float(s[:,0].min()),float(s[:,0].max())) if len(s) else None
L["x_range_top"]=xr_at(L["cy"]+L["h"]/2-14); L["x_range_leg"]=xr_at(L["cy"]-L["h"]/2+10)
ys=np.linspace(L["cy"]-L["h"]/2+1,L["cy"]+L["h"]/2-1,200); wid=[(y,xr_at(y)) for y in ys]; 
# find y where width jumps
ww=[(y,(r[1]-r[0]) if r else 0) for y,r in wid]
jump=max(range(1,len(ww)),key=lambda i: abs(ww[i][1]-ww[i-1][1])); L["step_y"]=float(ww[jump][0])
L["y_range_top"]=[L["step_y"],float(P[:,1].max())]; L["y_range_leg"]=[float(P[:,1].min()),L["step_y"]]
# ---- rails (dark vertical lines either side) by column minima
rails={}
for name,(x0,x1) in {"rail_scan_left":(222,246),"rail_scan_right":(466,486)}.items():
    pts=[]
    for y in range(270,890,6):
        p=g[y,x0:x1].astype(float); k=int(np.argmin(p)); pts.append((x0+k,y))
    pts=np.array(pts,float); mm=T(pts); rails[name]=dict(x_mean=float(mm[:,0].mean()),x_sd=float(mm[:,0].std()),y_range=[float(mm[:,1].min()),float(mm[:,1].max())],
        ends_px_y=[252,905])
    e=T(np.array([[pts[:,0].mean(),252],[pts[:,0].mean(),905]])); rails[name]["ends_mm"]=e.tolist()
# ---- comparisons with plate openings
def bbox(o): return (o["centre"][0]-o["w"]/2,o["centre"][0]+o["w"]/2,o["centre"][1]-o["h"]/2,o["centre"][1]+o["h"]/2)
def inside(o,fk):
    poly=np.array(feat[fk]["poly"],np.float32); x0,x1,y0,y1=bbox(o)
    if o["id"]=="POWER_BUTTON" or o["id"].startswith("AUDIO"):
        cx,cy=o["centre"]; r=o["w"]/2
        return float(min(cv2.pointPolygonTest(poly,(cx+r*math.cos(a),cy+r*math.sin(a)),True) for a in np.linspace(0,2*math.pi,36,endpoint=False)))
    ds=[cv2.pointPolygonTest(poly,(float(x),float(y)),True) for x,y in [(x0,y0),(x1,y0),(x0,y1),(x1,y1),((x0+x1)/2,y0),((x0+x1)/2,y1),(x0,(y0+y1)/2),(x1,(y0+y1)/2)]]
    return float(min(ds))
cmp=[]
for po,fk in [("AC","BIG_L"),("POWER_BUTTON","BIG_L"),("ETH_O1","BIG_L"),("HDMI","SMALL_R1"),("ETH_H1","SMALL_R2"),
              ("TB_H1","TALL_R"),("TB_H2","TALL_R"),("TB_H3","TALL_R"),("TB_O1","TALL_L"),("TB_O2","TALL_L"),("TB_O3","TALL_L"),
              ("USB_H1","SQ_R"),("USB_H2","SQ_R"),("USB_O1","SQ_L"),("USB_O2","SQ_L"),("AUDIO_H","ROUND_R"),("AUDIO_O","ROUND_L")]:
    cmp.append(dict(plate=po,frame=fk,min_margin_mm=round(inside(O[po],fk),2)))
feat["PIN_C3"]=dict(cx=float(T((350.0,803.0))[0][0]),cy=float(T((350.0,803.0))[0][1]),w=3.0,h=3.0,eq_d=3.0,area_mm2=7.1,poly=[],note="dark ring with bright centre between the audio holes (pin/LED?), manual +-0.5")
out=dict(source="io_frame_scan.jpeg (~100 dpi)",calibration=dict(SX=SX,SY=SY),
  identity="I/O plate carrier / trim frame (rounded frame same size as the I/O plate; opening grid = I/O plate port grid)",
  frame="I/O board back-view frame (bracket/io_board; same as io_plate.json), mm. Scan is mirrored (face on glass seen from the board side).",
  registration=dict(R=R.tolist(),t=t.tolist(),rms=rms,rot_deg=rot,pairs=[k for k,_ in pairs],excluded="SQ_L (opening is asymmetric, extends 2.3 mm outward)"),
  outline=outline,features={k:{a:b for a,b in v.items() if a!="poly"} for k,v in feat.items()},rails=rails,plate_vs_frame=cmp,
  threshold=thr)
json.dump(out,open("io_frame.json","w"),indent=1)
print(json.dumps(outline))
for k,v in out["features"].items(): print(k,{a:(round(b,2) if isinstance(b,float) else b) for a,b in v.items()})
print(json.dumps(rails))
for c in cmp: print(c)
# ---- DXF
doc=ezdxf.new("R2010"); doc.units=4; msp=doc.modelspace()
for ly,cl in [("OUTLINE",7),("OPENINGS",1),("HOLES",3),("RAILS",8),("PLATE_REF",2),("PLATE_OPENINGS_REF",2),("NOTES",7)]: doc.layers.add(ly,color=cl)
def rr(cx,cy,w,h,r,ang,ly,n=16):
    pts=[];a=math.radians(ang);ca,sa=math.cos(a),math.sin(a)
    for (qx,qy,a0) in [(w/2-r,h/2-r,0),(-(w/2-r),h/2-r,90),(-(w/2-r),-(h/2-r),180),(w/2-r,-(h/2-r),270)]:
        for i in range(n+1):
            t_=math.radians(a0+90*i/n); x=qx+r*math.cos(t_); y=qy+r*math.sin(t_); pts.append((cx+x*ca-y*sa,cy+x*sa+y*ca))
    msp.add_lwpolyline(pts,close=True,dxfattribs={"layer":ly})
o=outline; rr(o["cx"],o["cy"],o["w"],o["h"],o["R"],o["angle_deg_in_board_frame"],"OUTLINE")
for k,v in feat.items():
    if k.startswith(("HOLE","CORNER","ROUND","PIN")):
        msp.add_circle((v["cx"],v["cy"]),v["eq_d"]/2,dxfattribs={"layer":"HOLES" if not k.startswith("ROUND") else "OPENINGS"})
    else:
        P=np.array(v["poly"]); ap=cv2.approxPolyDP(P.astype(np.float32).reshape(-1,1,2),0.35,True)[:,0,:]
        msp.add_lwpolyline([tuple(p) for p in ap],close=True,dxfattribs={"layer":"OPENINGS"})
for k,r_ in rails.items(): msp.add_line(tuple(r_["ends_mm"][0]),tuple(r_["ends_mm"][1]),dxfattribs={"layer":"RAILS"})
for oo in pl["openings_outer"]:
    x0,x1,y0,y1=bbox(oo)
    if oo["id"] in ("POWER_BUTTON",) or oo["id"].startswith("AUDIO"): msp.add_circle(tuple(oo["centre"]),oo["w"]/2,dxfattribs={"layer":"PLATE_OPENINGS_REF"})
    else: msp.add_lwpolyline([(x0,y0),(x1,y0),(x1,y1),(x0,y1)],close=True,dxfattribs={"layer":"PLATE_OPENINGS_REF"})
msp.add_text("Scan 8 I/O plate carrier frame, I/O board back-view frame (mm). Openings +-0.5, outline +-0.5, holes +-0.5. PLATE_OPENINGS_REF = io_plate.json",dxfattribs={"layer":"NOTES","height":2}).set_placement((o["x_range"][0],o["y_range"][0]-8))
doc.saveas("io_frame_board_frame.dxf")
# ---- overlay on scan
im=cv2.cvtColor(g0,cv2.COLOR_GRAY2BGR)
def P_(q_): return np.round(Tinv(np.atleast_2d(q_))).astype(np.int32)
for oo in pl["openings_outer"]:
    x0,x1,y0,y1=bbox(oo); cv2.polylines(im,[P_([(x0,y0),(x1,y0),(x1,y1),(x0,y1)])],True,(0,200,0),1,cv2.LINE_AA)
for k,v in feat.items():
    if v["poly"]: cv2.polylines(im,[P_(np.array(v["poly"]))],True,(0,0,255),1,cv2.LINE_AA)
    else: cv2.circle(im,tuple(P_((v["cx"],v["cy"]))[0]),6,(0,0,255),1)
# outline
a=math.radians(o["angle_deg_in_board_frame"]); pts=[]
for (qx,qy,a0) in [(o["w"]/2-o["R"],o["h"]/2-o["R"],0),(-(o["w"]/2-o["R"]),o["h"]/2-o["R"],90),(-(o["w"]/2-o["R"]),-(o["h"]/2-o["R"]),180),(o["w"]/2-o["R"],-(o["h"]/2-o["R"]),270)]:
    for i in range(17):
        t_=math.radians(a0+90*i/16); x=qx+o["R"]*math.cos(t_); y=qy+o["R"]*math.sin(t_); pts.append((o["cx"]+x*math.cos(a)-y*math.sin(a),o["cy"]+x*math.sin(a)+y*math.cos(a)))
cv2.polylines(im,[P_(np.array(pts))],True,(255,0,255),1,cv2.LINE_AA)
for k,r_ in rails.items(): e=P_(np.array(r_["ends_mm"])); cv2.line(im,tuple(e[0]),tuple(e[1]),(255,160,0),1)
cr=cv2.resize(im[210:935,200:510],None,fx=1.5,fy=1.5,interpolation=cv2.INTER_CUBIC)
cv2.putText(cr,"red: frame openings  green: io_plate openings (registered)  magenta: outline fit  blue: rails",(4,14),0,0.36,(0,0,255),1)
cv2.imwrite("io_frame_overlay.png",cr)
