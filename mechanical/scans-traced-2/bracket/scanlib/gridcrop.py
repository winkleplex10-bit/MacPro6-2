"""grid_crop(img, frame=(X0,Y1,K), x0,x1,y0,y1, path, step, f): crop of a rectified image (origin X0,Y1 at top-left, K px/mm) with a mm grid."""
import cv2, math, numpy as np
def grid_crop(img, X0, Y1, K, x0, x1, y0, y1, path, step=5, f=1.0, clahe=True):
    c0 = int(round((x0 - X0) * K)); c1 = int(round((x1 - X0) * K)); r0 = int(round((Y1 - y1) * K)); r1 = int(round((Y1 - y0) * K))
    cr = img[max(r0, 0):r1, max(c0, 0):c1].copy()
    if clahe:
        lab = cv2.cvtColor(cr, cv2.COLOR_BGR2LAB); lab[:, :, 0] = cv2.createCLAHE(2.5, (6, 6)).apply(lab[:, :, 0]); cr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    if f != 1: cr = cv2.resize(cr, None, fx=f, fy=f, interpolation=cv2.INTER_CUBIC)
    kk = K * f
    for v in np.arange(math.ceil(x0 / step) * step, x1, step):
        X = int((v - x0) * kk); big = abs(v / 10 - round(v / 10)) < 1e-6; cv2.line(cr, (X, 0), (X, cr.shape[0]), (0, 255, 255) if big else (0, 110, 170), 1)
        if big: cv2.putText(cr, "%g" % v, (X + 2, 12), 0, 0.4, (0, 255, 255), 1)
    for v in np.arange(math.ceil(y0 / step) * step, y1, step):
        Y = int((y1 - v) * kk); big = abs(v / 10 - round(v / 10)) < 1e-6; cv2.line(cr, (0, Y), (cr.shape[1], Y), (0, 255, 255) if big else (0, 110, 170), 1)
        if big: cv2.putText(cr, "%g" % v, (2, Y - 2), 0, 0.4, (0, 255, 255), 1)
    cv2.imwrite(path, cr)
if __name__ == "__main__":
    import sys; a = sys.argv; img = cv2.imread(a[1])
    grid_crop(img, float(a[2]), float(a[3]), float(a[4]), float(a[5]), float(a[6]), float(a[7]), float(a[8]), a[9], float(a[10]) if len(a) > 10 else 5, float(a[11]) if len(a) > 11 else 1.0)
