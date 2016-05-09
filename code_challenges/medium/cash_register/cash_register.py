# -*- coding: utf-8 -*-
"""
Created on Sun Feb 21 10:01:04 2016

@author: ryankeenan
"""
#challenge description: https://www.codeeval.com/open_challenges/54/

import sys

def n_bills_cents(amount, denom, addstring, changestring):
    
    if amount >= denom:
        nbc = int(amount/denom)
        
        for idx in range(1, nbc+1):
            changestring += addstring
        
        amount = amount - denom*nbc
    
    return amount, changestring

    
    
dollar_strings = ['ONE HUNDRED,','FIFTY,','TWENTY,','TEN,','FIVE,','TWO,','ONE,']
dollar_denom = [100.,50.,20.,10.,5.,2.,1.]
cents_strings = ['HALF DOLLAR,','QUARTER,','DIME,','NICKEL,','PENNY,'] 
cents_denom = [50,25,10,5,1]

file = open(sys.argv[1], 'r')

lines = file.readlines()

for line in lines:
    
    line = line.replace('\n','')
    line = line.strip()
    if line != '':
        
        nums = line.split(';')
        num1 = float(nums[0])
        num2 = float(nums[1])

        change = num2 - num1
        
        if change < 0:
            print('ERROR')
        elif change == 0:
            print('ZERO')            
        elif change > 0:
            changestring = ''
            
            dollars = float(int(change))
            cents = round((change-dollars)*100)
            
            if dollars > 0:
                for idx, item in enumerate(dollar_strings):                    
                    dollars, changestring = n_bills_cents(dollars, dollar_denom[idx],
                                                   dollar_strings[idx], changestring)
 
            if cents > 0:
                for idx, item in enumerate(cents_strings):                    
                    cents, changestring = n_bills_cents(cents, cents_denom[idx],
                                                   cents_strings[idx], changestring)
     
            out = changestring.rstrip(',')        
            print(out)
            
            
file.close()
                        
            
            
                
