# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 19:01:48 2016

@author: ryankeenan
"""
#challenge_description: https://www.codeeval.com/open_challenges/168/
import sys
import math
#import matplotlib.pyplot as plt
#import pdb

def smoothie(input_list, nsmooth):

    if nsmooth%2 == 0:
        half_interval = int(nsmooth/2)
    else:
        half_interval = int((nsmooth-1)/2)
    
    boxlength = float((2*half_interval) + 1)    
    smoothed_list = []
    #pdb.set_trace()
    for index, elem in enumerate(input_list):
        if index > (half_interval - 1) and index < len(input_list)-(half_interval + 1): 
            smoothed_list.append(sum(input_list[index-half_interval:index+half_interval+1])/boxlength)
        else:
            smoothed_list.append(datalist[index])
    
    return smoothed_list
    
#file = open('signals_ex.txt', 'r')
file = open(sys.argv[1], 'r')

lines = file.readlines()

#for line in lines:
#    print(line)
    
#print(bullshit)

for idx, line in enumerate(lines):

    line = line.replace('\n','')
    line = line.strip()
    if line != '':
        datalist = line.split()
        datalist = [float(elem) for elem in datalist]
            
        datasmooth1 = smoothie(datalist, 3)
        datasmooth2 = smoothie(datasmooth1, 3)
        datasmooth3 = smoothie(datasmooth2, 3)
        #datasmooth4 = smoothie(datasmooth3, 3)
        #datasmooth5 = smoothie(datasmooth4, 3)
        
        gradcludge = []
        for index, elem in enumerate(datasmooth3):
            if index > 0 and index < len(datasmooth3)-2: 
                gradcludge.append(datasmooth3[index+1] - datasmooth3[index-1])
            else: 
                gradcludge.append(0)
        
                 
        gradsmooth1 = smoothie(gradcludge, 3)
        gradsmooth2 = smoothie(gradsmooth1, 3)
        gradsmooth3 = smoothie(gradsmooth2, 3)
        gradsmooth4 = smoothie(gradsmooth3, 3)
        gradsmooth5 = smoothie(gradsmooth4, 3)
        
        peaks = []
        peak_detected = False
        testgs = list(gradsmooth5)
        
        for idx in range(10, len(gradsmooth3)-10):
        
            if testgs[idx-2] > 0 and testgs[idx+2] < 0 and peak_detected == False:
                
                best_avg = math.fabs(sum(gradsmooth5[idx-2: idx+3]))
                peak_detected = True
                
            elif testgs[idx-2] > 0 and testgs[idx+2] < 0 and peak_detected == True:
                mov_avg = math.fabs(sum(gradsmooth5[idx-2: idx+3]))
                if mov_avg < best_avg:
                    best_avg = mov_avg
                else:
                    peaks.append(idx-1)
                    peak_detected = False
                    testgs[:idx+3] = [x*0.0 for x in testgs[:idx+3]]
        
        duration = []
        for idx, elem in enumerate(peaks):
            if idx < len(peaks)-2: duration.append(peaks[idx+1] - elem)
        
        avg_duration = float(sum(duration))/len(duration)
        freq = 1/(avg_duration/20000.)
        round_freq = round(freq/10.)*10
        print(round_freq)            
        
        #plt.plot(datalist, label='original')
        #plt.plot(datasmooth1, label='smooth1')
        #plt.plot(datasmooth2, label='smooth2')
        #plt.plot(datasmooth3, label='smooth3')
        #plt.plot(gradcludge, label='gradient')
        #plt.plot(gradsmooth1, label='smoothed1 gradient')
        #plt.plot(gradsmooth3, label='smoothed3 gradient')
        #plt.plot(gradsmooth5, label='smoothed5 gradient')
        #plt.legend()
        #plt.plot(gradcludge)
        #plt.plot(gradsmooth)
        #plt.show()
        
file.close()