## Advanced Lane Finding
[![Udacity - Self-Driving Car NanoDegree](https://s3.amazonaws.com/udacity-sdc/github/shield-carnd.svg)](http://www.udacity.com/drive)


In this project, your goal is to write a software pipeline to identify the lane boundaries in a video, but the main output or product we want you to create is a detailed writeup of the project.  Check out the [writeup template](https://github.com/udacity/CarND-Advanced-Lane-Lines/blob/master/writeup_template.md) for this project and use it as a starting point for creating your own writeup.  

Creating a great writeup:
---
A great writeup should include the rubric points as well as your description of how you addressed each point.  You should include a detailed description of the code used in each step (with line-number references and code snippets where necessary), and links to other supporting documents or external references.  You should include images in your writeup to demonstrate how your code works with examples.  

All that said, please be concise!  We're not looking for you to write a book here, just a brief description of how you passed each rubric point, and references to the relevant code :). 

You're not required to use markdown for your writeup.  If you use another method please just submit a pdf of your writeup.

The Project
---

The goals / steps of this project are the following:

* Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
```bash
# Bash
python adv_lane_detection.py calibrate --input-dir camera_cal --output camera.p
```
```python
# Python
from camera_cal import CameraCalibration
cam_cal = CameraCalibration()
cam_cal.compute(image_list)
cam_cal.save(camera_file)
```
* Apply a distortion correction to raw images.
```bash
# Bash
python adv_lane_detection.py undistort --camera-input camera.p --input-dir test_images --output-dir output_images/undist
```
```python
# Python
from camera_cal import CameraCalibration
cam_cal = CameraCalibration()
cam_cal.load(camera_file)
output_image = cam_cal.undistort(input_image)
```
* Use color transforms, gradients, etc., to create a thresholded binary image.
```bash
# Bash
python adv_lane_detection.py binary-image --input-dir output_images/undist --output-dir output_images/binary
```
```python
# Python
from binary_image import BinaryImage
bin_img = BinaryImage(input_image, kernel=5, grad_thresh=(20, 100),
                      sat_thresh=(120, 255), light_thresh=(45, 225),
                      mag_thresh=(30, 100), dir_thresh=(0.7, 1.3))
output_image = bin_img.get()
```
* Apply a perspective transform to rectify binary image ("birds-eye view").
```bash
# Bash
python adv_lane_detection.py perspective-transform --input-dir output_images\binary --output-dir output_images\perspective
```
```python
# Python
pers_img = PerspectiveTransform(input_image)
output_image = pers_img.get()
```
* Detect lane pixels and fit to find the lane boundary.
```bash
# Bash
python adv_lane_detection.py lane-finder --input-dir output_images\perspective --output-dir output_images\lanes
```
```python
# Python
gray_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
finder = LaneFinder(gray_image)
finder.slide_window()
output_image = finder.visualize()
```
* Determine the curvature of the lane and vehicle position with respect to center.
* Warp the detected lane boundaries back onto the original image.
* Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position.
```bash
# Bash
python adv_lane_detection.py lane-visualizer --input-dir output_images\perspective --original-dir output_images\undist --output-dir output_images\final
```
```python
# Python
gray_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
finder = LaneFinder(gray_image)
finder.slide_window()
overlay = finder.visualize(draw_lane_pixels=False, draw_on_image=False)
pers_img = PerspectiveTransform(overlay)
inverse_pers_img = pers_img.get_inverse()
undist_overlay = cv2.addWeighted(undist_image, 1, inverse_pers_img, 0.3, 0)
output_image = finder.draw_info(undist_overlay)
```

The images for camera calibration are stored in the folder called `camera_cal`.  The images in `test_images` are for testing your pipeline on single frames.  If you want to extract more test images from the videos, you can simply use an image writing method like `cv2.imwrite()`, i.e., you can read the video in frame by frame as usual, and for frames you want to save for later you can write to an image file.  

To help the reviewer examine your work, please save examples of the output from each stage of your pipeline in the folder called `ouput_images`, and include a description in your writeup for the project of what each image shows.    The video called `project_video.mp4` is the video your pipeline should work well on.  

The `challenge_video.mp4` video is an extra (and optional) challenge for you if you want to test your pipeline under somewhat trickier conditions.  The `harder_challenge.mp4` video is another optional challenge and is brutal!

If you're feeling ambitious (again, totally optional though), don't stop there!  We encourage you to go out and take video of your own, calibrate your camera and show us how you would implement this project from scratch!

Files Structure
---
The files that I added to complete the project have this structure
```
.
│   adv_lane_detection.py
│   pipeline.bat
│   pipeline.sh
└── utils
     │   camera_cal.py
     │   binary_image.py
     │   perspective_transform.py
     │   lane_finder.py
     │   video_processor.py
```

* **adv_lane_detection.py**: this python script handles input parameteres and call appropriate methods to achieve the result.
* **pipeline.bat**: this windows batch file run pipeline for images.
* **pipeline.sh**: this linux shell file run pipeline for images.
* **camera_cal.py**: this script contains CameraCalibration class which provides methods for finding camera calibration matrix and applying undistortion on images
* **binary_image.py**: this script contains BinaryImage class which provides a method for converting road color image into binary image.
* **perspective_transform.py**: this script contains PerspectiveTransform class which provides two methods for perspective transformation.
* **lane_finder.py**: this script contains LaneFinder and Lane classes which provides methods for finding and visualizing lane and curvature information of lanes.
* **video_processor.py**: this script contains VideoProcessor class which uses other utils classes to apply lane detection on videos instead of images.