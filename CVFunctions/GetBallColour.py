import numpy as np
import cv2


def get_ball_colour(frame):
    # --------------------------------------------------------------------------------------------------------------
    # sourced: https://stackoverflow.com/questions/50899692/most-dominant-color-in-rgb-image-opencv-numpy-python
    # @@@There is potential to improve the speed of this if required - check link above@@@
    data = np.reshape(frame, (-1, 3))
    print(data.shape)
    data = np.float32(data)

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    flags = cv2.KMEANS_RANDOM_CENTERS
    compactness, labels, centers = cv2.kmeans(data, 1, None, criteria, 10, flags)

    print('Dominant color is: bgr({})'.format(centers[0].astype(np.int32)))
    # --------------------------------------------------------------------------------------------------------------
    return format(centers[0].astype(np.int32))
