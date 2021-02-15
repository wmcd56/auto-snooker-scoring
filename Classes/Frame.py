import cv2
from .Ball import Ball
from .Player import Player


class Frame:

    # ==================================================================================================================
    # Frame class
    # -Initialised with an input of an array of *structs, circles, should contain: x, y, r, colour, ball_id
    # -
    # ==================================================================================================================
    def __init__(self, balls, mode='practice'):
        # for practice purposes
        p1_colour = 'purple'
        p2_colour = 'orange'

        self.player1 = Player(p1_colour)
        self.player2 = Player(p2_colour)
        self.balls = balls

        if mode == 'practice':
            print("Mode: Practice Break")
        else:
            print("The players playing include: \nPlayer 1: ", self.player1.cue_colour, "\nPlayer 2: ",
                  self.player2.cue_colour, "\nThe balls on the table are: ")  # update for clearer ball count
        for ball in self.balls:
            print(ball.colour)

    def get_current_player(self):
        # add code to track ball
        current_player = self.player1
        return current_player

    def obtain_scores(self):
        # add code to track ball
        return self.player1.current_points  # , self.player2.current_points

    def update_score(self, additional_points):
        current_player = self.player1
        current_player.current_points += additional_points
