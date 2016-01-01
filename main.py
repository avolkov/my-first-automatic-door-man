
import numpy as np
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import os

from datetime import datetime
import random


BLUR = 15


def getAdjustedThreshhold(cap):

    ret, base = cap.read()
    base = cv2.blur(base, (BLUR, BLUR))
    base = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)

    for i in range(0, 60):

        ret, frame = cap.read()

        frame = cv2.blur(frame, (BLUR, BLUR))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        diff = cv2.absdiff(frame, base)
        ret, diff = cv2.threshold(diff, i, 255, cv2.THRESH_BINARY)

        if cv2.countNonZero(diff) == 0:
            return i + 5

    return i


# START READING HERE
## This assumes that there exists /dev/video0 --> doesn't work with raspberry pi camera
#cap = cv2.VideoCapture(0)

camera = PiCamera()
cap = PiRGBArray(camera)


print "Adjusting..."
threshold = getAdjustedThreshhold(cap)
print "Threshold: " + str(threshold)

print "Starting!"
ret, base = cap.read()
base = cv2.blur(base, (BLUR, BLUR))
base = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)

isSensorActivated = False
wasSensorActivated = False

while True:

    ret, frame = cap.read()

    frame = cv2.blur(frame, (BLUR, BLUR))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    diffFrame = cv2.absdiff(frame, base)

    ret, diffFrame = cv2.threshold(
        diffFrame, threshold, 255, cv2.THRESH_BINARY)

    height, width = diffFrame.shape[:2]

    sensorFrame = diffFrame[
        (height / 5) * 2:(height / 5) * 3, (width / 5) * 2:(width / 5) * 3]

    frameHeight, frameWidth = sensorFrame.shape[:2]
    sensorFramePixels = frameHeight * frameWidth

    if cv2.countNonZero(sensorFrame) > sensorFramePixels * 0.4:
        isSensorActivated = True
    else:
        isSensorActivated = False

    if isSensorActivated and not wasSensorActivated:

        #sensor stuff happening here



    wasSensorActivated = isSensorActivated

    cv2.rectangle(diffFrame, ((width / 5) * 2, (height / 5) * 2),
                  ((width / 5) * 3, (height / 5) * 3), (255, 255, 255), 1)
    cv2.imshow('diff', diffFrame)

    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break


cap.release()
cv2.destroyAllWindows()
