import cv2, sys, numpy as np
def zoom(src, x0, y0, w, h, f, out, clahe=True, step=10):
    im = cv2.imread(src); cr = im[y0:y0 + h, x0:x0 + w].copy()
    if clahe:
        lab = cv2.cvtColor(cr, cv2.COLOR_BGR2LAB); lab[:, :, 0] = cv2.createCLAHE(2.5, (6, 6)).apply(lab[:, :, 0]); cr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    cr = cv2.resize(cr, None, fx=f, fy=f, interpolation=cv2.INTER_CUBIC)
    for v in range((x0 // step + 1) * step, x0 + w, step):
        X = int((v - x0) * f); c = (0, 255, 255) if v % 50 == 0 else (0, 120, 120)
        cv2.line(cr, (X, 0), (X, cr.shape[0]), c if v % 50 == 0 else (0, 90, 160), 1)
        if v % 50 == 0: cv2.putText(cr, str(v), (X + 2, 12), 0, 0.4, (0, 255, 255), 1)
    for v in range((y0 // step + 1) * step, y0 + h, step):
        Y = int((v - y0) * f); c = (0, 255, 255) if v % 50 == 0 else (0, 120, 120)
        cv2.line(cr, (0, Y), (cr.shape[1], Y), c if v % 50 == 0 else (0, 90, 160), 1)
        if v % 50 == 0: cv2.putText(cr, str(v), (2, Y - 2), 0, 0.4, (0, 255, 255), 1)
    cv2.imwrite(out, cr)
if __name__ == "__main__":
    a = sys.argv; zoom(a[1], int(a[2]), int(a[3]), int(a[4]), int(a[5]), float(a[6]), a[7], step=int(a[8]) if len(a) > 8 else 10)
