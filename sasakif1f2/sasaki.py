import numpy as np
import os
import math
import matplotlib
#matplotlib.use('Agg')


import matplotlib.pyplot as plt
from scipy import interpolate

tex = open("f1f2_Sasaki.dat")
lines = tex.readlines()

for i in range(len(lines)):
    if (lines[i][0] == "#") and (lines[i][1] == "S"):
        ll = lines[i].split()
        AtomNum = int(ll[1])
        outname = "f1f2_" + str(AtomNum) + ".dat"
        out = open(outname, "w")
        
        for j in range(i+5, len(lines)):
            if lines[j][0]=="#":
                break
            else:
                outtemp = lines[j].split()
                outl = outtemp[0]+ " " + outtemp[1] + " " + outtemp[2] + "\n"
                out.write(outl)
        out.close()
        