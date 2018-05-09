import numpy as np;
from PIL import Image
import copy;
import cv2;
import os;
import imutils;

debug_dir = "debug";

### Class: frameProcessObj
#
## Variables
# NAME: Name of stream. If a file, must be filename
# TYPE: Indicates object type
# RESOLUTION: Resolution (width, height)
# RESCALE: When frame processing, is it okay to scale to region of interest as best as possible?
# CROP: When frame processing, is it okay to crop out non-region of interest?
class frameProcessObj:
	# Default Attributes
	FRAME_PROCESS_STREAM_CAMERA = "Camera";
	FRAME_PROCESS_FILE_IMAGE = "Image";
	FRAME_PROCESS_FILE_VIDEO = "Video";
	FRAME_PROCESS_IMAGE_FRAME = "FRAME";

	roi_resolution = (128, 128);

	def __init__(self, name, objType, output="", resolution=(1648, 1232), rescale=True, crop=False, max_fps=-1, only_lower=False):
		self.NAME = name;
		self.OUTPUT = output;
		self.TYPE = objType;
		self.RESOLUTION = resolution;
		self.RESCALE = rescale;
		self.CROP = crop;
		self.USE_ROI_VERTICES = False;
		self.ROI_VERTICES = ((0,0), (resolution[0], 0), (resolution[0], resolution[1]), (0, resolution[1]));
		self.MAX_FPS = max_fps;
		self.ONLY_LOWER = only_lower;

	# User manually sets desired ROI
	def ROI_crop(self, frame):
		s = cv2.selectROI(frame);
		r = [0, 0, 0, 0];
		cv2.destroyAllWindows();

		# Must be even numbers
		for x in range(0,3):
			print(str(x));
			r[x] = s[x] + s[x] % 2;

		top_left = (int(r[0]), int(r[1]));
		bottom_left =  (int(r[0]), int(r[3]));
		bottom_right = (int(r[2]), int(r[3]));
		top_right = (int(r[2]), int(r[1]));
		self.setROI_vertices(top_left, bottom_left, bottom_right, top_right);

	# Sets the Region of Interest vertices
	# It will isolate your region of interest in a trapezoid shape (possible to be a rectangle/square)
	# Assumes all values are correct
	def setROI_vertices(self, top_left, bottom_left, bottom_right, top_right):
		self.ROI_VERTICES = (top_left, bottom_left, bottom_right, top_right);
		self.USE_ROI_VERTICES = True;

	# Sets the max fps for the output video
	def setMaxFPS(self, max_fps):
		self.MAX_FPS = max_fps;

	# Displays all the variables
	def properties(self):
		print("Camera name: " + self.NAME);
		if (self.OUTPUT != ""):
			print("Output: " + str(self.OUTPUT));
		print("Type: " + self.TYPE);
		print("Resolution: " + str(self.RESOLUTION[0]) + ' x ' + str(self.RESOLUTION[1]));
		print("Rescale: " + str(self.RESCALE));
		print("Crop: " + str(self.CROP));
		if (self.USE_ROI_VERTICES):
			print("ROI Vertices: " + str(self.ROI_VERTICES));
		if (self.MAX_FPS > 0):
			print("FPS: " + str(self.MAX_FPS));
		print("Lower half only when processing frame: " + str(self.ONLY_LOWER));

	## Function: detectLanes
	# Detect lanes based on object's properties
	# Will display output if specified
	def detectLanes(self, frame=None, debug=False, display=False):
		if (self.TYPE == self.FRAME_PROCESS_FILE_IMAGE):
			self.detectLanesImg(debug, display);
		elif (self.TYPE == self.FRAME_PROCESS_FILE_VIDEO):
			self.detectLanesVid(debug, display);
		elif (frame.any() != None and self.TYPE == self.FRAME_PROCESS_IMAGE_FRAME):
			print("Entering frame");
			output = self.detectLanesFrame(frame, debug);
			if (self.OUTPUT != ""):
				cv2.imwrite(self.OUTPUT, output);
			return output;
		else:
			print("ERROR! Wrong type!");

	def detectLanesVid(self, debug=False, display=True):
		# Reading the file
		original = cv2.VideoCapture(self.NAME);

		if (original is None):
			print("ERROR! Unable to read video file: " + str(self.NAME));
			return;
		elif (self.OUTPUT is None):
			print("ERROR! No output video file specified");
			return;

		# Getting video properties from first frame and video
		fps = int(original.get(cv2.CAP_PROP_FPS));
		ret, frame = original.read();
		frame = self.detectLanesFrame(frame);
		height, width, channels = frame.shape;

		# Setting output values if not specified
		if (self.RESOLUTION != (width, height)):
			self.RESOLUTION = (width, height);
			print("Setting output resolution to " + str(self.RESOLUTION));

		if (self.MAX_FPS > 0):
			fps = self.MAX_FPS;
		else:
			self.MAX_FPS = fps;
			print("Setting output fps to " + str(self.MAX_FPS));

		# Creating output file if specified
		fourcc = cv2.VideoWriter_fourcc(*'XVID');
		output = cv2.VideoWriter(self.OUTPUT, fourcc, fps, (width, height));

		# Processing
		while(original.isOpened() and ret):
			frame = self.detectLanesFrame(frame);
			output.write(frame);

			# Display frames if specified
			if (display):
				cv2.imshow('frame', frame);
				if cv2.waitKey(1) & 0xFF == ord('q'):
					break;

			ret, frame = original.read(); # Getting next frame

		original.release();
		output.release();
		cv2.destroyAllWindows();
		print("Finished processing video " + str(self.NAME));

	### detectLanes
	# Detects the lanes of an image
	def detectLanesImg(self, debug=False, display=False):
		# Reading the File and cropping the image
		original = cv2.imread(self.NAME);

		if (debug):
			if (not os.path.exists(debug_dir)):
				os.makedirs(debug_dir);
			cv2.imwrite(debug_dir + "/original.png", original);

		if (original is None):
			print("ERROR! Unable to read specified file: " + str(self.NAME));
			return;

		output = self.detectLanesFrame(original, debug);

		# Saving output
		if (self.OUTPUT != ""):
			cv2.imwrite(self.OUTPUT, output);

		# Display frame if specified
		if (display):
			cv2.imshow('Image', output);
			cv2.waitKey(0);
		print("Finished processing image " + str(self.NAME));

	### Function: detectLanesFrame
	# Detects the lane from a frame
	# Outputs the processed frame
	def detectLanesFrame(self, original, debug=False):
		if (original is None):
			print("ERROR! Unable to find frame");
			return;

		(height, width, size) = original.shape;
		frame = copy.deepcopy(original);

		# Getting ROI
		if (self.ONLY_LOWER):
			frame = original[round(height/2):height, 0:width];

		if (self.CROP):
			self.ROI_crop(frame);
			self.CROP = False;
			height, width, channels = frame.shape;
			self.RESOLUTION = (width, height);

		if (self.USE_ROI_VERTICES):
			top_left, bottom_left, bottom_right, top_right = self.ROI_VERTICES;
			frame = frame[top_left[1]:top_left[1] + bottom_right[1], top_left[0]:top_left[0] + bottom_right[0]];

		if (debug):
			if (not os.path.exists(debug_dir)):
				os.makedirs(debug_dir);
			cv2.imwrite(debug_dir + "/cropped.png", frame);

			# frameCropped = frame[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])];

		# colour = self.detectLanes_frameColour(frame, debug);
		canny = self.detectLanes_frameCanny(frame, debug);

		# edges = colour + canny;
		edges = canny;
		if (debug):
			cv2.imwrite(debug_dir + "/edges.png", edges);

		contour = self.detectLanes_contour(frame, edges, debug);
		return contour;

	# Detects the lane using colour
	# Assumes frame is colour
	def detectLanes_frameColour(self, frame, debug=False):
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

			if (len(lower) == len(upper)):
				mask = cv2.inRange(tempFrame, lower, upper);
				hsv = cv2.bitwise_and(tempFrame, tempFrame, mask = mask);
				output += hsv;
				if (debug):
					cv2.imwrite(debug_dir + "/hsv_colour" + str(counter) + ".png", hsv);
			counter += 1;

		output = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY);
		output = cv2.threshold(output, 20, 255, cv2.THRESH_BINARY)[1];

		if (debug):
			cv2.imwrite(debug_dir + "/laneColour.png", output);
		return output;

	# Detects the lane using edges
	# Assumes frame is colour
	def detectLanes_frameCanny(self, frame, debug=False):
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
	def detectLanes_contour(self, frame, edges, debug=False):
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
