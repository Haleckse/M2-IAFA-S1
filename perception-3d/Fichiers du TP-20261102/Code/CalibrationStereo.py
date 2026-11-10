# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import

import os
import matplotlib.pyplot as plt
import numpy as np
import cv2
import glob
import CalibUtils
from CalibTools import *

#Get Left and Right images
viewsLeft, image_namesLeft = getImages(os.path.join("data\\calibration_nav_3003\\NAV\\Calib", '*_0.png'));
viewsRight, image_namesRight = getImages(os.path.join("data\\calibration_nav_3003\\NAV\\Calib", '*_1.png'));

imgCalibLeft = []
imgPointsLeft = []
imgNameLeft = []

imgCalibRight = []
imgPointsRight = []
imgNameRight = []

objectPoints = []
idx=0

print(viewsLeft[1].shape[0:2])
imgSize = viewsLeft[1].shape[0:2];

#For each image pair
for view in viewsLeft:
    print("Left: "+image_namesLeft[idx])
    #Detect calibration pattern in the left image
    patternFoundLeft, imgPointLeft = detectPattern(viewsLeft[idx], cols = 7, rows = 15)
    if patternFoundLeft:
        print("Right: "+ image_namesRight[idx])
        #Detect calibration pattern in the right image only if it has been found in the left one
        patternFoundRight, imgPointRight = detectPattern(viewsRight[idx], cols = 7, rows = 15)
        if patternFoundRight:
            imgNameLeft.append(image_namesLeft[idx])
            imgNameRight.append(image_namesRight[idx])
            imgCalibLeft.append(view)
            imgCalibRight.append(viewsRight[idx])
            imgPointsLeft.append(imgPointLeft)
            imgPointsRight.append(imgPointRight)

            #Add corresponding object points
            objectPoints.append(asymmetricWorldPoints(cols = 7, rows = 15, patternSize_mm = 85.0))
    idx=idx+1

#Calibrate stereo bench
rms, mtxLeft, distLeft, mtxRight, distRight, R, T, rvecs, tvecs, pve = calibrateStereo(objectPoints, imgPointsLeft, imgPointsRight, imgSize)

print('\nRMS:', rms)
print('Left Camera matrix:\n', mtxLeft)
print('Left Distortion coefficients: ', distLeft.ravel())
print('Right Camera matrix:\n', mtxRight)
print('Right Distortion coefficients: ', distRight.ravel())
print('Rotation matrix: \n',R)
print('Translation matrix: \n',T)

plotRMS(pve, rms, imgNameLeft, figureName = 'RMS Plot')

mapxLeft, mapyLeft, mapxRight, mapyRight = computeCorrectionMapsStereo(imgSize, mtxLeft, distLeft, mtxRight, distRight, R, T, alpha = 1.0, xRatio = 1, yRatio = 1)
idx = 0
for view in viewsLeft:
    resultLeft = rectify(viewsLeft[idx], mapxLeft, mapyLeft);
    resultRight = rectify(viewsRight[idx], mapxRight, mapyRight);
    
    display = cv2.hconcat([resultLeft, resultRight])       
    for i in range(0, 20):
        display = cv2.line(display, (0, int(i*display.shape[1::-1][1]/20)), (display.shape[1::-1][0]-1, int(i*display.shape[1::-1][1]/20)), (0, 0, 200))
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.imshow(display)
    plt.show()
    idx = idx+1

#Load test stereo pair
imgLeft = cv2.imread("data\\calibration_nav_3003\\Test\\left_2.png", cv2.IMREAD_GRAYSCALE)
imgRight = cv2.imread("data\\calibration_nav_3003\\Test\\right_2.png", cv2.IMREAD_GRAYSCALE)
imgLeft = cv2.resize(imgLeft, (1024,1024))
imgRight = cv2.resize(imgRight, (1024,1024))
resultLeft = rectify(imgLeft, mapxLeft, mapyLeft);
resultRight = rectify(imgRight, mapxRight, mapyRight);
    
display = cv2.hconcat([resultLeft, resultRight])       
for i in range(0, 20):
    display = cv2.line(display, (0, int(i*display.shape[1::-1][1]/20)), (display.shape[1::-1][0]-1, int(i*display.shape[1::-1][1]/20)), (0, 0, 200))
fig = plt.figure()
ax = fig.add_subplot(111)
plt.imshow(display)
plt.show()

disparity = getDisparity(resultLeft, resultRight)
minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(disparity)
display = cv2.convertScaleAbs(disparity, alpha = (255.0 / maxVal - minVal))
display = cv2.cvtColor(display, cv2.COLOR_GRAY2BGR)
display = cv2.applyColorMap(display, cv2.COLORMAP_JET)

mask = np.copy(disparity)
mask[np.where(disparity <= [10])] = [0]
mask[np.where(disparity > [10])] = [1]             
mask = np.uint8(mask)
disparity = cv2.bitwise_and(display, display, mask = mask)

fig = plt.figure()
plt.title("Disparity map")
ax = fig.add_subplot(111)
plt.imshow(disparity)
plt.show()
