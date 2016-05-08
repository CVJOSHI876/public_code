# -*- coding: utf-8 -*-
import numpy as np
import cv2
import osax

hand_cascade = cv2.CascadeClassifier('Hand.Cascade.1.xml')

cap = cv2.VideoCapture(0)
font = cv2.FONT_HERSHEY_SIMPLEX
xvals=[]
yvals=[]
currentx = -1
currenty = -1

sa = osax.OSAX()
sa.set_volume(0)
settings = sa.get_volume_settings()
keys = list(settings.keys())
currentvol = settings[keys[2]]
waiting = 0
volume_increment = 7/100.

while 1:
    waiting += 1
    ret, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hands = hand_cascade.detectMultiScale(gray, 1.3, 5)

    if len(hands) > 0:
        for (x,y,w,h) in hands:
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)

        x1 = hands[0][0]
        y1 = hands[0][1]
        xvals.append(x1)
        yvals.append(y1)
        

        if len(yvals) > 2:
            if currenty == -1:
                currentx = np.mean(xvals)
                currenty = np.mean(yvals)

            newy = np.mean(yvals)
            yoffset = newy - currenty

            if yoffset > 3:
                currentvol -= 10
                currentvol = np.clip(currentvol, 0, 100)
                voladjusted = currentvol*volume_increment
                sa.set_volume(voladjusted)
                print('New Volume = ',currentvol, 'yoffset', yoffset)
                currenty = int(newy)
                xvals = []
                yvals = []
                
            if yoffset < -3:
                currentvol += 10
                currentvol = np.clip(currentvol, 0, 100)
                voladjusted = currentvol*volume_increment
                sa.set_volume(voladjusted)
                print('New Volume = ',currentvol, 'yoffset', yoffset)
                currentx = int(newy)
                xvals = []
                yvals = []
                       
        cv2.putText(img, 'Volume = '+str(currentvol), (0,50), font,
                1.5, (0,255,0), 3, cv2.LINE_AA)
            
    cv2.imshow('img',img)
    
    if waiting > 25:
        xvals=[]
        yvals=[]
        currentx = -1
        currenty = -1
        waiting = 0
        
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()
