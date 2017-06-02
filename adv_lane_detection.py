import os
import click
import cv2
from utils import *

general_cli = click.Group()

@general_cli.command()
@click.option('--input-dir', default='data', help='Input directory of camera calibration images.',
              prompt='Input directory')
@click.option('--output', default='camera.p', help='Camera parameters output filename.')
def calibrate(input_dir, output):
    filenames = os.listdir(input_dir)
    images = []
    for filename in filenames:
        if filename.endswith('.jpg') or filename.endswith('.png'):
            img = cv2.imread(os.path.join(input_dir, filename))
            images.append(img)
    cam_cal = CameraCalibration()
    cam_cal.compute(images)
    cam_cal.save(output)


@general_cli.command('test-calibrate')
@click.option('--camera-input', default='camera.p', help='Input camera parameters filename.',
              prompt='Input camera filename')
@click.option('--input-dir', help='Input directory contains images to apply undistort operation.',
              prompt='Input directory')
@click.option('--output-dir', help='Output directory of undistorted images.',
              prompt='Output directory')
def test_calibrate(camera_input, input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    cam_cal = CameraCalibration()
    cam_cal.load(camera_input)
    filenames = os.listdir(input_dir)
    for filename in filenames:
        if filename.endswith('.jpg') or filename.endswith('.png'):
            image = cv2.imread(os.path.join(input_dir, filename))
            cv2.imwrite(os.path.join(output_dir, os.path.splitext(filename)[0] + '.png'),
                        cam_cal.undistort(image))

@general_cli.command('binary-image')
@click.option('--input-dir', help='Input directory contains images to apply binary operation.',
              prompt='Input directory')
@click.option('--output-dir', help='Output directory of binary images.',
              prompt='Output directory')
def binary_image(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    filenames = os.listdir(input_dir)
    for filename in filenames:
        if filename.endswith('.jpg') or filename.endswith('.png'):
            image = cv2.imread(os.path.join(input_dir, filename))
            bin_img = BinaryImage(image, kernel=5, grad_thresh=(20, 100),
                                  color_thresh=(120, 255), mag_thresh=(30, 100),
                                  dir_thresh=(0.7, 1.3))
            cv2.imwrite(os.path.join(output_dir, filename), bin_img.get())

@general_cli.command('perspective-transform')
@click.option('--input-dir', help='Input directory contains images to apply binary operation.',
              prompt='Input directory')
@click.option('--output-dir', help='Output directory of binary images.',
              prompt='Output directory')
def perspective_transform(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    filenames = os.listdir(input_dir)
    for filename in filenames:
        if filename.endswith('.jpg') or filename.endswith('.png'):
            image = cv2.imread(os.path.join(input_dir, filename))
            pers_img = PerspectiveTransform(image)
            cv2.imwrite(os.path.join(output_dir, filename), pers_img.get())

@general_cli.command('lane-finder')
@click.option('--input-dir', help='Input directory contains perspective gray images for finding lanes.',
              prompt='Input directory')
@click.option('--output-dir', help='Output directory for images.',
              prompt='Output directory')
def lane_finder(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    filenames = os.listdir(input_dir)
    for filename in filenames:
        if filename.endswith('.jpg') or filename.endswith('.png'):
            image = cv2.imread(os.path.join(input_dir, filename))
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            finder = LaneFinder(image)
            finder.slide_window()
            cv2.imwrite(os.path.join(output_dir, filename), finder.visualize())


@general_cli.command('lane-visualizer')
@click.option('--input-dir', help='Input directory contains perspective gray images for finding lanes.',
              prompt='Input directory')
@click.option('--original-dir', help='Input directory contains undistorted images for finding lanes.',
              prompt='Original directory')
@click.option('--output-dir', help='Output directory for images.',
              prompt='Output directory')
def lane_visualizer(input_dir, original_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    filenames = os.listdir(input_dir)
    for filename in filenames:
        if filename.endswith('.jpg') or filename.endswith('.png'):
            image = cv2.imread(os.path.join(input_dir, filename))
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            finder = LaneFinder(image)
            finder.slide_window()
            overlay = finder.visualize(draw_lane_pixels=False, draw_on_image=False)
            undist = cv2.imread(os.path.join(original_dir, filename))
            pers_img = PerspectiveTransform(overlay)
            inverse_pers_img = pers_img.get_inverse()
            undist_overlay = cv2.addWeighted(undist, 1, inverse_pers_img, 0.3, 0)
            undist_overlay = finder.draw_info(undist_overlay)
            cv2.imwrite(os.path.join(output_dir, filename), undist_overlay)

@general_cli.command('process-video')
@click.option('--input-file', help='Input video file.',
              prompt='Input video')
@click.option('--output-file', help='Output video file.',
              prompt='Output video')
def process_video(input_file, output_file):
    VideoProcessor.init(input_file, output_file, 'camera_cal')
    VideoProcessor.process()

if __name__ == '__main__':
    general_cli()

