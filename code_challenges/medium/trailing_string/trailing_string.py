# -*- coding: utf-8 -*-
"""
Created on Sun Feb 21 09:42:12 2016

@author: ryankeenan
"""
#challenge description: https://www.codeeval.com/open_challenges/32/
import sys
file = open(sys.argv[1], 'r')

lines = file.readlines()

for line in lines:
    
    line = line.replace('\n','')
    line = line.strip()
    strs = line.split(',')
    str1 = strs[0][::-1]
    str2 = strs[1][::-1]
    
    if str1[:len(str2)] == str2:
        print(1)
    else:
        print(0)
        
file.close()
    
    