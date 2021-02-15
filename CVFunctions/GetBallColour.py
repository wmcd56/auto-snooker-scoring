import numpy as np
import cv2


def get_ball_colour(img):

    # --------------------------------------------------------------------------------------------------------------
    # sourced: https://stackoverflow.com/questions/50899692/most-dominant-color-in-rgb-image-opencv-numpy-python
    # @@@There is potential to improve the speed of this if required - check link above@@@
    data = np.reshape(img, (-1, 3))
    # print(data.shape)  # debugging
    data = np.float32(data)
    # print(data.shape)

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    flags = cv2.KMEANS_RANDOM_CENTERS
    if data.shape[0] > 0 and data.shape[1] > 0:
        compactness, labels, centers = cv2.kmeans(data, 1, None, criteria, 10, flags)
        return centers[0]
    # print('Dominant color is: bgr({})'.format(centers[0].astype(np.int32)))
    # --------------------------------------------------------------------------------------------------------------

    else:
        return False
