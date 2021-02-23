import numpy as np
import cv2


def pixels_distance(loc1, loc2):
    x1, y1 = loc1[0], loc1[1]
    x2, y2 = loc2[0], loc2[1]
    distance = np.sqrt((np.abs(x1-x2))**2 + (np.abs(y1-y2))**2)
    return distance
