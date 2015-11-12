import numpy as np
import cv2
import os
from BluetoothSurveyor import BluetoothSurveyor
import subprocess
from datetime import datetime
import random


BLUR = 15
knownPeople = {'42:4B:F9:AB:0D:5C' : ("Thiago", "Old sport")}
presetMessages = ["Nice weather today isn't it,", "Nice shirt,", "Have a wonderful day,", "Nice to see you here,", "I'm running out of greetings again",
                  "I'm not being paid enough for this", "Good morning. No.   Wait. Good afternoon. No.   Wait. Good morning. No.    Wait. Nevermind", "I think I've saw you before"]

def getAdjustedThreshhold(cap):

    ret, base = cap.read()
    base = cv2.blur(base,(BLUR,BLUR))
    base = cv2.cvtColor(base,cv2.COLOR_BGR2GRAY)

    for i in range(0, 60):

        ret, frame = cap.read()

        frame = cv2.blur(frame,(BLUR,BLUR))
        frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

        diff = cv2.absdiff(frame, base)
        ret, diff = cv2.threshold(diff, i, 255, cv2.THRESH_BINARY)

        if cv2.countNonZero(diff) == 0:
            return i + 5

    return i

def getGreetingMessage(callingName):

    message = ''

    rand = int (random.random() * 2)

    if rand == 0: # time based greeting
        currentHour = datetime.now().hour
        if currentHour >= 5 and currentHour <= 11:
            message += "Good morning,"
        elif currentHour >= 12 and currentHour <= 5:
            message += "Good afternoon,"
        elif currentHour >= 6 and currentHour <= 9:
            message += "Good evening,"
        else:
            message += "Good night,"
    else: # vague greeting
        message += presetMessages[ (int) (random.random() * len(presetMessages)) ]


    if callingName is not None:
        message += " " + callingName

    return message


###### START READING HERE ##########
cap = cv2.VideoCapture(0)
bluetoothSurveyor = BluetoothSurveyor()

print "Adjusting..."
threshold = getAdjustedThreshhold(cap)
print "Threshold: " + str(threshold)

print "Starting!"
ret, base = cap.read()
base = cv2.blur(base, (BLUR,BLUR))
base = cv2.cvtColor(base,cv2.COLOR_BGR2GRAY)

isSensorActivated = False
wasSensorActivated = False

while True:

    ret, frame = cap.read()

    frame = cv2.blur(frame, (BLUR,BLUR))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    diffFrame = cv2.absdiff(frame, base)

    ret, diffFrame = cv2.threshold(diffFrame, threshold, 255, cv2.THRESH_BINARY)

    height, width = diffFrame.shape[:2]

    sensorFrame = diffFrame[(height/5)*2:(height/5)*3, (width/5)*2:(width/5)*3]

    frameHeight, frameWidth = sensorFrame.shape[:2]
    sensorFramePixels = frameHeight * frameWidth

    if cv2.countNonZero(sensorFrame) > sensorFramePixels * 0.4:
        isSensorActivated = True
    else:
        isSensorActivated = False

    if isSensorActivated and not wasSensorActivated:

        greeted = False
        message = ''

        for mac in knownPeople:
            lastTime = bluetoothSurveyor.getDeviceLastSeenAgeInSecondsByMAC(mac)

            if lastTime is not None and lastTime < 180: # known person found
                message = getGreetingMessage(knownPeople[mac][1])
                greeted = True
                break

        if not greeted:
            message = getGreetingMessage(None)
        else:
            del knownPeople[mac]

        process1 = subprocess.Popen(["echo", message], stdout=subprocess.PIPE)
        process2 = subprocess.Popen(["text2wave"], stdin=process1.stdout, stdout=subprocess.PIPE)
        subprocess.Popen(["play", "-t", "wav", "-", "tempo", str(0.8), "pitch", str(-100)], stdin=process2.stdout)


    wasSensorActivated = isSensorActivated

    cv2.rectangle(diffFrame, ((width/5)*2,(height/5)*2), ((width/5)*3,(height/5)*3), (255, 255, 255), 1)
    cv2.imshow('diff', diffFrame)

    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break


cap.release()
cv2.destroyAllWindows()