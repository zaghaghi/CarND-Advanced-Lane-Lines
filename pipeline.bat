python adv_lane_detection.py calibrate --input-dir camera_cal --output camera.p
python adv_lane_detection.py test_calibrate --camera-input camera.p --input-dir test_images --output-dir output_images\undist
python adv_lane_detection.py binary_image --input-dir output_images\undist --output-dir output_images\binary
python adv_lane_detection.py perspective_transform --input-dir output_images\binary --output-dir output_images\perspective
python adv_lane_detection.py lane_finder --input-dir output_images\perspective --output-dir output_images\lanes
