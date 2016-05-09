# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 15:36:11 2016

@author: ryankeenan
"""

#challenge description: https://www.codeeval.com/open_challenges/7/
import sys
file = open(sys.argv[1], 'r')
#file = open('prefix.txt', 'r')
lines = file.readlines()

class stack():
    
    def __init__(self):
        self.content = []
        
    def isempty(self):
        return self.content == []
        
    def push(self, item):
        self.content.append(item)
        
    def pop(self):
        return self.content.pop()
    
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

for idx, line in enumerate(lines):
    
#    badchar = False
#    offenders = []
    line = line.replace('\n','')
    line = line.strip()
    if line != '':
        mylist = line.split()[::-1]
#        for idx, elem in enumerate(mylist):
#            elem = elem.strip()
#            if idx in [0,1] and is_number(elem) == False:
#                badchar = True
#                offenders.append(elem+' (non-number in first two elements)')
#            if is_number(elem) == False and elem not in ['+','/','*']:
#                badchar = True
#                offenders.append(elem)
                
#        if badchar == False:
            
        mystack = stack()
        for elem in mylist:
            
            elem = elem.strip()
            if is_number(elem):
                mystack.push(int(elem))
                #print('pushed:',elem)
            elif elem == '+':
                pop2 = mystack.pop()
                pop1 = mystack.pop()
                result = float(pop2) + float(pop1)
                mystack.push(result)
                #print(pop2,'+',pop1)
                
            elif elem == '*':
                pop2 = mystack.pop()
                pop1 = mystack.pop()
                result = float(pop2) * float(pop1)
                mystack.push(result)
                #print(pop2,'*',pop1)
                
            elif elem == '/':
                pop2 = mystack.pop()
                pop1 = mystack.pop()
                result = float(pop2) / float(pop1)
                mystack.push(result)
                #print(pop2,'/',pop1,'=',result)
        
        out = mystack.content[0]        
        if out >= 0 and idx <= 39 and out == int(out): print(int(out))
    
        #else:
            
        #    print('Found bad character(s)! = ',offenders)
        
file.close()
                        