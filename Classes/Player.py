import numpy as np
import cv2


class Player:

    def __init__(self, cue_colour):
        self.cue_colour = cue_colour
        self.current_points = 0

        print(self.cue_colour)

    def update_score(self, points):
        # add code to track ball
        self.current_points += points
