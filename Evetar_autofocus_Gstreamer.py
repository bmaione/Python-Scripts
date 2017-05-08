#import libs
import cv2
import numpy as np
import os
import time 
from matplotlib import pyplot as plt
from scipy import stats as st
import sys, select, os
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor, Evetar_FocusMotor
import atexit



sensorid="0"


cmd="gst-launch-1.0 udpsrc port=5000 num-buffers=1000 ! application/x-rtp,encoding-name=JPEG,payload=26 ! rtpjpegdepay ! filesink location=test.jpg"
ev = Evetar_FocusMotor()

def Focusin(nsteps):
    ev.moveBackward(nsteps)
def Focusout(nsteps):
    ev.moveForward(nsteps)
def getpos():
    status,loc=ev.queryPos()
    return loc
def gotofocuspos(position):
    status,loc=ev.queryPos()
    diff = loc - position
    if diff < 0:
        ev.moveBackward(np.abs(diff))
    elif diff > 0:
        ev.moveForward(np.abs(diff))
    else:
        b = 0
# %%
# Loop to grab frame and analyze focus
i=0
#send a command to bring lens to near far focus
gotofocuspos(0)
time.sleep(3)
#initialize the step size
nstep = 100
#define the scanlength for the coarse search
scanlength = 2300/nstep
contrasttrack = np.zeros([1,scanlength],dtype=np.double)
steptrack = np.zeros([1,scanlength],dtype=np.double)
#Do a coarse search
while i in range(0,scanlength):
    # Issue command to grab frame
    steptrack[0,i] = getpos()
    os.system(cmd)
    # Load the frame, this will be replaced w/ most recent JPG from stream
    img=cv2.imread('test.jpg',0)
    med = np.median(img)
    delt = .5
    # Filtered image used to determine focus quality

    edges = cv2.Canny(img,(1-delt)*med,(1+delt)*med)         
    edgesc = np.double(edges)/255
    print(np.max(edges))
    # Single valued metric to asses the quality of focus
    contrast = np.sum(edgesc)/np.size(edgesc)
    contrasttrack[0,i] = contrast
  
    # Small images used for display
    img_sm=cv2.resize(img,(0,0),fx=0.25,fy=0.25)
    edges_sm=cv2.resize(edges,(0,0),fx=0.25,fy=0.25)
    #display the images to screen
    display = cv2.hconcat((img_sm, edges_sm))
    cv2.imshow('image',display)
#    cv2.imshow('edges',edges_sm)
    #Output the current metric value
    print 'Current metric value: '+np.str(contrast)
    print np.str(steptrack[0,i])
    time.sleep(1)
    cv2.waitKey(25)        

    Focusin(np.uint(nstep))
    time.sleep(.25)
    i += 1
#Find the best focus position
bestpos = steptrack[0,np.argmax(contrasttrack[0,:])]
print 'best position: '+np.str(bestpos)
#return to this best focus positon
gotofocuspos(0)
time.sleep(5)
gotofocuspos(bestpos)
#recalculate the focus metric
cv2.destroyAllWindows()
# %%
os.system(cmd)
# Load the frame, this will be replaced w/ most recent JPG from stream
img=cv2.imread('test.jpg',0)
cv2.imshow('image',img)
cv2.waitKey(10000)
cv2.destroyAllWindows()
