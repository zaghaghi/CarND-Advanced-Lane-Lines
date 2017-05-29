import os
import cv2
import numpy as np
import click

class CameraCalibration:
    ''' This class computes camera calibration parameters '''
    def __init__(self, img_list):
        self.img_list = img_list
        self.mtx = None
        self.dist = None

    def _compute(self, force=False):
        if not force and self.mtx is not None and self.dist is not None:
            return
        imgpoints = []
        objpoints = []

        objp = np.zeros((9*6, 3), np.float32)
        objp[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)
        for img in self.img_list:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, (9, 6), None)

            if ret:
                imgpoints.append(corners)
                objpoints.append(objp)
        _, self.mtx, self.dist, _, _ = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

@click.command()
@click.option('--input-dir', default='data', help='Input directory of camera calibration images.',
              prompt='Input directory')
def main(input_directory):
    pass

if __name__ == '__main__':
    main()
