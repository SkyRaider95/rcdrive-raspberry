# Import packages
from imutils.video import VideoStream;
import frameProcess as fp;
from pololu_drv8835_rpi import motors, MAX_SPEED
import imutils;
import time;
import datetime;
import argparse;
import cv2;

# Main running program for the car
def drive(usePiCamera=True, resolution=(1648, 1232), fps=30, speedLimit=MAX_SPEED):
	# Initialize the video stream and allow the camera sensor to warmup
	isPiCamera=True;
	vs = VideoStream(usePiCamera=usePiCamera, resolution=resolution, framerate=fps).start();
	time.sleep(2.0);

	# Initialise to write to file
	fourcc = cv2.VideoWriter_fourcc(*'XVID');
	out = cv2.VideoWriter('output.avi', fourcc, fps, resolution);

	# Initialise motors
	# Assume motor1 is longitudinal (forwards/backwards)
	# Assume motor2 is lateral (turning or yaw)
	motors.motor1.setSpeed(speedLimit);
	motors.motor2.setSpeed(0);

	# Event loop
	while (True):
		# Grabbing frame from the threaded video and resize it to 400 pixels
		frame = vs.read();

		# Detect lanes
		frame = fp.detectLanesFrame(frame);

		# Do some lane stuff

		# # Draw the timestamp on the frame
		# 	timestamp = datetime.datetime.now();
		# 	ts = timestamp.strftime("%d %B %Y %I:%M:%S%p");
		# 	print(str(ts));
		# 	cv2.putText(frame, ts, (100, 100), cv2.FONT_HERSHEY_SIMPLEX,
		# 1, (0, 0, 255), 1);

		# Displaying frame
		cv2.imshow("Frame", frame);
		key = cv2.waitKey(1) & 0xFF;

		# Saving the frame
		out.write(frame);

		# if the `q` key was pressed, break from the loop
		if key == ord("q"):
			break

	# Closing Program
	cv2.destroyAllWindows();
	out.release();
	vs.stop();
