# -*- coding: utf-8 -*-
import cv2

body_cascade = cv2.CascadeClassifier('haarcascade_fullbody.xml')

cap = cv2.VideoCapture('MallMovie.mp4')
fgbg = cv2.createBackgroundSubtractorMOG2()
font = cv2.FONT_HERSHEY_SIMPLEX

while 1:
    ret, img = cap.read()
    fgmask = fgbg.apply(img)   
    peeps = body_cascade.detectMultiScale(img, 1.03,2)

    for (x,y,w,h) in peeps:
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)

    cv2.putText(img, 'People Counted = '+str(len(peeps)), (0,50), font,
                1.5, (0,255,0), 3, cv2.LINE_AA)
    cv2.imshow('img',img)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()
