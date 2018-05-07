import numpy as np;
import copy;
import cv2;
import os;
import imutils;

debug_dir = "debug";

def detectLanesVid(input_filename, output_filename, debug=False):
	# Reading the file
	original = cv2.VideoCapture(input_filename);

	if (original is None):
		print("ERROR! Unable to read file: " + str(input_filename));
		return;
	elif (output_filename is None):
		print("ERROR! No output filename specified");
		return;

	# Getting video properties
	fps = int(original.get(cv2.CAP_PROP_FPS));
	height = int(original.get(cv2.CAP_PROP_FRAME_HEIGHT));
	height = round(height/2);
	width = int(original.get(cv2.CAP_PROP_FRAME_WIDTH));

	print("Resolution of new video: " + str(width) + "x" + str(height));

	# Creating output file if specified
	fourcc = cv2.VideoWriter_fourcc(*'XVID');
	output = cv2.VideoWriter(output_filename, fourcc, fps, (width, height));

	ret = True;
	# Processing
	while(original.isOpened() and ret):
		ret, frame = original.read();

		if (ret == True):
			frame = detectLanesFrame(frame);

			output.write(frame);
			cv2.imshow('frame', frame);

			if cv2.waitKey(1) & 0xFF == ord('q'):
				break;

	original.release();
	output.release();
	cv2.destroyAllWindows();
	print("Finished processing " + str(input_filename));

### detectLanes
# Detects the lanes of an image
def detectLanesImg(input_filename, output_filename="", debug=False):
	# Initialisation of Variables

	# Reading the File and cropping the image
	original = cv2.imread(input_filename);

	if (debug):
		if (not os.path.exists(debug_dir)):
			os.makedirs(debug_dir);
		cv2.imwrite(debug_dir + "/original.png", original);

	if (original is None):
		print("ERROR! Unable to read specified file: " + str(input_filename));
		return;

	output = detectLanesFrame(original, debug);

	# Saving output
	if (output_filename != ""):
		cv2.imwrite(output_filename, output);
 
	print("Finished processing " + str(input_filename));

def detectLanesFrame(original, debug=False):
	if (original is None):
		print("ERROR! Unable to find frame");
		return;

	(height, width, size) = original.shape;
	frame = original[round(height/2):height, 0:width];

	if (debug):
		cv2.imwrite(debug_dir + "/cropped.png", frame);

	colour = detectLanes_frameColour(frame, debug);
	canny = detectLanes_frameCanny(frame, debug);

	edges = colour + canny;
	if (debug):
		cv2.imwrite(debug_dir + "/edges.png", edges);

	contour = detectLanes_contour(frame, edges, debug);
	return contour;

# Detects the lane using colour
# Assumes frame is colour
def detectLanes_frameColour(frame, debug=False):
	if (frame is None):
		print("ERROR! Frame is blank");
		return;

	# Isolating for Yellow and White markings
	rgb_boundaries = [
		# ([25, 146, 190], [62, 174, 250]), # yellow
		# ([103, 86, 65], [145, 133, 128]),	# green
		([187, 187, 218], [255, 255, 255])	# white
	];

	tempFrame = copy.deepcopy(frame);
	counter = 0;

	for (lower, upper) in rgb_boundaries:
		# create NumPy arrays from the boundaries
		lower = np.array(lower, dtype = "uint8");
		upper = np.array(upper, dtype = "uint8");
	 
		# find the colors within the specified boundaries and apply
		# the mask
		mask = cv2.inRange(tempFrame, lower, upper);
		rgb = cv2.bitwise_and(tempFrame, tempFrame, mask = mask);

		if (debug):
			cv2.imwrite(debug_dir + "/rgb_colour" + str(counter) + ".png", rgb);
		counter += 1;
		output = rgb;

	# Ranges:
	# H: 0 - 180
	# S: 0 - 255
	# V: 0 - 255
	hsv_boundaries = [
		# ([round(50/360*180), round(30/100*255), round(50/100*255)], [round(80/360*180), 255, round(85/100*255)]), # yellow
		([0, 0, round(80/100*255)], [180, round(10/100*255), 255])	# white
	];
	
	hsv = cv2.cvtColor(tempFrame, cv2.COLOR_BGR2HSV);
	tempFrame = copy.deepcopy(hsv);
	counter = 0;

	if (debug):
		cv2.imwrite(debug_dir + "/hsv.png", hsv);

	for (lower, upper) in hsv_boundaries:
		# create NumPy arrays from the boundaries
		lower = np.array(lower, dtype = "uint8");
		upper = np.array(upper, dtype = "uint8");
	 
		# find the colors within the specified boundaries and apply
		# the mask
		mask = cv2.inRange(tempFrame, lower, upper);
		hsv = cv2.bitwise_and(tempFrame, tempFrame, mask = mask);

		if (debug):
			cv2.imwrite(debug_dir + "/hsv_colour" + str(counter) + ".png", hsv);
		output += hsv;
		counter += 1;

	output = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY);
	output = cv2.threshold(output, 20, 255, cv2.THRESH_BINARY)[1];

	if (debug):
		cv2.imwrite(debug_dir + "/laneColour.png", output);
	return output;

# Detects the lane using edges
# Assumes frame is colour
def detectLanes_frameCanny(frame, debug=False):
	if (frame is None):
		print("ERROR! Frame is blank");
		return;

	# Converting to different colour space
	grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY);

	if (debug):
		cv2.imwrite(debug_dir + "/grey.png", grey);

	# Smoothing the image
	canny = copy.deepcopy(grey);
	# canny = cv2.medianBlur(canny, 3);
	canny = cv2.GaussianBlur(canny,(7, 7), 0);

	if (debug):
		cv2.imwrite(debug_dir + "/blur.png", canny);	
	
	# Applying canny
	canny = imutils.auto_canny(canny);

	if (debug):
		cv2.imwrite(debug_dir + "/canny.png", canny);
	return canny;

#Draws lines on the lanes
# Assumes frame is coloured and edges is processed
def detectLanes_contour(frame, edges, debug=False):
	if (frame is None):
		print("ERROR! Frame is blank");
		return;
	elif edges is None:
		print("ERROR! Edges is blank");
		return;

	# Contours using edges
	tempFrame = copy.deepcopy(frame);
	im2, contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE);
	cv2.drawContours(tempFrame, contours, -1, (0,255,0), 3); # Draws all the contours

	if (debug):
		cv2.imwrite(debug_dir + "/contour_edges.png", tempFrame);

	# Approximate shape from contours
	tempFrame = copy.deepcopy(frame);

	for cnt in contours:
		approx = cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt,True), True);

		if (len(approx) >= 2 and cv2.arcLength(cnt,True) > 100):
			# cv2.drawContours(tempFrame,[cnt],0,(0,0,255),-1);

			# Bounding boxes
			rect = cv2.minAreaRect(cnt);
			box = cv2.boxPoints(rect);
			box = np.int0(box);
			cv2.drawContours(tempFrame,[box],0,(0,0,255),2);

	if (debug):
		cv2.imwrite(debug_dir + "/contour_edges_boxes.png", tempFrame);

	# # Hough Line Transform Probabilistic
	# tempFrame = copy.deepcopy(frame);
	# lines = cv2.HoughLinesP(edges, 2, np.pi/180, 200, minLineLength=200, maxLineGap=50);
	# for line in lines:
	# 	x1,y1,x2,y2 = line[0];
	# 	cv2.line(tempFrame, (x1,y1), (x2,y2), (0,255,0), 2);

	# if (debug):
	# 	cv2.imwrite(debug_dir + "/houghlinesP.png", tempFrame);
	return tempFrame;
