# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import

import os
import matplotlib.pyplot as plt
import numpy as np
import cv2
import glob
import CalibUtils
from CalibTools import *


def calibrate(path):
    #Get list of images
    views, image_names = getImages(path);

    imgCalib = []
    objectPoints = []
    imgPoints = []
    imgName = []
    idx=0

    imgSize = views[1].shape[0:2];
    print(imgSize)

    #For each image
    for view in views:
        #Detect calibration pattern
        patternFound, corners = detectPattern(view, cols = 7, rows = 15)
        if patternFound:
            imgName.append(image_names[idx])
            idx=idx+1
            imgCalib.append(view)
            imgPoints.append(corners)

            #Add corresponding object points
            objectPoints.append(asymmetricWorldPoints(cols = 7, rows = 15, patternSize_mm = 85.0))

    #Calibrate camera
    rms, mtx, dist, rvecs, tvecs, pve = calibrateMono(objectPoints, imgPoints, imgSize)

    #Show pattern pose with respect to camera
    visualizeBoards(mtx, rvecs, tvecs, cols = 7, rows = 15, patternSize_mm = 85.0, cameraWidth = 0.1, cameraHeight = 0.05)

    print('\nRMS:', rms)
    print('Camera matrix:\n', mtx)
    print('Distortion coefficients: ', dist.ravel())

    #Compute correction maps
    mapx, mapy = computeCorrectionMapsMono(imgSize, mtx, dist, alpha = 1.0, xRatio = 1, yRatio = 1)

    #For each image
    for view in views:
        #Rectify it
        result = rectify(view, mapx, mapy);
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.imshow(result)
        plt.show()
    
    #Plot RMS for each image
    plotRMS(pve, rms, imgName, figureName = 'RMS Plot')


#Calibration Gauche
calibrate(os.path.join("data\\calibration_nav_3003\\NAV\\Calib", '*_0.png'))


#Calibration Droite
calibrate(os.path.join("data\\calibration_nav_3003\\NAV\\Calib", '*_1.png'))
