# Summary

The goal of this project is to create a self-driving rc car using Raspbery Pi and a camera. The logic of steering the vehicle is done through TensorFlow on a combination of dashcam footage and iterations of the model.

# Objective

To reinforce our knowledge of electronics, machine learning and image processing in a team environment

# Project Goals
## RC Car
- [X] Purchase cheap RC car
- [X] Mount a Raspberry Pi and Camera
- [ ] Implement basic control over RC car motors through Raspberry Pi

## Raspberry Pi
- [X] Install OpenCV and Raspberry Camera
- [X] Stream and save raw camera footage
- [ ] Implement edge detection

## Neural Network
- [X] Deploy TensorFlow
- [ ] Prepare data for inputs for TensorFlow
- [ ] Implement model onto Raspberry Pi

## Lane Detection

There are two approaches to lane detection:
- Detection of shape (Object Detection)
- Detection of colour (Colour Space)

### Detection of colour

To select the road markings using colour, we convert the original image frame into HSV Colourspace. In OpenCV, the HSV parameters goes as follows:
-	H: 0 - 180
-	S: 0 - 255
-	V: 0 - 255

Since most road markings are white and yellow, the following HSV values are chosen:
- White: (0, 0, 100)
- Yellow: (62, 100, 50)

The only problem is that this is highly dependent on the camera colour calibration.

### Detection of shape

With some margin of tolerance due to colour variations in road marking paint, weather, light conditions and camera colour calliberation, each value is given a tolerance of 10%.

# Installation

## pip dependencies
- numpy
- scipy
- matplotlib
- opencv
- imutils
- wiringpi
- "picamera[array]"
- Pillow
- pololu-drv88350-rpi
- gpiozero

# References
- [Optimised OpenCV](https://www.pyimagesearch.com/2017/10/09/optimizing-opencv-on-the-raspberry-pi/)
- [VideoStream](https://www.pyimagesearch.com/2016/01/04/unifying-picamera-and-cv2-videocapture-into-a-single-class-with-opencv/)
- [Python library for the Pololu DRV8835 Dual Motor Driver Kit for Raspberry Pi](https://github.com/pololu/drv8835-motor-driver-rpi)
- [Increasing Raspberry Pi Camera FPS](https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/)
- [Faster video file FPS](https://www.pyimagesearch.com/2017/02/06/faster-video-file-fps-with-cv2-videocapture-and-opencv/)

