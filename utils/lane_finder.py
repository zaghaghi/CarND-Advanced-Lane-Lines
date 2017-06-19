import numpy as np
import cv2


class Line:
    ''' keep track of detected lines '''
    average_count = 5
    def __init__(self):
        self.poly_fit = []
        self.lane_ind = []
        self.lane_start = []

    def add_poly_fit(self, poly_fit):
        self.poly_fit.append(poly_fit)
        if len(self.poly_fit) > Line.average_count:
            del self.poly_fit[0]

    def get_last_poly_fit(self):
        return self.poly_fit[-1]

    def get_average_poly_fit(self):
        return np.average(self.poly_fit, axis=0)

    def add_lane_ind(self, lane_ind):
        self.lane_ind.append(lane_ind)
        if len(self.lane_ind) > Line.average_count:
            del self.lane_ind[0]

    def get_last_lane_ind(self):
        return self.lane_ind[-1]

    def add_lane_start(self, lane_start):
        self.lane_start.append(lane_start)
        if len(self.lane_start) > Line.average_count:
            del self.lane_start[0]

    def get_last_lane_start(self):
        return self.lane_start[-1]

    def get_average_lane_start(self):
        return np.average(self.lane_start, axis=0)

class LaneFinder:
    ''' Finds lanes from perspective image '''
    right_line = Line()
    left_line = Line()

    def __init__(self, image, cache=False):
        if not cache:
            Line.average_count = 1
            LaneFinder.right_line.average_count = 1
            LaneFinder.left_line.average_count = 1
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
        self.left_curverad = None
        self.right_curverad = None
        self.ym_per_pix = 30/720 # meters per pixel in y dimension
        self.xm_per_pix = 3.7/700 # meters per pixel in x dimension
        self.distance_from_center = self.left_lane_start - \
                                    (self.image.shape[1] - self.right_lane_start)

    def slide_window(self, n_windows=9, window_width=120, min_pixel=50):
        ''' Slides a window on both lanes to find a polynomial fit '''
        window_height = np.int(self.image.shape[0]/n_windows)

        nonzero = self.image.nonzero()
        nonzero_y = np.array(nonzero[0])
        nonzero_x = np.array(nonzero[1])

        left_current = self.left_lane_start
        right_current = self.right_lane_start

        LaneFinder.left_line.add_lane_start(left_current)
        LaneFinder.right_line.add_lane_start(right_current)

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

        LaneFinder.left_line.add_lane_ind(self.left_lane_inds)
        LaneFinder.right_line.add_lane_ind(self.right_lane_inds)

        # Extract left and right line pixel positions
        left_x = nonzero_x[self.left_lane_inds]
        left_y = nonzero_y[self.left_lane_inds]
        right_x = nonzero_x[self.right_lane_inds]
        right_y = nonzero_y[self.right_lane_inds]

        # Fit a second order polynomial to each
        self.left_fit = np.polyfit(left_y, left_x, 2)
        self.right_fit = np.polyfit(right_y, right_x, 2)

        LaneFinder.left_line.add_poly_fit(self.left_fit)
        LaneFinder.right_line.add_poly_fit(self.right_fit)

        y_eval = self.image.shape[0] * self.ym_per_pix
        # Fit new polynomials to x,y in world space
        left_fit_cr = np.polyfit(left_y * self.ym_per_pix, left_x * self.xm_per_pix, 2)
        right_fit_cr = np.polyfit(right_y * self.ym_per_pix, right_x * self.xm_per_pix, 2)
        # Calculate the new radii of curvature
        left_1st_derivative = 2 * left_fit_cr[0] * y_eval + left_fit_cr[1]
        left_2nd_derivative = 2 * left_fit_cr[0]
        right_1st_derivative = 2 * right_fit_cr[0] * y_eval + right_fit_cr[1]
        right_2nd_derivative = 2 * right_fit_cr[0]
        self.left_curverad = (((1 + (left_1st_derivative) ** 2) ** 1.5) /
                              np.absolute(left_2nd_derivative))
        self.right_curverad = (((1 + (right_1st_derivative) ** 2) ** 1.5) /
                               np.absolute(right_2nd_derivative))

    def visualize(self, draw_on_image=True, draw_lane_pixels=True, draw_lane=True):
        ''' visualize founded lanes and windows on image '''
        #if self.left_fit is None or self.right_fit is None:
        #    return None
        vis_img = np.dstack((self.image, self.image, self.image))
        if not draw_on_image:
            vis_img = np.zeros_like(vis_img)
        ploty = np.linspace(0, self.image.shape[0] - 1, self.image.shape[0])

        left_fit = LaneFinder.left_line.get_average_poly_fit()
        right_fit = LaneFinder.right_line.get_average_poly_fit()

        left_fitx = left_fit[0] * ploty ** 2 + left_fit[1] * ploty + left_fit[2]
        right_fitx = right_fit[0] * ploty ** 2 + right_fit[1] * ploty + right_fit[2]

        nonzero = self.image.nonzero()
        nonzero_y = np.array(nonzero[0])
        nonzero_x = np.array(nonzero[1])

        pts_left = np.array([np.transpose(np.vstack([left_fitx, ploty]))])
        pts_right = np.array([np.flipud(np.transpose(np.vstack([right_fitx, ploty])))])
        pts = np.hstack((pts_left, pts_right))

        if draw_lane:
            cv2.fillPoly(vis_img, np.int_([pts]), (0, 255, 0))

        if draw_lane_pixels:
            left_lane_inds = LaneFinder.left_line.get_last_lane_ind()
            right_lane_inds = LaneFinder.right_line.get_last_lane_ind()
            vis_img[nonzero_y[left_lane_inds], nonzero_x[left_lane_inds]] = [255, 0, 0]
            vis_img[nonzero_y[right_lane_inds], nonzero_x[right_lane_inds]] = [0, 0, 255]

        return vis_img

    def draw_info(self, image):
        ''' draw curve information on input image'''
        text = "Left Curve: {:6.2f}m".format(self.left_curverad)
        cv2.putText(image, text, (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        text = "Right Curve: {:6.2f}m".format(self.right_curverad)
        cv2.putText(image, text, (20, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        text = "Distance from center {:4.2f}m to the {}"
        if self.distance_from_center < 0:
            text = text.format(-self.distance_from_center * self.xm_per_pix, 'left')
        elif self.distance_from_center == 0:
            text = "Distance from center 0m"
        else:
            text = text.format(self.distance_from_center * self.xm_per_pix, 'right')
        cv2.putText(image, text, (20, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return image