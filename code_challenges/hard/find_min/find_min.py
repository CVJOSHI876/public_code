# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 17:30:45 2016

@author: ryankeenan
"""
#challenge description: https://www.codeeval.com/open_challenges/85/

import sys
file = open(sys.argv[1], 'r')
#file = open('nth_element.txt', 'r')

lines = file.readlines()

#for line in lines:
#    print(line)
#print(bullshit)    
    
for line in lines:
    
    line = line.replace('\n', '')
    line.strip()
    if line != '':
        
        #init_values will be [n, k, a, b, c, r]
        #m[0] = a
        #m[i] = (b*m[i-1] + c) % r, 0 < i < k
        n, k, a, b, c, r = [int(x) for x in line.strip().split(',')]
        #print('n,k,a,b,c,r = ', n, k, a, b, c, r)
        m = []
        m.append(a) #assigns m[0] = a
        for idx in range(1, k):
            m.append(((b*m[idx-1]) + c) % r)
        
        #print(m)
        for idx in range(k, n):
            mconsidered = m[idx-k:]
            found_mofidx = False
            checkval = 0
            
            while not found_mofidx:
                if checkval not in mconsidered:
                    m.append(checkval)
                    found_mofidx = True
                else:
                    checkval += 1
        
        print(m[len(m)-1])
        
file.close()