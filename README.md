# Summary

The goal of this project is to create a self-driving rc car using Raspbery Pi and a camera. The logic of steering the vehicle is done through TensorFlow on a combination of dashcam footage and iterations of the model.

# Objective

To reinforce our knowledge of electronics, machine learning and image processing in a team environment of three

# Libraries
## rcdrive
### drive(usePiCamera=True, resolution=(1648, 1232), fps=30, display=False, detectLanes=False)

# Project Goals
## RC Car
- [X] Purchase cheap RC car
- [X] Mount a Raspberry Pi and Camera
- [X] Implement basic control over RC car motors through Raspberry Pi
- [X] Work around PWM safety considerations for sudden intitial current spike
- [X] Mount batteries for motor and Raspberry Pi (each)
- [X] Tune RC Car to improve ease for training 

## Raspberry Pi
- [X] Install OpenCV and Raspberry Camera
- [X] Stream and save raw camera footage
- [X] Implement image processing to obtain lanes
- [X] Save keyboard Inputs
- [X] Optimise to obtain better FPS through multithreading
- [X] Save image frames and keyboard inputs for neural network
- [ ] Improve code reability and docuimentation

## Neural Network
- [X] Deploy TensorFlow (AlexNet)
- [X] Determine inputs and outputs of AlexNet and the model
- [ ] Obtain training data and validation data
- [ ] Implement model onto Raspberry Pi

# Image Processing
We chose the open source library [OpenCV](https://opencv.org/) because it is easily accessible and there is plenty of documentation on the topic, especially with working with Raspberry Pi.

The resolution of 80x64 is chosen for an image frame processed by the neural network model.

## Lane Detection

There are two approaches to lane detection:
- Detection of colour (Colour Space)
- Detection of shape (Object Detection)

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

To detect the lanes in the image, we greyscale the image and crop the lower half since most of the lanes are in the lower half of a cmaera's POV. Then, we run a Gaussian Blur to smoothen the image and perform Canny edge detection. Further work needs to be done to optimise Canny edge detection since 'autocanny' function from imutils creates unnecessary lines on background objects while an aggressive Gaussian Blur will smoothen the lanes as well.

### Lane Detection

After going through the data, it is determined that detection of shape via canny edge detection offers the best results. Using colour to detect lanes gives more false positives than desired. Code for detecting via colour will be kept for legacy reasons and in hopes that it will find its use when the scope of the self-driving RC car expands.

## HoughLines
Initially, we wanted to draw HoughLines on the lanes from the edges that are detected. This would significally improve the accuracy of the data for the neural network and the model to work on. However, we encoutered many problems from determining the location of lanes without the use of object specification to generation of zero Houghlines due to the discontinuous edges drawn on the image frame. Ater further discussion , we determined that we will use edges to detect the lanes rather than HoughLines to minimize the complexity of the image processing step.

# Neural Network
## Training Data
Currently, we are obtaining more training data by using the keyboard to drive the car. We append the keyboard inputs to the processed image and feed batches of data to the neural network.

## Model

# Problems Encountered
## PWM and Motor
One of the problems 

# Installation
## pip dependencies
- numpy
- scipy
- opencv
- imutils
- wiringpi
- "picamera[array]"
- Pillow
- pololu-drv88350-rpi
- pandas

# References
- [Optimised OpenCV](https://www.pyimagesearch.com/2017/10/09/optimizing-opencv-on-the-raspberry-pi/)
- [VideoStream](https://www.pyimagesearch.com/2016/01/04/unifying-picamera-and-cv2-videocapture-into-a-single-class-with-opencv/)
- [Python library for the Pololu DRV8835 Dual Motor Driver Kit for Raspberry Pi](https://github.com/pololu/drv8835-motor-driver-rpi)
- [Increasing Raspberry Pi Camera FPS](https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/)
- [Faster video file FPS](https://www.pyimagesearch.com/2017/02/06/faster-video-file-fps-with-cv2-videocapture-and-opencv/)

