import cv2
import numpy as np


def bgr_to_hsv(bgr):
    b = bgr[0]
    g = bgr[1]
    r = bgr[2]

    b_dash = b/255
    g_dash = g/255
    r_dash = r/255

    c_max = max(b_dash, g_dash, r_dash)
    c_min = min(b_dash, g_dash, r_dash)
    delta = c_max - c_min

    if delta == 0:
        h = 0
    elif c_max == b_dash:
        h = 60*(((r_dash-g_dash)/delta)+4)
    elif c_max == g_dash:
        h = 60*(((b_dash-r_dash)/delta)+2)
    else:  # c_max == r_dash:
        h = 60*(((g_dash-b_dash)/delta) % 6)

    if c_max == 0:
        s = 0
    else:
        s = delta/c_max

    v = c_max

    print("BGR: ", b, g, r, "HSV: ", h, s, v)
    return [h, s, v]


# out = bgr_to_hsv(255, 0, 0)
