# -*- coding: utf-8 -*-
"""
Created on Sat Jan 20 23:32:47 2018

@author: Oliver
"""

outlaw_start = ['Artist:', 'Album: ', 'Typed by:', 'Song:']
outlaw_mid = """
anonymous/
.html
txt
""".split('\n')

with open('rapdata/hihop.txt', 'r', encoding="latin-1") as filein:
    with open('rapdata/hip_hop.txt', 'w', 1, encoding="utf-8") as fileout:
        for line in filein:
            if len(line) == 0 or line[0].upper() == line[0].lower():
                continue

            for x in outlaw_start:
                if line.startswith(x):
                    continue

            for part in outlaw_mid:
                if part in line.lower():
                    continue
            fileout.write(line)
