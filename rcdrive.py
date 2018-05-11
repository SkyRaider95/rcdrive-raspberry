# Import packages
from __future__ import print_function
from imutils.video import VideoStream;
from frameProcess import frameProcessObj as fp;
from pololu_drv8835_rpi import motors, MAX_SPEED
from threading import Thread
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
forwardSpd = 200;
turningSpd = MAX_SPEED;
char = "";

# Main running program for the car
def drive(usePiCamera=True, resolution=(1648, 1232), fps=30, display=False, alwaysForward = True):
	# Initalise variables
	counter = 1;
	global eventLoop, forwardSpd, turningSpd, char;
	eventLoop = True;
	char = "";

	# Initialize the video stream and allow the camera sensor to warmup
	isPiCamera=True;
	vs = VideoStream(usePiCamera=usePiCamera, resolution=resolution, framerate=fps).start();
	time.sleep(2.0);

	# Initialise frameProcessObj
	rccamera = fp("rc-camera", "rc-camera.output", fp.FRAME_PROCESS_STREAM_CAMERA, resolution, max_fps=fps);

	# Initialise to write to file
	fourcc = cv2.VideoWriter_fourcc(*'XVID');
	out = cv2.VideoWriter('output.avi', fourcc, fps, resolution);

	# Initialise opencv file
	csvfile = open('keyboard.csv', 'w');
	fieldnames = ['frame', 'timestamp', 'kb_input'];
	csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames);
	csvwriter.writeheader();

	# Initialise motors
	# Assume motor1 is lateral (turning or yaw)
	# Assume motor2 is longitudinal (forwards/backwards)
	motors.setSpeeds(0, 0);

	# Constant longitudinal speed
	if (alwaysForward):
		motors.motor2.setSpeed(forwardSpd);

	# Begin thread for keyboard control
	try:
		keyboardThread = Thread(target=keyboardLoop, args = ());
		keyboardThread.start();
	except:
		print("Error: unable to start thread");
		eventLoop = False;

	if (eventLoop):
		print("Beginning stream");
	
	# Event loop
	while (eventLoop):
		# Grabbing frame from tjhe video and perform processing
		frame = vs.read();
		frame = rccamera.detectLanesFrame(frame);

		# Getting the timestamp on the frame
		timestamp = datetime.datetime.now();
		ts = timestamp.strftime("%d %B %Y %I:%M:%S%p");

		# Keyboard Input
		if (char != ""):
			# Exit the program next loop
			if (char == "x"):
				motors.setSpeeds(0, 0);
				eventLoop = False;

			# Write to csv file
			print("Writing to file: " + str(char));
			csvwriter.writerow({'frame': str(counter), 'timestamp': ts, 'kb_input': str(char)});

		else:
			# motors.setSpeeds(0, 0);
			motors.motor1.setSpeed(0);

		# Saving the frame
		out.write(frame);
		counter += 1;

	# Closing Program
	motors.setSpeeds(0, 0);
	cv2.destroyAllWindows();
	out.release();
	vs.stop();
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

	print("Beginning keyboard loop");
	while (eventLoop and char != "q"):
		# Getting Keyboard
		char = getch();

		# # Accelerate
		# if (char == "w"):
		# 	motors.motor2.setSpeed(forwardSpd);

		# Turning Left
		if char == "a":
			motors.motor1.setSpeed(turningSpd);
		# Turning Right
		elif char == "d":
			motors.motor1.setSpeed(-turningSpd);  		

		time.sleep(0.0001);
		char = "";
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
