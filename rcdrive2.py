# Import packages
from __future__ import print_function
from imutils.video import VideoStream;
from frameProcess import frameProcessObj as fp;
from outputProcess import outputFrame
from pololu_drv8835_rpi import motors, MAX_SPEED
from threading import Thread, Lock
from piStream import piStream
from collections import Counter
import pandas as pd
import copy;
import os;
import numpy as np
import sys;
import tty;
import termios;
import imutils;
import time;
import datetime;
import argparse;
import cv2;
import csv;

eventLoop = True;
motorSpd = [MAX_SPEED, 100, 140, 160, 180, 200, 240, 280, 320, 380]; # Ranges of speed. Arranged according to keyboard layout
forwardSpd = 240; # Default speed
turningSpd = MAX_SPEED;
char = "";

### Function: drive
## Main running program for the car
#
## INPUT
# usePiCamera: True when using the Raspberry Pi camera. False if otherwise. Defaults to True
# resolution: Resolution of the image frame. Defaults to 1648x1232.
# fps: Specifies fps for saving to the video output and expected from the camera. Defaults to 30
# display: Displays to screen if True. Defaults to False
# detectLanes: Attempts to detect lanes from the camera if True. Defaults to False.
def drive(resolution=(1648, 1232), fps=30, display=False, detectLanes=False, flip=False):
	# Initialise constants
	DRIVE_LEFT = 0;
	DRIVE_STRAIGHT = 1;
	DRIVE_RIGHT = 2;
	DRIVE_STOP = 3;
	fieldnames = ['frameName', 'frame', 'timestamp', 'kb_input'];

	# Initialise global variables
	counter = 1;
	global eventLoop, forwardSpd, turningSpd, char, selfDrive, output_dir
	eventLoop = True;
	char = "";
	output_dir = "output";
	selfDrive = False;

	# Initialise to write to file
	if (not os.path.exists(output_dir)):
		os.makedirs(output_dir);
		os.makedirs(output_dir + "/frames");

	# Initialising csv file
	# if os.path.isfile(output_dir + "/" + 'keyboard.csv'):
	# 	csvfile = open(output_dir + "/" + 'keyboard.csv', 'a');
	# 	csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames);
	# else:
	# 	csvfile = open(output_dir + "/" + 'keyboard.csv', 'w');
	# 	csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames);
	# 	csvwriter.writeheader();

	# Initialize the video stream
	camera = piStream(name="PiCamera", resolution=resolution, fps=fps);
	camera.start();

	# Initialise keyboard thread
	keyboardThread = Thread(target=keyboardLoop, args = ());
	keyboardThread.start();

	# Initialise frameProcessObj
	rccamera = fp("rc-camera", "rc-camera.output", fp.FRAME_PROCESS_STREAM_CAMERA, resolution, max_fps=fps, only_lower=True);

	# Initialise training data
	training_filename = "training_data.npy";
	if os.path.isfile(training_filename):
		training_data = list(np.load(training_filename));
		print("Training file exists! Number of entries on file: " + str(len(training_data)));
		df = pd.DataFrame(np.load(training_filename));
		print(df.head());
		print(Counter(df[0].apply(str)));
		print(Counter(df[1].apply(str)));
		print(Counter(df[2].apply(str)));

	# Initialise motors
	# Assume motor1 is lateral (turning or yaw)
	# Assume motor2 is longitudinal (forwards/backwards)
	motors.setSpeeds(0, 0);

	# Begin driving
	print("Begin drive");
	
	# Writing frames
	while (eventLoop):
		# Grabbing frame from the video and perform processing
		(frame, counter) = camera.read();
		current_char = copy.deepcopy(char);

		if (frame is None):
			print("ERROR! Unable to find frame");
			break;

		# Rotate the camera
		if (flip):
			frame = cv2.flip(frame,0);
			frame = cv2.flip(frame,1);

		frameName = "original_frame_frameNum_" + str(counter) + "_char_" + str(current_char);
		outputFrame(frameName, frame, str(output_dir + '/frames'));
		# Processing the frame in a separate thread

		args = [frame, current_char, training_filename, counter, True];
		processFrameThread = Thread(target=processFrame, args=args);
		# processFrameThread.daemon = True;
		processFrameThread.start();
		# processFrame(frame, current_char, training_filename, counter, True);

		# Keyboard Input
		if (current_char != ""):
			# Exit the program next loop
			if (current_char == "x"):
				motors.setSpeeds(0, 0);
				eventLoop = False;
				print("End drive");
				camera.stop();
				current_charr = "";

	# Closing Program
	camera.stats();
	cv2.destroyAllWindows();
	keyboardThread.join();
	motors.setSpeeds(0, 0);
	if os.path.isfile(training_filename):
		training_data = list(np.load(training_filename));
		print("Number of entries on file: " + str(len(training_data)));
		df = pd.DataFrame(np.load(training_filename));
		print(df.head());
		print(Counter(df[1].apply(str)));
	print("End of drive");

