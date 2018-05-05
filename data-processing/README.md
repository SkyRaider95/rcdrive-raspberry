# Summary

To process dashcam footage into useful data for neural networks

# Decisions


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

## Choices

- Hough Line Transform
- Contour
- Edges
- Threshold
- Approximation

# Syntax

dc_FEATURE