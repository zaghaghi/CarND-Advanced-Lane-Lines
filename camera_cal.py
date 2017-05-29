import cv2
import pickle
import numpy as np
import click

class CameraCalibration:
    ''' This class computes camera calibration parameters '''
    def __init__(self):
        self.mtx = None
        self.dist = None

    def compute(self, img_list, force=False):
        ''' computes camera parameters '''
        if not force and self.mtx is not None and self.dist is not None:
            return
        imgpoints = []
        objpoints = []

        objp = np.zeros((9*6, 3), np.float)
        objp[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)
        for img in img_list:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, (9, 6), None)

            if ret:
                imgpoints.append(corners)
                objpoints.append(objp)
        _, self.mtx, self.dist, _, _ = cv2.calibrateCamera(objpoints, imgpoints,
                                                           gray.shape[::-1], None, None)

    def save(self, filename):
        ''' saves the mtx and dist parameters to a binary file '''
        with open(filename, 'wb') as output:
            pickle.dump([self.mtx, self.dist], output)

    def load(self, filename):
        ''' loads the mtx and dist parameters from a binary file '''
        with open(filename, 'rb') as input_file:
            data = pickle.load(input_file)
            self.mtx = data[0]
            self.dist = data[1]

    def undistort(self, image):
        ''' get an image and return undistorted version of it '''
        if self.dist is None or self.mtx is None:
            return None
        return cv2.undistort(image, self.mtx, self.dist, None, self.mtx)

