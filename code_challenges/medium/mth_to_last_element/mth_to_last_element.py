# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 17:33:56 2016

@author: ryankeenan
"""
#challenge description: https://www.codeeval.com/open_challenges/10/
import sys
file = open(sys.argv[1], 'r')
lines = file.readlines()

for line in lines:
    
    items = line.split()
    num = int(items.pop(-1))
    items = items[::-1]
    if num <= len(items): print(items[num-1])
    
file.close()