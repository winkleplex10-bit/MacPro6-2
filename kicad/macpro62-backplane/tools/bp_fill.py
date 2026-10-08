"""Refill all zones in place: python3 tools/bp_fill.py BOARD"""
import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1]); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1], b); print("filled")
