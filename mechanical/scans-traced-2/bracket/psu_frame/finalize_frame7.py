"""Scan 7 -> frame that carries the I/O board (6 bosses match io_board hole pattern) with PSU behind.
Output frame: I/O board back-view frame (bracket/io_board), mm. Scan face = boss side (I/O-board side) -> mirrored."""
import json,numpy as np,sys,cv2,ezdxf,math
sys.path.insert(0,"../scanlib"); import scanlib
SX,SY=3.9509971295564403,3.93511116872863
S=json.load(open("work/screws.json")); io=json.load(open("../io_board/io_final.json"))
H=io["holes"]; sw={"TL":"TR","TR":"TL","ML":"MR","MR":"ML","BL":"BR","BR":"BL"}
def pre(p): p=np.atleast_2d(np.asarray(p,float)); return np.c_[-p[:,0]/SX,-p[:,1]/SY]
A=pre([S[k]["px"] for k in S]); B=np.array([[H[sw[k]]["x"],H[sw[k]]["y"]] for k in S])
R,t,rms,res=scanlib.procrustes(A,B)
def T(p): return pre(p)@R.T+t
def Tinv(q): q=np.atleast_2d(q); a=(q-t)@R; return np.c_[-a[:,0]*SX,-a[:,1]*SY]
rot=math.degrees(math.atan2(R[1,0],R[0,0]))
E=json.load(open("work/edges.json"))["pts"]
side={}
for k in "LR": side[k]=float(np.median(T(np.array(E[k]))[:,0]))
side["T"]=float(np.median(T(np.array(E["T"]))[:,1]))
Bp=np.array([p for p in E["B"] if p[0]>=250]); side["B"]=float(np.median(T(Bp)[:,1]))
# scan-left (L) maps to board +X after mirror
xmin,xmax=sorted([side["L"],side["R"]]); ymin,ymax=sorted([side["T"],side["B"]])
def spread(k,col):
    P=T(np.array(E[k] if k!="B" else Bp))[:,col]; return float(np.percentile(P,90)-np.percentile(P,10))
out={"source":"psu_frame_scan.jpeg (~100 dpi flatbed)","calibration":{"SX":SX,"SY":SY},
 "frame":"I/O board back-view frame (bracket/io_board), mm; scan face = boss side, mirror+rigid",
 "scan_to_frame":{"R":R.tolist(),"t":t.tolist(),"rms":rms,"rot_deg":rot,"alt_direct_fit_rms":0.222},
 "outline":{"x":[xmin,xmax],"y":[ymin,ymax],"w":xmax-xmin,"h":ymax-ymin,"corner_r_est":3.0,
   "edge_spread_p10_p90":{k:spread(k,0 if k in "LR" else 1) for k in "LRTB"}}}
bos=[]
for k in S:
    c=T(S[k]["px"])[0]; bos.append({"id":sw[k],"x":float(c[0]),"y":float(c[1]),"boss_d":S[k]["outer_d"],"bore_d":S[k]["inner_d"],
      "io_hole":[H[sw[k]]["x"],H[sw[k]]["y"]],"d":[float(c[0]-H[sw[k]]["x"]),float(c[1]-H[sw[k]]["y"])]})
out["bosses"]=bos
rings={"c_TL_scan":((143.5,192.0),3.7),"c_TR_scan":((528.7,204.9),3.7),"c_BL_scan":((137.5,862.0),3.2),"c_BR_scan":((517.5,870.6),3.2)}
out["corner_rings"]=[{"id":k,"x":float(T(p)[0][0]),"y":float(T(p)[0][1]),"d":d} for k,(p,d) in rings.items()]
def box(name,x0,x1,y0,y1,note=""):
    c=T(((x0+x1)/2,(y0+y1)/2))[0]; return {"id":name,"cx":float(c[0]),"cy":float(c[1]),"w":(x1-x0)/SX,"h":(y1-y0)/SY,"note":note}
def bead(name,p0,p1,wpx):
    a,b=T(p0)[0],T(p1)[0]; return {"id":name,"p0":a.tolist(),"p1":b.tolist(),"len":float(np.linalg.norm(a-b)),"w":wpx/SY}
out["beads"]=[bead("top_bead",(162,197),(521,203),14),bead("bottom_bead",(191,858),(500,864),14)]
out["black_pads"]=[box("pad_sL_top",139,165,211,278),box("pad_sR_top",506,537,219,289),box("pad_sL_mid",134,160,519,549),
  box("pad_sR_mid",500,532,522,552),box("pad_sL_bot",129,156,744,850),box("pad_sR_bot",497,528,751,857)]
out["foam_rails"]=[box("foam_sL_upper",135,180,280,517),box("foam_sL_lower",133,178,552,742),
  box("foam_sR_upper",490,537,290,522),box("foam_sR_lower",488,535,553,750)]
out["window_approx"]=box("window",183,488,210,790,"open centre; PSU visible through it; edges +-2 mm")
out["bottom_feature"]=box("bottom_rounded_rect",185,470,795,850,"bright rounded rect, blurred (behind frame?) +-2 mm")
json.dump(out,open("psu_frame.json","w"),indent=1)
for k in ["scan_to_frame","outline"]: print(k,json.dumps(out[k])[:400])
for b in bos: print(b["id"],round(b["x"],2),round(b["y"],2),"d",np.round(b["d"],2).tolist(),round(b["boss_d"],2),round(b["bore_d"],2))
for k in ["corner_rings","beads","black_pads","foam_rails"]:
    for f in out[k]: print(k,{a:(round(v,2) if isinstance(v,float) else v) for a,v in f.items()})
