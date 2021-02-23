import cv2
import numpy as np
import json
import difflib


def classify_hsv(bgr, colours_hsv=None):

    if colours_hsv is None:
        with open('C:/Users/mcdon/Desktop/AutoSnooker/Resources/colours_hsv.txt', 'r') as file:
            colours_bgr = json.load(file)
