import cv2
import numpy as np

class PerspectiveTransform:
    ''' transforms the image to a bird-eyes view '''
    def __init__(self, image):
        self.image = image
        self.img_size = (image.shape[1], image.shape[0])
        self.src = np.float32(
            [[(self.img_size[0] / 2) - 55, self.img_size[1] / 2 + 100],
             [((self.img_size[0] / 6) - 10), self.img_size[1]],
             [(self.img_size[0] * 5 / 6) + 60, self.img_size[1]],
             [(self.img_size[0] / 2 + 55), self.img_size[1] / 2 + 100]])
        self.dst = np.float32(
            [[(self.img_size[0] / 5), 0],
             [(self.img_size[0] / 5), self.img_size[1]],
             [(self.img_size[0] * 4 / 5), self.img_size[1]],
             [(self.img_size[0] * 4 / 5), 0]])
        self.M = cv2.getPerspectiveTransform(self.src, self.dst)
        self.Minv = cv2.getPerspectiveTransform(self.dst, self.src)

    def get(self):
        return cv2.warpPerspective(self.image, self.M, self.img_size, flags=cv2.INTER_LINEAR)

    def get_inverse(self):
        return cv2.warpPerspective(self.image, self.Minv, self.img_size, flags=cv2.INTER_LINEAR)
