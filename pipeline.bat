python adv_lane_detection.py calibrate --input-dir camera_cal --output camera.p
python adv_lane_detection.py test-calibrate --camera-input camera.p --input-dir test_images --output-dir output_images\undist
python adv_lane_detection.py binary-image --input-dir output_images\undist --output-dir output_images\binary
python adv_lane_detection.py perspective-transform --input-dir output_images\binary --output-dir output_images\perspective
python adv_lane_detection.py lane-finder --input-dir output_images\perspective --output-dir output_images\lanes
python adv_lane_detection.py lane-visualizer --input-dir output_images\perspective --original-dir output_images\undist --output-dir output_images\final