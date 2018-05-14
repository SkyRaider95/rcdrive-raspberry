# import the necessary packages
from imutils.video import VideoStream;
from picamera.array import PiRGBArray;
from picamera import PiCamera;
from threading import Thread;
import cv2;
import datetime;
import time;
import sys;

# import the Queue class from Python 3
if sys.version_info >= (3, 0):
	from queue import Queue
 
# otherwise, import the Queue class for Python 2.7
else:
	from Queue import Queue

class piStream:
	def __init__(self, name="", resolution=(320,240), fps=30):
		# Initialise camera properties
		self.name = name;
		self.resolution = resolution;
		self.fps = fps;
		self.isStream = False;
		
		# Initialise time statistics
		self._start = None
		self._end = None

		# Initialise the stream and frame properties
		self.frames_updated = 0;
		self.frames_read = 0;
		self.frame = None;
		self.vs = VideoStream(usePiCamera=True, resolution=resolution, framerate=fps).start();
		print("Initializing PiCamera " + str(name));

		# initialize the queue used to store frames read from
		# the video file
		queueSize = 128; # May need to change in the future
		self.Q = Queue(maxsize=queueSize)

		time.sleep(2.0);

	def start(self):
		print("Begin streaming...");
		self.isStream = True;
		self._start = datetime.datetime.now()
		self._end = None;
		self.counter = 1;

		piStreamThrd = Thread(target=self.update, args=());
		piStreamThrd.daemon = True; # deletes itself when main program ends
		piStreamThrd.start();
		return self;

	def update(self):
		while (self.isStream):
			# Stop Thread
			if (self.isStream == False):
				return;

			# Queue has room for more frames
			if (not self.Q.full()):
				self.frames_updated += 1;
				frame = self.vs.read();
				self.Q.put(frame);
		self.vs.stop();

	def stop(self):
		self.isStream = False;
		self._end = datetime.datetime.now();
		
		print("End streaming");

	def read(self):
		self.frames_read += 1;
		return self.Q.get(), self.frames_read;

	# return True if there are still frames in the queue
	def more(self):
		return self.Q.qsize() > 0

	# Prints all the statistics of a given piStream object
	def stats(self):
		print("Name of camera: " + str(self.name));
		print("Resolution of camera: " + str(self.resolution));
		print("Frames updated: " + str(self.frames_updated));
		print("Frames read: " + str(self.frames_read));
		
		# Gets actual FPS, even if camera is still ongoing
		# Also checks the status of the camera
		if (self._end is None and self.isStream):
			time_diff = (datetime.datetime.now() - self._start).total_seconds();
		else:
			time_diff = (self._end - self._start).total_seconds();

		actual_fps = self.frames_read/time_diff;
		print("Expected fps: " + str(self.fps));
		print("Actual FPS: " + str(actual_fps));
