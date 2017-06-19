import cv2
import numpy as np

class BinaryImage:
    ''' build a binary image from input image which is best for lane detecction'''
    def __init__(self, image, kernel=5, grad_thresh=(0, 255),
                 sat_thresh=(0, 255), light_thresh=(0, 255),
                 mag_thresh=(0, 255), dir_thresh=(0, np.pi/2)):
        image = cv2.bilateralFilter(image, kernel*2, 60, 120)
        self.image = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
        self.s_channel = self.image[:, :, 2]
        self.l_channel = self.image[:, :, 1]
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        self.abs_sobelx = None
        self.abs_sobely = None
        self.scaled_sobelx = None
        self.scaled_sobely = None
        self._compute_sobel(kernel)
        self.grad_binary = self._abs_sobel_thresh(grad_thresh)
        self.color_binary = self._color_thresh(sat_thresh, light_thresh)
        self.mag_binary = self._mag_thresh(mag_thresh)
        self.dir_binary = self._dir_thresh(dir_thresh)

    def _compute_sobel(self, kernel):
        sobelx = cv2.Sobel(self.gray, cv2.CV_64F, 1, 0, ksize=kernel)
        self.abs_sobelx = np.absolute(sobelx)
        self.scaled_sobelx = np.uint8(255*self.abs_sobelx/np.max(self.abs_sobelx))
        sobely = cv2.Sobel(self.gray, cv2.CV_64F, 0, 1, ksize=kernel)
        self.abs_sobely = np.absolute(sobely)
        self.scaled_sobely = np.uint8(255*self.abs_sobely/np.max(self.abs_sobely))

    def _color_thresh(self, sat_thresh, light_thresh):
        color_binary = np.zeros_like(self.s_channel)
        color_binary[(self.s_channel >= sat_thresh[0]) & (self.s_channel <= sat_thresh[1]) &
                     (self.l_channel >= light_thresh[0]) & (self.l_channel <= light_thresh[1])] = 1
        return color_binary

    def _abs_sobel_thresh(self, thresh):
        grad_binary = np.zeros_like(self.scaled_sobelx)
        grad_binary[(self.scaled_sobelx >= thresh[0]) & (self.scaled_sobelx <= thresh[1])] = 1
        return grad_binary

    def _mag_thresh(self, thresh):
        mag = np.sqrt(self.abs_sobelx*self.abs_sobelx + self.abs_sobely*self.abs_sobely)
        scaled_mag = np.int8(255.0*mag/np.max(mag))
        mag_binary = np.zeros_like(scaled_mag)
        mag_binary[(scaled_mag >= thresh[0]) & (scaled_mag <= thresh[1])] = 1
        return mag_binary

    def _dir_thresh(self, thresh):
        direction = np.arctan2(self.abs_sobely, self.abs_sobelx)
        dir_binary = np.zeros_like(direction)
        dir_binary[(direction >= thresh[0]) & (direction <= thresh[1])] = 1
        return dir_binary

    def get(self):
        ''' returns binary representation of an input image '''
        img_binary = np.zeros_like(self.gray)
        cond = (self.color_binary == 1) | \
               ((self.grad_binary == 1) | ((self.dir_binary == 1) & (self.mag_binary == 1)))
        img_binary[cond] = 1
        return img_binary*255