### Function: stop()
# Stops the car entirely (just in case)
def stop():
	global eventLoop, forwardSpd, turningSpd, char, selfDrive;
	char = "x";
	eventLoop = False;
	motors.setSpeeds(0, 0);
	selfDrive = False;

### Function: keyboardLoop()
## Get the keyboard input. Sets the motor speed accordingly.
def keyboardLoop():
	# Initialise all variables
	global eventLoop, forwardSpd, turningSpd, char, selfDrive;
	char = "";
	selfDrive = False;
	print("Setting speed to :" + str(forwardSpd));
	print("Speeds should be set when the car is still");
	print("SelfDrive mode: " + str(selfDrive));

	print("Beginning keyboard loop");
	while (eventLoop and char != "x"):
		# Getting Keyboard
		char = getch();
		# print(str(char));

		# Adjust speed
		if (str.isnumeric(char)):
			forwardSpd = motorSpd[int((char))];
			char = "";
			print("Setting speed to :" + str(forwardSpd));

		# Straight
		if (char == "w"):
			motors.motor2.setSpeed(forwardSpd);
			motors.motor1.setSpeed(0);

		# Turning Left
		if char == "a":
			motors.motor1.setSpeed(turningSpd);
		# Turning Right
		elif char == "d":
			motors.motor1.setSpeed(-turningSpd);
		# Stop
		elif char == "s":
			motors.motor2.setSpeed(0);
			char = "";
			print("Car is idling");
		# Self-Driving Mode. Initially starts from a straight
		elif (char == "g"):
			print("SelfDrive mode: " + str(selfDrive));
			char = "";

		# Exit
		if char == "x":
			eventLoop = False;
			selfDrive = False;
			break;
		
	print("Ending keyboardLoop");

### Function: getch()
## Gets the cahr from the keyboard
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# Process the frame.
# Outputs training data if specified
def processFrame(original, char="", training_filename="", counter = "", debug=False):
	lock = Lock;

	# Saving a copy of the varialbes
	lock.acquire();
	current_char = copy.deepcopy(char);
	frame = copy.deepcopy(original);
	lock.release();
	
	# Initialisation of constants
	global selfDrive, output_dir;
	selfDrive = False;
	DRIVE_LEFT = 0;
	DRIVE_STRAIGHT = 1;
	DRIVE_RIGHT = 2;
	DRIVE_STOP = 3;

	# Initialisation for steering
	inputSteer = [0, 0, 0]; # No stopping input
	if (current_char == "w"):
		inputSteer[DRIVE_STRAIGHT] = 1;
	elif (current_char == "a"):
		inputSteer[DRIVE_LEFT] = 1;
	elif (current_char == "d"):
		inputSteer[DRIVE_RIGHT] = 1;

	# Exiting out if there is no valid inputs
	if (frame is None):
		print("ERROR! Unable to find frame");
		return;
	elif (inputSteer == [0,0,0]):
		return;

	# Getting the ROI	of the frame
	(height, width, size) = frame.shape;
	frame = frame[round(height/2):height, 0:width];

	# Apply Canny Edge Detection
	grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY);
	canny = cv2.medianBlur(grey, 3);
	canny = cv2.GaussianBlur(canny,(7, 7), 0);
	canny = imutils.auto_canny(canny);

	# Checking if canny image still exists
	(height, width) = canny.shape;
	if (height <=0 or width <= 0):
		print("ERROR! Height or width is zero or less inside processFrame!");

	# Fixing the frame name
	frameName = "frame_lane_detection_img";
	if (counter != ""):
		frameName = frameName + "_frameNum_" + str(counter);
	frameName = frameName + "_char_" + str(char);

	# Export Processed Image
	if (not os.path.exists(output_dir)):
		os.makedirs(output_dir)
	outputFrame(frameName, canny, str(output_dir + '/processed'));

	# Creating the list
	if (training_filename != ""):
		if os.path.isfile(training_filename):
			training_data = list(np.load(training_filename));
			training_data.append([canny, inputSteer]);
		else:
			print('Training data file does not exist; starting fresh!');
			training_data = [];

		# Saving the training data
		training_data.append([canny, inputSteer]);
		np.save(training_filename, training_data);

	return canny;
