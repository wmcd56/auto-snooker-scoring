import cv2
from . import Ball
from . import Player

class Frame:

    def __init__(self, circles):
        # for practice purposes
        p1_colour = 'purple'
        p2_colour = 'orange'

        self.player1 = Player(p1_colour)
        self.player2 = Player(p2_colour)

        if circles is not None:
            i = 0
            for (x, y, r, colour, ball_id) in circles:
                loc = (x, y)
                self.balls[i] = Ball(circles.colour, loc, ball_id)


    # def obtain_scores(self):
        # add code to track ball

