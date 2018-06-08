# Import packages
from __future__ import print_function
from imutils.video import VideoStream;
from frameProcess import frameProcessObj as fp;
from outputProcess import outputFrame
from pololu_drv8835_rpi import motors, MAX_SPEED
from threading import Thread
from piStream import piStream
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
def drive(usePiCamera=True, resolution=(1648, 1232), fps=30, display=False, detectLanes=False, flip=False):
	# Initialise constants
	DRIVE_LEFT = 0;
	DRIVE_STRAIGHT = 1;
	DRIVE_RIGHT = 2;
	DRIVE_STOP = 3;

	# Initalise variables
	counter = 1;
	global eventLoop, forwardSpd, turningSpd, char;
	eventLoop = True;
	char = "";
	output_dir = "output";
	filename_counter = 1;
	inputSteer = [0, 0, 0]; # No stopping input variable

	# Initialise training data
	training_filename = "training_data.npy";
	if os.path.isfile(training_filename):
		print('File exists, loading previous data!');
		training_data = list(np.load(training_filename));
		print("Number of entries on file: " + str(len(training_data)));
	else:
		print('File does not exist, starting fresh!');
		training_data = [];

	# Initialise frameProcessObj
	rccamera = fp("rc-camera", "rc-camera.output", fp.FRAME_PROCESS_STREAM_CAMERA, resolution, max_fps=fps, only_lower=True);

	# Initialise to write to file
	if (not os.path.exists(output_dir)):
		os.makedirs(output_dir);

	# fourcc = cv2.VideoWriter_fourcc(*'XVID');
	# out = cv2.VideoWriter(output_dir + "/" + 'output.avi', fourcc, fps, resolution);

	# Initialise opencv file
	fieldnames = ['frameName', 'frame', 'timestamp', 'kb_input'];
	if os.path.isfile(output_dir + "/" + 'keyboard.csv'):
		csvfile = open(output_dir + "/" + 'keyboard.csv', 'a');
		csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames);
	else:
		csvfile = open(output_dir + "/" + 'keyboard.csv', 'w');
		csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames);
		csvwriter.writeheader();

	# Initialise motors
	# Assume motor1 is lateral (turning or yaw)
	# Assume motor2 is longitudinal (forwards/backwards)
	motors.setSpeeds(0, 0);

	# Initialise keyboard thread
	keyboardThread = Thread(target=keyboardLoop, args = ());

	# Initialize the video stream
	camera = piStream(name="PiCamera", resolution=resolution, fps=fps);

	# Begin driving
	camera.start();
	keyboardThread.start();
	print("Begin drive");
	
	# Writing frames
	while (eventLoop):
		# Grabbing frame from the video and perform processing
		(frame, counter) = camera.read();

		if (frame is None):
			break;

		# Rotate the camera
		if (flip):
			frame = cv2.flip(frame,0);
			frame = cv2.flip(frame,1);

		# Detects the lanes
		if (detectLanes):
			detectedLane = rccamera.detectLanesFrame(frame);

		# Getting the timestamp on the frame
		timestamp = datetime.datetime.now();
		ts = str(timestamp.strftime("%d %B %Y %I:%M:%S %p"));

		frameName = ts + str(" frameNum ") + str(counter);

		if (counter == 1):
			csvwriter.writerow({'frameName': frameName, 'frame': str(counter), 'timestamp': ts, 'kb_input': str(char)});

		inputSteer = [0, 0, 0]; # No stopping input
		# Keyboard Input
		if (char != ""):
			if (char == "w"):
				inputSteer[DRIVE_STRAIGHT] = 1;
			elif (char == "a"):
				inputSteer[DRIVE_LEFT] = 1;
			elif (char == "d"):
				inputSteer[DRIVE_RIGHT] = 1;

			# Exporting training data if there are valid inputs
			if (inputSteer != [0,0,0]):
				if (detectLanes):
					training_data.append([detectedLane, inputSteer]);
				else:
					training_data.append([frame, inputSteer]);

				# Saves after 100 entries
				if (len(training_data) % 100 == 0):
					np.save(training_filename, training_data);

			# Exit the program next loop
			if (char == "x"):
				motors.setSpeeds(0, 0);
				eventLoop = False;
				print("End drive");
				camera.stop();
				char = "";
				np.save(training_filename, training_data);

			# Write to csv file
			csvwriter.writerow({'frameName': frameName, 'frame': str(counter), 'timestamp': ts, 'kb_input': str(char)});

		# Saving the frame
		outputFrame(frameName, frame, str(output_dir + '/frames'));
		# out.write(frame);
		if (detectLanes):
			outputFrame(frameName + 'edge', detectedLane, str(output_dir + '/frames_edges'));

	# Closing Program
	camera.stats();
	cv2.destroyAllWindows();
	# out.release();
	csvfile.close();
	keyboardThread.join();
	motors.setSpeeds(0, 0);
	print("End of drive");

### Function: stop()
# Stops the car entirely (just in case)
def stop():
	global eventLoop, forwardSpd, turningSpd, char;
	char = "x";
	eventLoop = False;
	motors.setSpeeds(0, 0);

### Function: keyboardLoop()
## Get the keyboard input. Sets the motor speed accordingly.
def keyboardLoop():
	# Initialise all variables
	global eventLoop, forwardSpd, turningSpd, char;
	char = "";
	print("Setting speed to :" + str(forwardSpd));
	print("Speeds should be set when the car is still");

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
		elif char == "g":
			motors.motor2.setSpeed(forwardSpd);
			motors.motor1.setSpeed(0);

		# Exit
		if char == "x":
			eventLoop = False;
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
