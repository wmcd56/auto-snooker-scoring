from Classes.Player import Player
from Classes.Ball import Ball
from Classes.Frame import Frame
from CVFunctions.FindBalls import find_balls

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

frame = Frame(find_balls(img))

print(frame.player1.cue_colour)




