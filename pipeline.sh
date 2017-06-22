#!/bin/sh
python adv_lane_detection.py calibrate --input-dir camera_cal --output camera.p
python adv_lane_detection.py undistort --camera-input camera.p --input-dir test_images --output-dir output_images/undist
python adv_lane_detection.py binary-image --input-dir output_images/undist --output-dir output_images/binary
python adv_lane_detection.py perspective-transform --input-dir output_images/binary --output-dir output_images/perspective
python adv_lane_detection.py lane-finder --input-dir output_images/perspective --output-dir output_images/lanes
python adv_lane_detection.py lane-visualizer --input-dir output_images/perspective --original-dir output_images/undist --output-dir output_images/final

python adv_lane_detection.py test-undistort --input-file test_images/straight_lines1.jpg --output-file examples/test-undistort1.png --camera-input camera.p
python adv_lane_detection.py test-undistort --input-file camera_cal/calibration1.jpg --output-file examples/test-undistort.png --camera-input camera.p
python adv_lane_detection.py test-perspective-transform --input-file output_images/undist/straight_lines1.png --output-file examples/test-perspective1.png
python adv_lane_detection.py test-perspective-transform --input-file output_images/undist/straight_lines2.png --output-file examples/test-perspective2.png