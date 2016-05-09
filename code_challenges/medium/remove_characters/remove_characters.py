# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 19:46:48 2016

@author: ryankeenan
"""
#challenge description: https://www.codeeval.com/open_challenges/13/

import sys
file = open(sys.argv[1], 'r')

lines = file.readlines()

for line in lines:
    
    line = line.replace('\n','')
    line = line.strip()
    strings = line.split(',')

    string1 = strings[0].strip()
    chars = strings[1].strip()
    
    for char in chars:
        string1 = string1.replace(char, '')
    
    
    print(string1)
    

    
    
file.close()