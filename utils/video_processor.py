import os
import cv2
from moviepy.editor import VideoFileClip
from utils.camera_cal import CameraCalibration
from utils.binary_image import BinaryImage
from utils.perspective_transform import PerspectiveTransform
from utils.lane_finder import LaneFinder


class VideoProcessor:
    ''' Process a video for finding lanes '''
    cam_cal = None

    @staticmethod
    def init(input_video, output_video, camera_cal_directory):
        ''' initialize static class members '''
        VideoProcessor.input_video = input_video
        VideoProcessor.output_video = output_video
        VideoProcessor.cam_cal = VideoProcessor.calibrate_camera(camera_cal_directory)

    @staticmethod
    def process_image(image):
        ''' process each frame image '''
        image_undist = VideoProcessor.cam_cal.undistort(image)
        bin_img = BinaryImage(image_undist, kernel=5, grad_thresh=(20, 100),
                              color_thresh=(120, 255), mag_thresh=(30, 100),
                              dir_thresh=(0.7, 1.3))
        image_binary = bin_img.get()
        pers_img = PerspectiveTransform(image_binary)
        image_perspective = pers_img.get()
        #image_perspective = cv2.cvtColor(image_perspective, cv2.COLOR_BGR2GRAY)
        finder = LaneFinder(image_perspective)
        finder.slide_window()
        image_perspective_overlay = finder.visualize(draw_lane_pixels=False, draw_on_image=False)
        pers_img = PerspectiveTransform(image_perspective_overlay)
        image_overlay = pers_img.get_inverse()
        undist_overlay = cv2.addWeighted(image_undist, 1, image_overlay, 0.3, 0)
        undist_overlay = finder.draw_info(undist_overlay)

        return undist_overlay

    @staticmethod
    def calibrate_camera(camera_cal_directory):
        ''' calibrating camera '''
        filenames = os.listdir(camera_cal_directory)
        images = []
        for filename in filenames:
            if filename.endswith('.jpg') or filename.endswith('.png'):
                img = cv2.imread(os.path.join(camera_cal_directory, filename))
                images.append(img)
        cam_cal = CameraCalibration()
        cam_cal.compute(images)
        return cam_cal

    @staticmethod
    def process():
        ''' process input video '''
        clip = VideoFileClip(VideoProcessor.input_video)
        new_clip = clip.fl_image(VideoProcessor.process_image)
        new_clip.write_videofile(VideoProcessor.output_video, audio=False)


    "frame_num = 0\n",
    "debug = False\n",
    "def process_image(image):\n",
    "    global frame_num\n",
    "    result, lines = detect_lane_lines(image)\n",
    "    if debug:\n",
    "        mpimg.imsave(\"test_videos_output/orig/{}.jpg\".format(str(frame_num).zfill(4)), image, format=\"jpg\")\n",
    "        mpimg.imsave(\"test_videos_output/lanes/{}.jpg\".format(str(frame_num).zfill(4)), result, format=\"jpg\")\n",
    "        mpimg.imsave(\"test_videos_output/lines/{}.jpg\".format(str(frame_num).zfill(4)), lines, format=\"jpg\")\n",
    "    frame_num += 1\n",
    "    return result"

