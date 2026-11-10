# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import

import os
import matplotlib.pyplot as plt
import numpy as np
import cv2
import glob
import CalibUtils

def getImages(root_path):
    image_names = sorted(glob.glob(root_path))
    views = []
    for image_name in image_names:
        views.append(cv2.imread(image_name))
    return views, image_names

def detectPattern(frame, cols = 6, rows = 7):
    patternFound = False
    imgPoints = []

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # 1.1.1.2 - Implémenter la fonction findChessboardCorners ou findCircleGrid en fonction du type de mire utilisé
    # C'est à vous de jouer!!!
    patternFound, imgPoints = cv2.findCirclesGrid(gray, (cols, rows), flags=cv2.CALIB_CB_ASYMMETRIC_GRID)

    if patternFound:
        result = cv2.drawChessboardCorners(frame.copy(), (cols, rows), imgPoints, patternFound)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.imshow(result)
        plt.show()
    return patternFound, imgPoints

def asymmetricWorldPoints(cols = 7, rows = 6, patternSize_mm = 1.0):
    patternPoints = []
    
    #1.1.2.1 - Créer une liste de points 3D correspondant à chaque point de la mire
    # C'est à vous de jouer!!!
    for i in range(rows):
        for j in range(cols):
            patternPoints.append([2 * j + i % 2, i, 0])
                
    return np.array(patternPoints).astype('float32') * patternSize_mm

def calibrateMono(objpoints, imgpoints, imgSize):
    ret = 0
    mtx = []
    dist = []
    rvecs = []
    tvecs = []
    pve = []

    #1.1.2.2 - Implémenter la fonction calibrateCameraExtended
    # C'est à vous de jouer!!!
    ret, mtx, dist, rvecs, tvecs, stdDeviationsIntrinsics, stdDeviationsExtrinsics, pve = cv2.calibrateCameraExtended(
        objpoints, imgpoints, imgSize, None, None
    )
    return ret, mtx, dist, rvecs, tvecs, pve

def computeCorrectionMapsMono(imageSize, mtx, dist, alpha = 1.0, xRatio = 1, yRatio = 1):
    mapx = []
    mapy = []
    newImageSize = (int(imageSize[0] / xRatio), int(imageSize[1] / yRatio))

    h,  w = imageSize[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

    # 1.1.3.1 - Implement initUndistortRectifyMap here
    # C'est à vous de jouer!!!
    mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, newImageSize, cv2.CV_32FC1)

    return mapx, mapy

def rectify(frame, mapx, mapy):
    dst = []
    # 1.1.3.2 - Implement remap here
    # C'est à vous de jouer!!!
    dst = cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR)
    return dst

def calibrateStereo(objpoints, imgpointsLeft, imgPointsRight, imgSize):
    ret = 0
    mtxLeft = []
    distLeft = []
    mtxRight = []
    distRight = []
    R = []
    T = []
    rvecs = []
    tvecs = []
    pve = []

    #2.1.1 - Implémenter la fonction calibrateCameraExtended
    # C'est à vous de jouer!!!
    retLeft, mtxLeft, distLeft, rvecsLeft, tvecsLeft, _, _, pveLeft = cv2.calibrateCameraExtended(
        objpoints, imgpointsLeft, imgSize, None, None
    )
    retRight, mtxRight, distRight, rvecsRight, tvecsRight, _, _, pveRight = cv2.calibrateCameraExtended(
        objpoints, imgPointsRight, imgSize, None, None
    )

    #2.1.1 - Implémenter la fonction stereoCalibrateExtended
    # C'est à vous de jouer!!!
    ret, mtxLeft, distLeft, mtxRight, distRight, R, T, E, F, rvecs, tvecs, pve = cv2.stereoCalibrateExtended(
        objpoints, imgpointsLeft, imgPointsRight, mtxLeft, distLeft, mtxRight, distRight, imgSize, None, None
    )
    return ret, mtxLeft, distLeft, mtxRight, distRight, R, T, rvecs, tvecs, pve


def computeCorrectionMapsStereo(imageSize, mtxLeft, distLeft, mtxRight, distRight, R, T, alpha = 1.0, xRatio = 1, yRatio = 1):
    newImageSize = (int(imageSize[0] / xRatio), int(imageSize[1] / yRatio))

    h,  w = imageSize[:2]
    # 2.2.1 - Implement stereoRectify here
    # C'est à vous de jouer!!!
    R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(
        mtxLeft, distLeft, mtxRight, distRight, (w, h), R, T, alpha=alpha, newImageSize=newImageSize
    )

    # 2.2.2 - Implement initUndistortRectifyMap here
    # C'est à vous de jouer!!!
    mapxLeft, mapyLeft = cv2.initUndistortRectifyMap(mtxLeft, distLeft, R1, P1, newImageSize, cv2.CV_32FC1)
    mapxRight, mapyRight = cv2.initUndistortRectifyMap(mtxRight, distRight, R2, P2, newImageSize, cv2.CV_32FC1)

    return mapxLeft, mapyLeft, mapxRight, mapyRight


def visualizeBoards(mtx, rvecs, tvecs, rows, cols, patternSize_mm, cameraWidth = 0.1, cameraHeight = 0.05):       
    figureName = 'Calibration boards visualization in camera frame'
    
    # Plot settings
    fig = plt.figure(figureName)
    ax = fig.add_subplot(111, projection='3d')
    ax.set_title(figureName)
    ax.set_xlabel('x')
    ax.set_ylabel('z')
    ax.set_zlabel('-y')
    
    CalibUtils.plot_camera_frame(ax, rvecs, tvecs, mtx, cameraWidth, cameraHeight)
    CalibUtils.plot_board_frames(ax, rvecs, tvecs, cols, rows, patternSize_mm)
    CalibUtils.set_axes_equal(ax) 
    plt.show()

def plotRMS(pve, rms, imgNames, figureName = 'RMS Plot'):
    # Plot settings
    plt.figure(figureName)
    plt.title(figureName)
    plt.xlabel('Image ID')
    plt.ylabel('RMS')
    
    x = [os.path.splitext(os.path.basename(image))[0] for image in imgNames]
    
    if len(pve[0]) == 2:
        plt.scatter(x, [rms[0] for rms in pve], label='Per image RMS (Left Camera)', marker='o')
        plt.scatter(x, [rms[1] for rms in pve], label='Per image RMS (Right Camera)', marker='o')
    else:
        plt.scatter(x, pve, label='Per image RMS', marker='o')
    
    plt.plot(x, [rms]*len(imgNames), label='Mean RMS', linestyle='--')
    plt.legend(loc='upper right')
    plt.show()



def getDisparity(left, right):
    stereo = cv2.StereoSGBM_create(
        minDisparity=1,
        numDisparities=256, 
        blockSize=15,
        uniquenessRatio=5,
        speckleWindowSize=5,
        speckleRange=5,
        disp12MaxDiff=2)
    
    disparity = stereo.compute(left,right)

    return disparity