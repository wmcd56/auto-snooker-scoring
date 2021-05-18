# needs to be changed for optimised return

import cv2
import numpy as np
from Functions.PixelsDistance import pixels_distance


def find_circles(img, show_image=True, hough_param1=4.5, hough_param2=15, pockets=None,
                 hough_min_radius=20, hough_max_radius=30):
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
    # cimg = img.copy()
    # cimg = cv2.medianBlur(img, 6)
    cimg = cv2.GaussianBlur(img, (5, 5), 10)

    cimg = cv2.cvtColor(cimg, cv2.COLOR_BGR2YUV)
    cimg[..., 0] = cimg[..., 0] * 1
    cimg = cv2.cvtColor(cimg, cv2.COLOR_YUV2BGR)
    if show_image is True:
        cv2.imshow("test", cimg)
        # cv2.waitKey(0)
    cimg = cv2.cvtColor(cimg, cv2.COLOR_BGR2GRAY)
    cimg = cv2.adaptiveThreshold(cimg, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
    kernel = np.ones((1, 1), np.uint8)
    cimg = cv2.erode(cimg, kernel, iterations=1)
    kernel = np.ones((3, 3), np.uint8)
    cimg = cv2.dilate(cimg, kernel, iterations=1)
    if show_image is True:
        cv2.imshow("adaptive thresh", cimg)
        # cv2.waitKey(0)

    # ret, cimg = cv2.threshold(cimg, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # kernel = np.ones((5, 5), np.uint8)
    # cimg = cv2.erode(cimg, kernel, iterations=1)
    # kernel = np.ones((5, 5), np.uint8)
    # cimg = cv2.dilate(cimg, kernel, iterations=1)
    # if show_image is True:
    #     cv2.imshow("otsu", cimg)
    #     cv2.waitKey(0)
    # hough_param2,

    circles = cv2.HoughCircles(cimg, cv2.HOUGH_GRADIENT, hough_param1, hough_param2, minRadius=hough_min_radius,
                               maxRadius=hough_max_radius)

    # print(len(circles[0, :]))
    # ensure at least some circles were found
    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        rounded_circles = np.round(circles[0, :]).astype("int")
        rounded_circles = list(rounded_circles)
        # print(rounded_circles)

        # remove pockets from the circles found
        indexes_to_remove = []
        pockets_x = []
        pockets_y = []
        if pockets is not None:
            for pocket in pockets:
                pockets_x.append(pocket[0][0])
                pockets_y.append(pocket[0][1])
            pockets_xmin = min(pockets_x)
            pockets_xmax = max(pockets_x)
            pockets_ymin = min(pockets_y)
            pockets_ymax = max(pockets_y)
            # print(f'xmax: {pockets_xmax}')
            # print(f'xmin: {pockets_xmin}')
            # print(f'ymax: {pockets_ymax}')
            # print(f'ymin: {pockets_ymin}')

            for i in range(len(rounded_circles)):
                circle_xy = (rounded_circles[i][0], rounded_circles[i][1])
                if (circle_xy[0] <= pockets_xmin+10) or (circle_xy[0] >= pockets_xmax-10):
                    indexes_to_remove.append(i)
                elif (circle_xy[1] <= pockets_ymin+10) or (circle_xy[1] >= pockets_ymax-10):
                    indexes_to_remove.append(i)

            indexes_to_remove.reverse()
            # print('indexes to remove: ', indexes_to_remove)
            for index in indexes_to_remove:
                rounded_circles.pop(index)

            indexes_to_remove = []
            for i in range(len(rounded_circles)):
                removed_flag = False
                circle_xy = (rounded_circles[i][0], rounded_circles[i][1])
                for pocket in pockets:
                    if pixels_distance(circle_xy, pocket[0]) <= pocket[1]:
                        indexes_to_remove.append(i)
                        removed_flag = True
                if removed_flag is True:
                    continue

            indexes_to_remove.reverse()
            # print('indexes to remove: ', indexes_to_remove)
            for index in indexes_to_remove:
                rounded_circles.pop(index)

        if show_image is True:
            # loop over the (x, y) coordinates and radius of the circles
            for (x, y, r) in rounded_circles:
                # draw the circle in the output image, then draw a rectangle
                # corresponding to the center of the circle
                # print(f'x: {x}, y: {y}')
                cv2.circle(output, (x, y), r, (0, 255, 0), 4)
                cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
            cv2.imshow("output", output)
            cv2.waitKey(0)

        return rounded_circles
    else:
        print("No circles detected")
        # return circles


