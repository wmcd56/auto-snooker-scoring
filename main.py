from Classes.Player import Player
from Classes.Ball import Ball
from Classes.Frame import Frame
# from CVFunctions.FindBalls import find_balls

import cv2
import numpy as np

# ======================================================================================================================
# access a web cam

# cap = cv2.VideoCapture(0)
# cap.set(3, 640)
# cap.set(4, 480)
# success, img = cap.read()
path = 'Resources/blue_example.png'
img = cv2.imread(path)
roi = cv2.selectROI("ROI selector", img, False, False)  # hit enter after making selection
cv2.destroyWindow("ROI selector")
print(roi)
roi_cropped = img[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]
cv2.imshow("ROI", roi_cropped)
cv2.rectangle(img, (60, 60), (75, 95), (0, 128, 255), -1)
cv2.imshow("Pic", img)
cv2.waitKey(0)

# frame = Frame(find_balls(img))

# print(frame.player1.cue_colour)




