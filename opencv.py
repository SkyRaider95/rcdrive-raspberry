# Import packages
from picamera.array import PiRGBArray;
from picamera import PiCamera;
import time;
import numpy as np;
import cv2;

# Initialisation
mode = 4; # Sensor mode
size = (1648,1232); # Resolution. For mode 4, use 1640x1232
fps = 30;
max_length = 1; # Maximum length of video in seconds
frame_counter = 0;

camera = PiCamera();
camera.sensor_mode = mode;
camera.resolution = size;
camera.framerate = fps;
rawCapture = PiRGBArray(camera);

fourcc = cv2.VideoWriter_fourcc(*'XVID');
out = cv2.VideoWriter('output.avi', fourcc, fps, size);

# Camera Warmup
time.sleep(0.2);

# Grab an image from the camera
# camera.capture("test_image" + '.jpeg', format="jpeg");
# camera.capture(rawCapture, format="bgr");
# image = rawCapture.array;
# cv2.imshow("Image", image);
# cv2.imwrite("test_image2.jpg", image);

# Capture frames from camera for frame in 
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
  # Grab the raw NumPy array representing the image, then initialise
  # the timestamp and occupied/unoccupied text
  image = frame.array;
  
  # Doing operations on frame
  # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY); # Grey-scaling
  # image = cv2.Canny(image, 50/255, 150/255); # Edge detection

  # Displaying frame the frame
  # Uncomment for debugging camera
  # cv2.imshow("Frame", image);
  # key = cv2.waitKey(1) & 0xFF;

  # Saving frame
  out.write(image);
  frame_counter += 1;

  # Clear the stream in preparation for next frame
  rawCapture.truncate(0);

  # If the 'q' key was pressed, break the loop
  # Uncomment for debugging camera
  # if (key == ord("q")):
  #    break;

  # Finish recording video?
  if (frame_counter > max_length*fps):
    print("Finished recording");
    break;

print("Done");
camera.close();
out.release();
cv2.destroyAllWindows();
