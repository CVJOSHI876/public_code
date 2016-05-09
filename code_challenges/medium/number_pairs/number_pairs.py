# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 20:33:42 2016

@author: ryankeenan
"""
#challenge description: https://www.codeeval.com/open_challenges/34/
import sys
file = open(sys.argv[1], 'r')
#file = open('pairsums.txt', 'r')

lines = file.readlines()

for line in lines:
    
    line = line.replace('\n','')
    line = line.strip()
    goodies = line.split(';')
    nums = goodies[0].split(',')
    numsum = int(goodies[1])
    pairs = ''    
    for idx, item in enumerate(nums):
        current_nums = nums[idx+1:]
        intitem = int(item)
        if intitem < numsum:
            diff = numsum - intitem
            if str(diff) in current_nums:
                if pairs == '':
                    pairs = pairs + item + ',' + str(diff)
                else:
                    pairs = pairs + ';' + item + ',' + str(diff)
        
        
    if pairs == '':
        pairs = 'NULL'
    
    print(pairs)

    
file.close()