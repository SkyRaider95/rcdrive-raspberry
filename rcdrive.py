# Import packages
from __future__ import print_function
from imutils.video import VideoStream;
from frameProcess import frameProcessObj as fp;
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
forwardSpd = 180;
turningSpd = MAX_SPEED;
char = "";

# Main running program for the car
def drive(usePiCamera=True, resolution=(1648, 1232), fps=30, display=False, detectLanes=False):
	# Initalise variables
	counter = 1;
	global eventLoop, forwardSpd, turningSpd, char;
	eventLoop = True;
	char = "";
	output_dir = "output"

	# Initialize the video stream and allow the camera sensor to warmup
	camera = piStream(name="PiCamera", resolution=resolution, fps=fps);
	camera.start();

	# Initialise frameProcessObj
	rccamera = fp("rc-camera", "rc-camera.output", fp.FRAME_PROCESS_STREAM_CAMERA, resolution, max_fps=fps);

	# Initialise to write to file
	if (not os.path.exists(output_dir)):
		os.makedirs(output_dir);

	fourcc = cv2.VideoWriter_fourcc(*'XVID');
	out = cv2.VideoWriter(output_dir + "/" + 'output.avi', fourcc, fps, resolution);

	# Initialise opencv file
	csvfile = open(output_dir + "/" + 'keyboard.csv', 'w');
	fieldnames = ['frameName', 'frame', 'timestamp', 'kb_input'];
	csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames);
	csvwriter.writeheader();

	# Initialise motors
	# Assume motor1 is lateral (turning or yaw)
	# Assume motor2 is longitudinal (forwards/backwards)
	motors.setSpeeds(0, 0);

	# Begin thread for keyboard control
	try:
		keyboardThread = Thread(target=keyboardLoop, args = ());
		keyboardThread.daemon = True;
		keyboardThread.start();
	except:
		print("Error: unable to start thread");
		eventLoop = False;

	if (eventLoop):
		print("Beginning stream");
	
	# Event loop
	while (eventLoop):
		# Grabbing frame from the video and perform processing
		(frame, counter) = camera.read();

		if (detectLanes):
			frame = rccamera.detectLanesFrame(frame);

		# if (display):
		# 	displayThread = Thread(target=showFrame, args = ());
		# 	displayThread.start();

		# Getting the timestamp on the frame
		timestamp = datetime.datetime.now();
		ts = str(timestamp.strftime("%d %B %Y %I:%M:%S %p"));

		frameName = ts + str(" frameNum ") + str(counter);

		if (counter == 1):
			csvwriter.writerow({'frameName': frameName, 'frame': str(counter), 'timestamp': ts, 'kb_input': str(char)});

		# Keyboard Input
		if (char != ""):
			# Exit the program next loop
			if (char == "x"):
				motors.setSpeeds(0, 0);
				eventLoop = False;
				camera.stop();

			# Write to csv file
			# print('At frame ' + str(counter) + ', writing to file: ' + str(char) + '\n');
			csvwriter.writerow({'frameName': frameName, 'frame': str(counter), 'timestamp': ts, 'kb_input': str(char)});

		# else:
		# 	# motors.setSpeeds(0, 0);
		# 	motors.motor1.setSpeed(0);

		# Saving the frame
		cv2.imwrite(output_dir + "/" + frameName +'.png', frame);
		# out.write(frame);

	# Closing Program
	camera.stats();
	motors.setSpeeds(0, 0);
	cv2.destroyAllWindows();
	out.release();
	csvfile.close();
	keyboardThread.join();

	print("End of drive");

def stop():
	global eventLoop, forwardSpd, turningSpd, char;
	char = "x";
	eventLoop = False;
	motors.setSpeeds(0, 0);

# Get the keyboard input
def keyboardLoop():
	# Initialise all variables
	global eventLoop, forwardSpd, turningSpd, char;

	char = "";

	print("Beginning keyboard loop");
	while (eventLoop and char != "x"):
		# Getting Keyboard
		char = getch();

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

		# Exit
		if char == "x":
			eventLoop = False;
			break;
		
	print("Ending keyboardLoop");
	return;

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# def showFrame():
# 	global eventLoop, forwardSpd, turningSpd, char, frame;

# 	cv2.imshow(frame);
# 	cv2.waitKey(1);
