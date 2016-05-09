# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 18:38:48 2016

@author: ryankeenan
"""
#challenge description: https://www.codeeval.com/open_challenges/28/

import sys
import pdb
file = open(sys.argv[1], 'r')
#file = open('substrings.txt', 'r')
lines = file.readlines()

for line in lines:
    
    result = 'false'
    line = line.replace('\n','')
    line = line.rstrip()
    if line != '' and ',' in line:
        
        strings = line.split(',')
        str1 = strings[0]
        str2 = strings[1]
        
        if str1 != '' and str2 != '':
            
            if '\\*' not in str2 and '*' not in str2:
                
                if str2 in str1:
                    result = 'true'
                
            if result == 'false':
            
                if '\\*' in str2: 
                    str2 = str2.replace('\\*', '$')
                
                if '*' in str1:
                    str1 = str1.replace('*', '$')
                    
                if '*' not in str2:
                    if str2 in str1:
                        result = 'true'
                   
            if result == 'false':
            
                if '*' in str2:
                    strings2 = str2.split('*')
                    truth = [0]*len(strings2)
                    currentpos = 0
                    
                    for idx, substr in enumerate(strings2):
                        if idx == 0 and substr == '':
                            truth[idx] = 1
                        elif idx == len(strings2)-1 and substr == '':
                            truth[idx] = 1
                        elif substr in str1:
                            pos = str1.find(substr)
                            if pos != -1 and pos >= currentpos:
                                currentpos = pos + len(substr)
                                truth[idx] = 1
        
                    if 0 not in truth:
                        result = 'true'
                        
                            
            #print(str1, str2, result)
            print(result)
            #if 'amagonna*geti' in line: pdb.set_trace()
            
file.close()