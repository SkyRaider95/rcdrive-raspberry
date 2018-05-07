# Import packages
from imutils.video import VideoStream;
import imutils;
import time;
import datetime;
import argparse;
import cv2;

# Running program for the rc car
def drive(usePiCamera=True, resolution=(1648, 1232), fps=30):
	# Initialize the video stream and allow the camera sensor to warmup
	isPiCamera=True;
	vs = VideoStream(usePiCamera=usePiCamera, resolution=resolution, framerate=fps).start();
	time.sleep(2.0);

	# Initialise to write to file
	fourcc = cv2.VideoWriter_fourcc(*'XVID');
	out = cv2.VideoWriter('output.avi', fourcc, fps, resolution);

	# Streaming the video
	while (True):
		# Grabbing frame from the threaded video and resize it to 400 pixels
		frame = vs.read();

		# Doing image processing operations
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY);
		frame = imutils.auto_canny(frame);

		# Draw the timestamp on the frame
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
