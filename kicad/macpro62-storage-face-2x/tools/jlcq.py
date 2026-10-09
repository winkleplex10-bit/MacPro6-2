#!/usr/bin/env python3
"""Query the JLC parts search (public web API used by jlcpcb.com) -> code, basic/ext/pref, stock, price@1, name, package.
   python3 jlcq.py "keyword" [n]"""
import json, sys, urllib.request
def q(kw, n=5):
    req = urllib.request.Request("https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList",
        data=json.dumps({"keyword": kw, "currentPage": 1, "pageSize": n}).encode(), headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
    d = json.load(urllib.request.urlopen(req, timeout=30))
    out = []
    for c in (d.get("data") or {}).get("componentPageInfo", {}).get("list", []) or []:
        t = {"base": "BASIC", "expand": "ext"}.get(c.get("componentLibraryType"), c.get("componentLibraryType"))
        if c.get("preferredComponentFlag"): t += "/PREF"
        p = (c.get("componentPrices") or [{}])[0].get("productPrice")
        out.append((c.get("componentCode"), t, c.get("stockCount"), p, c.get("componentModelEn"), c.get("componentSpecificationEn"), c.get("erpComponentName")))
    return out
if __name__ == "__main__":
    for kw in sys.argv[1:]:
        print("##", kw)
        for r in q(kw, 6): print("  ", r)
