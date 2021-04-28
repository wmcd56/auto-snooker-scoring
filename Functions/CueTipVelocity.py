import cv2
import numpy as np

from Functions.PixelsDistance import pixels_distance


# ======================================================================================================================
# cue_tip_velocity
# Inputs:
#        - cue_tips_list: a list of boxes outlining the cue tips position in the last x number of frames
# Outputs:
#        - cue_tip_speed: number of pixels moving per frame
#        - direction: the approximate direction that the cue tip is travelling
# ======================================================================================================================
def cue_tip_velocity(cue_tips_list, frames=None):
    distance = 0
    last_loc = None
    first_loc = None
    if frames is None:
        frames = 10
    for i in range(1, frames+1):
        # x1 = 0
        # y1 = 0
        # x2 = 0
        # y2 = 0
        # for j in range(len(cue_tips_list[-i])):
        #     x1 = x1 + cue_tips_list[-i][j][0]
        #     y1 = y1 + cue_tips_list[-i][j][1]
        #
        # for j in range(len(cue_tips_list[-1*(i+1)])):
        #     x2 = x2 + cue_tips_list[-1*(i+1)][j][0]
        #     y2 = y2 + cue_tips_list[-1*(i+1)][j][1]
        #
        # # print(f'x1: {x1}, y1: {y1}')
        # # print(f'x2: {x2}, y2: {y2}')
        # # print('list: ', cue_tips_list[-i], ' length: ', len(cue_tips_list[-i]))
        # loc1 = (x1/len(cue_tips_list[-i]), y1/len(cue_tips_list[-i]))
        # loc2 = (x2/len(cue_tips_list[-1*(i+1)]), y2/len(cue_tips_list[-1*(i+1)]))
        # print(f'loc1: {loc1}, loc2: {loc2}')

        loc1 = cue_tips_list[-i][1]
        loc2 = cue_tips_list[-1*(i+1)][1]
        distance += pixels_distance(loc1, loc2)
        if i == 1:
            last_loc = loc1
        if i == frames:
            first_loc = loc2
        # print('d: ', distance)
    cue_tip_speed = distance/frames
    if last_loc[1] != first_loc[1]:
        direction = (last_loc[0]-first_loc[0]) / (last_loc[1] - first_loc[1])
    else:
        direction = 0.0
    return [cue_tip_speed, direction]