print(out["window_approx"]); print(out["bottom_feature"])
# ---- DXF
doc=ezdxf.new("R2010"); doc.units=4; msp=doc.modelspace()
for ly,c in [("OUTLINE",7),("BOSSES",1),("BORES",1),("CORNER_RINGS",3),("BEADS",4),("BLACK_PADS",8),("FOAM_RAILS",6),("WINDOW_APPROX",5),("BOTTOM_FEATURE",5),("IO_BOARD_REF",2),("NOTES",7)]:
    doc.layers.add(ly,color=c)
def rrect(cx,cy,w,h,r,ly):
    r=min(r,w/2-1e-3,h/2-1e-3); x0,x1,y0,y1=cx-w/2,cx+w/2,cy-h/2,cy+h/2
    b=math.tan(math.radians(90)/4)
    msp.add_lwpolyline([(x0+r,y0,0),(x1-r,y0,b),(x1,y0+r,0),(x1,y1-r,b),(x1-r,y1,0),(x0+r,y1,b),(x0,y1-r,0),(x0,y0+r,b)],format="xyb",close=True,dxfattribs={"layer":ly})
o=out["outline"]; rrect((xmin+xmax)/2,(ymin+ymax)/2,o["w"],o["h"],3.0,"OUTLINE")
for b in bos:
    msp.add_circle((b["x"],b["y"]),b["boss_d"]/2,dxfattribs={"layer":"BOSSES"}); msp.add_circle((b["x"],b["y"]),b["bore_d"]/2,dxfattribs={"layer":"BORES"})
for c in out["corner_rings"]: msp.add_circle((c["x"],c["y"]),c["d"]/2,dxfattribs={"layer":"CORNER_RINGS"})
for b in out["beads"]:
    p0,p1=np.array(b["p0"]),np.array(b["p1"]); cx,cy=(p0+p1)/2; L=b["len"]+b["w"]; rrect(cx,cy,L,b["w"],b["w"]/2,"BEADS")
for f in out["black_pads"]: rrect(f["cx"],f["cy"],f["w"],f["h"],0.5,"BLACK_PADS")
for f in out["foam_rails"]: rrect(f["cx"],f["cy"],f["w"],f["h"],2.5,"FOAM_RAILS")
f=out["window_approx"]; rrect(f["cx"],f["cy"],f["w"],f["h"],3,"WINDOW_APPROX")
f=out["bottom_feature"]; rrect(f["cx"],f["cy"],f["w"],f["h"],4,"BOTTOM_FEATURE")
W,Hh=io["W"],io["H"]; msp.add_lwpolyline([(0,0),(W,0),(W,Hh),(0,Hh)],close=True,dxfattribs={"layer":"IO_BOARD_REF"})
for k,h in H.items(): msp.add_circle((h["x"],h["y"]),h["pad_d"]/2,dxfattribs={"layer":"IO_BOARD_REF"})
msp.add_text("Scan 7 frame (I/O-board carrier, PSU side behind). I/O board back-view frame, mm. Traced at ~100 dpi: outline +-0.5, bosses +-0.2, pads/rails/window +-1.5..2",dxfattribs={"layer":"NOTES","height":2.0}).set_placement((xmin,ymin-8))
doc.saveas("psu_frame_ioboard_frame.dxf")
# ---- overlay on scan
im=cv2.imread("psu_frame_scan.jpeg")
def P(q): return tuple(int(round(v)) for v in Tinv(q)[0])
def poly(pts,col,th=1): cv2.polylines(im,[np.array([P(q) for q in pts],np.int32)],True,col,th,cv2.LINE_AA)
def rect(cx,cy,w,h,col): poly([(cx-w/2,cy-h/2),(cx+w/2,cy-h/2),(cx+w/2,cy+h/2),(cx-w/2,cy+h/2)],col)
rect((xmin+xmax)/2,(ymin+ymax)/2,o["w"],o["h"],(0,0,255))
for b in bos:
    c=P((b["x"],b["y"])); cv2.circle(im,c,int(round(b["boss_d"]/2*SX)),(0,0,255),1); cv2.circle(im,c,int(round(b["bore_d"]/2*SX)),(0,255,255),1)
    ch=P(b["io_hole"]); cv2.drawMarker(im,ch,(0,200,0),cv2.MARKER_CROSS,8,1)
for c in out["corner_rings"]: cv2.circle(im,P((c["x"],c["y"])),int(round(c["d"]/2*SX)),(0,200,0),1)
for b in out["beads"]:
    p0,p1=np.array(b["p0"]),np.array(b["p1"]); cx,cy=(p0+p1)/2; rect(cx,cy,b["len"]+b["w"],b["w"],(255,128,0))
for f in out["black_pads"]: rect(f["cx"],f["cy"],f["w"],f["h"],(255,0,255))
for f in out["foam_rails"]: rect(f["cx"],f["cy"],f["w"],f["h"],(0,165,255))
for f in [out["window_approx"],out["bottom_feature"]]: rect(f["cx"],f["cy"],f["w"],f["h"],(255,255,0))
poly([(0,0),(W,0),(W,Hh),(0,Hh)],(0,200,0))
cr=im[150:920,90:600]; cr=cv2.resize(cr,None,fx=1.3,fy=1.3,interpolation=cv2.INTER_CUBIC)
cv2.putText(cr,"red: outline/bosses  green: I/O board outline+holes (reg)  magenta: black pads  orange: foam  cyan: window/bottom feature",(5,15),0,0.33,(0,0,0),1)
cv2.imwrite("psu_frame_overlay.png",cr)
