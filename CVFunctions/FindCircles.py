# needs to be changed for optimised return

import cv2
import numpy as np


def find_circles(img, show_image=True):
    # ==============================================================================================================
    # Function find_circles
    # -recognises the number of circles and returns their locations and radii in a mask
    #
    # INPUT - cv2.imread(pathToImage), or, video frame
    #
    # OUTPUT - circles
    #        - cv2.mask of x, y locations and radii
    #
    # OUTPUT USED - as input to get_ball_colour
    #
    # ==============================================================================================================

    output = img.copy()
    img = cv2.medianBlur(img, 5)
    cimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    circles = cv2.HoughCircles(cimg, cv2.HOUGH_GRADIENT, 3, 80, minRadius=45, maxRadius=60)

    # ensure at least some circles were found
    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        rounded_circles = np.round(circles[0, :]).astype("int")
        # loop over the (x, y) coordinates and radius of the circles
        for (x, y, r) in rounded_circles:
            # draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
            cv2.circle(output, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
        if show_image is True:
            cv2.imshow("output", output)
            cv2.waitKey(0)
        return rounded_circles
    else:
        print("No circles detected")
        # return circles


