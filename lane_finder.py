import numpy as np
import cv2

class LaneFinder:
    ''' Finds lanes from perspective image '''
    def __init__(self, image):
        self.image = image
        if len(self.image.shape) != 2:
            raise Exception("Invalid image channels, expected 1 but {} provided.".\
                            format(len(self.image.shape)))
        self.histogram = np.sum(image[image.shape[0]//2:, :], axis=0)
        image_midpoint = self.histogram.shape[0]//2
        self.left_lane_start = np.argmax(self.histogram[:image_midpoint])
        self.right_lane_start = np.argmax(self.histogram[image_midpoint:]) + image_midpoint
        self.left_windows = []
        self.right_windows = []
        self.left_fit = None
        self.right_fit = None
        self.left_lane_inds = None
        self.right_lane_inds = None

    def slide_window(self, n_windows=9, window_width=100, min_pixel=50):
        ''' Slides a window on both lanes to find a polynomial fit '''
        window_height = np.int(self.image.shape[0]/n_windows)

        nonzero = self.image.nonzero()
        nonzero_y = np.array(nonzero[0])
        nonzero_x = np.array(nonzero[1])

        left_current = self.left_lane_start
        right_current = self.right_lane_start

        left_lane_inds = []
        right_lane_inds = []
        self.left_windows = []
        self.right_windows = []
        for window in range(n_windows):
            # Identify window boundaries in x and y (and right and left)
            win_y_low = self.image.shape[0] - (window + 1) * window_height
            win_y_high = self.image.shape[0] - window * window_height
            win_xleft_low = left_current - window_width
            win_xleft_high = left_current + window_width
            win_xright_low = right_current - window_width
            win_xright_high = right_current + window_width
            # Append windows to list for further visualization
            self.left_windows.append([win_xleft_low, win_y_low, win_xleft_high, win_y_high])
            self.right_windows.append([win_xright_low, win_y_low, win_xright_high, win_y_high])
            # Identify the nonzero pixels in x and y within the window
            good_left_inds = ((nonzero_y >= win_y_low) & (nonzero_y < win_y_high) &
                              (nonzero_x >= win_xleft_low) & (nonzero_x < win_xleft_high)
                             ).nonzero()[0]
            good_right_inds = ((nonzero_y >= win_y_low) & (nonzero_y < win_y_high) &
                               (nonzero_x >= win_xright_low) & (nonzero_x < win_xright_high)
                              ).nonzero()[0]
            # Append these indices to the lists
            left_lane_inds.append(good_left_inds)
            right_lane_inds.append(good_right_inds)
            # If you found > minpix pixels, recenter next window on their mean position
            if len(good_left_inds) > min_pixel:
                left_current = np.int(np.mean(nonzero_x[good_left_inds]))
            if len(good_right_inds) > min_pixel:
                right_current = np.int(np.mean(nonzero_x[good_right_inds]))

        # Concatenate the arrays of indices
        self.left_lane_inds = np.concatenate(left_lane_inds)
        self.right_lane_inds = np.concatenate(right_lane_inds)

        # Extract left and right line pixel positions
        left_x = nonzero_x[self.left_lane_inds]
        left_y = nonzero_y[self.left_lane_inds]
        right_x = nonzero_x[self.right_lane_inds]
        right_y = nonzero_y[self.right_lane_inds]

        # Fit a second order polynomial to each
        self.left_fit = np.polyfit(left_y, left_x, 2)
        self.right_fit = np.polyfit(right_y, right_x, 2)

    def visualize(self, draw_on_image=True, draw_lane_pixels=True, draw_lane=True):
        ''' visualize founded lanes and windows on image '''
        if self.left_fit is None or self.right_fit is None:
            return None
        vis_img = np.dstack((self.image, self.image, self.image))
        if not draw_on_image:
            vis_img = np.zeros_like(vis_img)
        ploty = np.linspace(0, self.image.shape[0] - 1, self.image.shape[0])
        left_fitx = self.left_fit[0] * ploty ** 2 + self.left_fit[1] * ploty + self.left_fit[2]
        right_fitx = self.right_fit[0] * ploty ** 2 + self.right_fit[1] * ploty + self.right_fit[2]
        nonzero = self.image.nonzero()
        nonzero_y = np.array(nonzero[0])
        nonzero_x = np.array(nonzero[1])

        pts_left = np.array([np.transpose(np.vstack([left_fitx, ploty]))])
        pts_right = np.array([np.flipud(np.transpose(np.vstack([right_fitx, ploty])))])
        pts = np.hstack((pts_left, pts_right))

        if draw_lane:
            cv2.fillPoly(vis_img, np.int_([pts]), (0, 255, 0))

        if draw_lane_pixels:
            vis_img[nonzero_y[self.left_lane_inds], nonzero_x[self.left_lane_inds]] = [255, 0, 0]
            vis_img[nonzero_y[self.right_lane_inds], nonzero_x[self.right_lane_inds]] = [0, 0, 255]

        return vis_img

