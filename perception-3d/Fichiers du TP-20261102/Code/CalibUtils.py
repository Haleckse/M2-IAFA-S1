# -*- coding: utf-8 -*-
from matplotlib import cm
from numpy import linspace
import numpy as np
import cv2 as cv

## Misc
def nullFunction(x = None, y = None):
    pass

## 3-D plotting
def set_axes_radius(ax, origin, radius):
    ax.set_xlim3d([origin[0] - radius, origin[0] + radius])
    ax.set_ylim3d([origin[1] - radius, origin[1] + radius])
    ax.set_zlim3d([origin[2] - radius, origin[2] + radius])
    
def set_axes_equal(ax):
    '''Make axes of 3D plot have equal scale so that spheres appear as spheres,
    cubes as cubes, etc..  This is one possible solution to Matplotlib's
    ax.set_aspect('equal') and ax.axis('equal') not working for 3D.

    Input
      ax: a matplotlib axis, e.g., as output from plt.gca().
    '''

    limits = np.array([
        ax.get_xlim3d(),
        ax.get_ylim3d(),
        ax.get_zlim3d(),
    ])

    origin = np.mean(limits, axis=1)
    radius = 0.5 * np.max(np.abs(limits[:, 1] - limits[:, 0]))
    set_axes_radius(ax, origin, radius)
    
def transform_to_matplotlib_frame(cMo, X):
    # util function
    M = np.identity(4)
    M[1,1] = 0
    M[1,2] = 1
    M[2,1] = -1
    M[2,2] = 0

    return M.dot(cMo.dot(X))

def create_camera_model(camera_matrix, width, height, draw_frame_axis=True):
    # util function
    # fx = camera_matrix[0,0]
    # fy = camera_matrix[1,1]
    # focal = (fx + fy) /2
    f_scale =  0.1 #focal / 100

    # draw image plane
    X_img_plane = np.ones((4,5))
    X_img_plane[0:3,0] = [-width, height, f_scale]
    X_img_plane[0:3,1] = [width, height, f_scale]
    X_img_plane[0:3,2] = [width, -height, f_scale]
    X_img_plane[0:3,3] = [-width, -height, f_scale]
    X_img_plane[0:3,4] = [-width, height, f_scale]
    
    # draw triangle above the image plane
    X_triangle = np.ones((4,3))
    X_triangle[0:3,0] = [-width, -height, f_scale]
    X_triangle[0:3,1] = [0, -2*height, f_scale]
    X_triangle[0:3,2] = [width, -height, f_scale]

    # draw camera
    X_center1 = np.ones((4,2))
    X_center1[0:3,0] = [0, 0, 0]
    X_center1[0:3,1] = [-width, height, f_scale]

    X_center2 = np.ones((4,2))
    X_center2[0:3,0] = [0, 0, 0]
    X_center2[0:3,1] = [width, height, f_scale]

    X_center3 = np.ones((4,2))
    X_center3[0:3,0] = [0, 0, 0]
    X_center3[0:3,1] = [width, -height, f_scale]

    X_center4 = np.ones((4,2))
    X_center4[0:3,0] = [0, 0, 0]
    X_center4[0:3,1] = [-width, -height, f_scale]

    return [X_img_plane, X_triangle, X_center1, X_center2, X_center3, X_center4]

def create_board_model(board_width, board_height, square_size):
    # util function
    width = board_width*square_size
    height = board_height*square_size

    # draw calibration board
    X_board = np.ones((4,5))
    X_board[0:3,0] = [0,0,0]
    X_board[0:3,1] = [width,0,0]
    X_board[0:3,2] = [width,height,0]
    X_board[0:3,3] = [0,height,0]
    X_board[0:3,4] = [0,0,0]

    # draw board frame axis
    X_frame1 = np.ones((4,2))
    X_frame1[0:3,0] = [0, 0, 0]
    X_frame1[0:3,1] = [height/2, 0, 0]

    X_frame2 = np.ones((4,2))
    X_frame2[0:3,0] = [0, 0, 0]
    X_frame2[0:3,1] = [0, height/2, 0]

    X_frame3 = np.ones((4,2))
    X_frame3[0:3,0] = [0, 0, 0]
    X_frame3[0:3,1] = [0, 0, height/2]

    return [X_board, X_frame1, X_frame2, X_frame3]

def plot_camera_frame(ax, rvecs, tvecs, cam_matrix, cam_width = 10.0, cam_height = 5.0,):
    extrinsics = np.zeros((len(rvecs),6))
    for i in range(0, len(rvecs)):
        extrinsics[i]=np.append(rvecs[i].flatten(), tvecs[i].flatten())

    camera_frame = create_camera_model(cam_matrix, cam_width, cam_height)

    for i in range(len(camera_frame)):
        X = np.zeros(camera_frame[i].shape)
        for j in range(camera_frame[i].shape[1]):
            X[:,j] = transform_to_matplotlib_frame(np.eye(4), camera_frame[i][:,j])
        ax.plot3D(X[0,:], X[1,:], X[2,:], color='r')
        
def plot_board_frames(ax, rvecs, tvecs, cols, rows, pattern_size):
    extrinsics = np.zeros((len(rvecs),6))
    for i in range(0, len(rvecs)):
        extrinsics[i]=np.append(rvecs[i].flatten(), tvecs[i].flatten())
        
    board_frames = create_board_model(cols, rows, pattern_size)
    
    cm_subsection = linspace(0.0, 1.0, extrinsics.shape[0])
    colors = [ cm.jet(x) for x in cm_subsection ]

    for idx in range(extrinsics.shape[0]):
        R, _ = cv.Rodrigues(extrinsics[idx,0:3])
        cMo = np.eye(4,4)
        cMo[0:3,0:3] = R
        cMo[0:3,3] = extrinsics[idx,3:6]
        for i in range(len(board_frames)):
            X = np.zeros(board_frames[i].shape)
            for j in range(board_frames[i].shape[1]):
                X[0:4,j] = transform_to_matplotlib_frame(cMo, board_frames[i][0:4,j])
            ax.plot3D(X[0,:], X[1,:], X[2,:], color=colors[idx])