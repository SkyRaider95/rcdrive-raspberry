# import the necessary packages
from threading import Thread
import sys
import cv2
import os;
 
# import the Queue class from Python 3
if sys.version_info >= (3, 0):
	from queue import Queue
 
# otherwise, import the Queue class for Python 2.7
else:
	from Queue import Queue

class outputFrame:
	def __init__(self, filename, frame, output_dir=""):
		self.filename = str(filename);
		self.frame = frame;
		self.output_dir = str(output_dir);

		outputStreamThrd = Thread(target=self.save, args=());
		outputStreamThrd.daemon = True;
		outputStreamThrd.start();
		return;

	def save(self):
		if (not os.path.exists(self.output_dir)):
			os.makedirs(output_dir);
		if (self.output_dir != ""):
			frameName = self.output_dir + "/" + self.filename + '.png';
		else:
			frameName = self.filename + '.png';

		# print(frameName);
		cv2.imwrite(frameName, self.frame);
		return;
