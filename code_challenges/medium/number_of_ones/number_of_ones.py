# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 19:51:42 2016

@author: ryankeenan
"""
#challenge description: https://www.codeeval.com/open_challenges/16/

import sys
file = open(sys.argv[1], 'r')

lines = file.readlines()

for line in lines:
    
    line = line.replace('\n','')
    line = line.strip()
    binnumber = bin(int(line))[2:]
    print(binnumber.count('1'))
    
file.close()