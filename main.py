from Classes.Player import Player
from Classes.Ball import Ball
from Classes.Frame import Frame
# from CVFunctions.FindBalls import find_balls

import cv2
import numpy as np
from CVFunctions.GetBallColour import get_ball_colour
from CVFunctions.FindBalls import find_balls

# ======================================================================================================================
# access a web cam

# cap = cv2.VideoCapture(0)
# cap.set(3, 640)
# cap.set(4, 480)
# success, img = cap.read()
path = 'Resources/snooker.png'
img = cv2.imread(path)
# roi = cv2.selectROI("ROI selector", img, False, False)  # hit enter after making selection
# cv2.destroyWindow("ROI selector")
# print(roi)
# roi_cropped = img[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]

circles = find_balls(img)
print(circles)
print(circles[0][1])
i = 0
colour_circles = {}
for (x, y, r) in circles:
    print('x: ', x)
    print('y: ', y)
    print('Radius is: ', r)
    half_width = np.floor(np.sqrt((r**2)/2))
    print('half-width: ', half_width)
    roi = img[int(y-half_width):int(y+half_width), int(x-half_width):int(x+half_width)]
    colour_circles[i] = (circles[i][:], get_ball_colour(roi))
    cv2.imshow("ROI", roi)
    cv2.waitKey(1000)
    i += 1

print("GetBallColour:", get_ball_colour(roi))

print(colour_circles)

print(colour_circles[1][0])

# frame = Frame(colour_circles)

# print(frame.player1.cue_colour)




