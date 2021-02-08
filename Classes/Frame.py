import cv2
from . import Ball
from . import Player


class Frame:

    # ==================================================================================================================
    # Frame class
    # -Initialised with an input of an array of *structs, circles, should contain: x, y, r, colour, ball_id
    # -
    # ==================================================================================================================
    def __init__(self, circles):
        # for practice purposes
        p1_colour = 'purple'
        p2_colour = 'orange'

        self.player1 = Player.Player(p1_colour)
        self.player2 = Player.Player(p2_colour)
        self.balls = {}
        for i in circles:
            self.balls[i] = Ball.Ball(circles[i][0], circles[i][1])

        if circles is not None:
            i = 0
            for (x, y, r, colour, ball_id) in circles:
                loc = (x, y)
                self.balls[i] = Ball.Ball(circles.colour, loc, ball_id)

        print("The players playing include: \nPlayer 1: ", self.player1.cue_colour, "\nPlayer 2: ",
              self.player2.cue_colour, "\nThe balls on the table are: ", self.balls)  # update for clearer ball count

    # def obtain_scores(self):
        # add code to track ball

