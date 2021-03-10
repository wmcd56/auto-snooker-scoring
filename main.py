"""
Automatic Snooker Scoring System
Undertaken as part of the Masters of Engineering at Maynooth University
Started    - September 2020
Completed  -


Author: William McDonnell
Specific code segments sourced from others are cited with the url from where they were obtained
Further information on the operation  of this system can be found in the accompanying class and sequence diagrams
"""
# ======================================================================================================================
# This file runs the main program for the system and utilises all classes and functions included in this directory
# ======================================================================================================================

from Classes.Player import Player
from Classes.Ball import Ball
from Classes.WhiteBall import WhiteBall
from Classes.Frame import Frame

import cv2
import numpy as np
import time
import json
import multiprocessing
import concurrent.futures
import PySimpleGUI as sg

from CVFunctions.GetBallColour import get_ball_colour
from CVFunctions.FindCircles import find_circles
from CVFunctions.FindBalls import find_balls
from CVFunctions.BGRtoHSV import bgr_to_hsv
# from CVFunctions.ClassifyHSV import classify_hsv
from CVFunctions.ClassifyBGR import classify_bgr
from Functions.CalibrateColours import calibrate_colours
from Functions.PixelsDistance import pixels_distance


# def get_colour_circles(img, circles, xyr, i):
#     half_width = np.floor(np.sqrt((r ** 2) / 2))
#     # print('half-width: ', half_width)  # debugging
#     roi = img[int(y - half_width):int(y + half_width), int(x - half_width):int(x + half_width)]
#     bgr_colour = get_ball_colour(roi)
#     if bgr_colour is False:
#         continue
#     # hsv_colour = bgr_to_hsv(bgr_colour)
#     temp_colour_circles = (circles[i][:], bgr_colour)
#     # print("Temp colour: ", temp_colour_circles)  # debugging
#     colour_circles.append(temp_colour_circles)
#     cv2.circle(img, (x, y), r, (0, 255, 0), 4)
#     cv2.rectangle(img, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
#     return colour_circles

def main():
    # ==================================================================================================================
    # FRAME SET-UP

    # For different lighting conditions the colours should be calibrated first
    # This function requests the user to place balls of a certain colour within view of the camera
    # Can be run separately from the main file if calibrating once before multiple games

    # colours = calibrate_colours()

    print("starting...")
    print("place all balls in position")
    # time.sleep(10)
    # ------------------------------------------------------------------------------------------------------------------
    # access a web cam

    # cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # comment out for big set up
    cap = cv2.VideoCapture(0)  # comment out for small set up
    cap.set(3, 1024)  # comment out for big set up
    cap.set(4, 768)  # comment out for big set up
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # comment out for small set up
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)  # comment out for small set up
    success, img = cap.read()
    if success is False:
        print('Failed to connect to camera')
    # cv2.imshow('test', img)
    # cv2.waitKey(0)
    # ------------------------------------------------------------------------------------------------------------------
    # load a picture from 'Resources'

    # path = 'Resources/snooker.png'
    # img = cv2.imread(path)

    # setup complete
    # ==================================================================================================================
    # Variable initialisation and locating balls
    # ------------------------------------------------------------------------------------------------------------------
    # start gui
    score = 0
    layout = [[sg.Text(f"Player's current score: {score}")], [sg.Button("OK")]]
    window = sg.Window("AutoSnooker", layout)

    # ------------------------------------------------------------------------------------------------------------------
    # Find the balls that have been laid on the table
    white_ball, balls = find_balls(img)
    frame = Frame(white_ball, balls)  # frame is now set up
    # cv2.imshow("window", img)  # show the balls that have been on the table
    # cv2.waitKey(0)

    # ------------------------------------------------------------------------------------------------------------------
    # variable initialisation

    # for colour lines tracking
    # TODO: Replace this file directory with something more robust
    with open('C:/Users/mcdon/Desktop/AutoSnooker/Resources/colours_bgr.txt', 'r') as file:
        colours_bgr = json.load(file)

    ball_to_hit = ['red']  # first ball to hit must be red, this is updated once a red is hit
    ball_pocketed = ['']  # this list holds the balls which were pocketed in the last shot
    ball_index = -1  # used in the second stage, to get what ball should be pocketed next, starts at -1 as +1 is added
    foul_flag = False
    foul_type = ''

    balls_gone = []
    white_gone = []
    frame_count = 0  # used to ensure certain situations occur in subsequent frames
    max_frame_count = 300
    consecutive_frames = 5  # used for the number of consecutive frames needed to register a ball as having been potted
    while True:
        # ==============================================================================================================
        time.sleep(1)  # debugging
        print('Ball to hit: ', ball_to_hit)
        # --------------------------------------------------------------------------------------------------------------
        # initialise variables
        if frame_count == max_frame_count:  # arbitrarily chosen frame cap
            frame_count = 0

        reds_on_table = []  # list to hold the red balls detected to be on the table in this turn
        frame_reds = []  # list of red balls registered to be in the game
        updated_balls = []  # list of balls which have been successfully updated within this loop
        indexes = []  # index of red balls in frame_reds

        additional_points = 0
        # --------------------------------------------------------------------------------------------------------------
        # capture new frame
        success, img = cap.read()
        if not success:
            print('Failed to access camera')
            exit()
        # --------------------------------------------------------------------------------------------------------------
        # find the balls in the new image & update locations (track)
        white_ball_on_table, balls_on_table = find_balls(img, show_image=False)

        # debugging
        # out = ''
        # for b in balls_on_table:
        #     out += f'{b.colour}, '
        # print(f'The balls on table: {out}')

        # if the white ball is still on the table update it's location
        if white_ball_on_table:
            frame.white_ball.ball.track_ball(white_ball_on_table.ball.loc[0])
        # otherwise add the frame number to the list white_gone
        else:
            white_gone.append(frame_count)

        # find all of the red balls on the table and in the frame.balls list
        for b in balls_on_table:
            if b.colour == 'red':
                reds_on_table.append(b)  # make a list of reds from the balls currently on the table
                continue
            for ball in frame.balls:
                if ball.colour == 'red':
                    frame_reds.append(ball)  # make a list of reds from frame.balls
                    continue
                if b.colour == ball.colour:
                    ball.track_ball(b.loc[0])  # update the location of the coloured ball
                    updated_balls.append(ball)  # add the coloured ball to the list of coloured balls still on table

        # if len(reds_on_table) < len(frame_reds):

        # TODO: a more efficient algorithm could be used here
        for r in reds_on_table:
            differences = []
            for red in frame_reds:  # create a list of differences for the location of reds on table and previous frame
                differences.append(pixels_distance(r.loc[0], red.loc[0]))
            if differences:
                min_diff = min(differences)  # find the minimum difference
                index = differences.index(min_diff)  # find index of minimum difference
                if min_diff <= r.radius:  # only update the ball if the minimum distance is less than the radius width
                    frame_reds[index].track_ball(r.loc[0])  # update the correct red ball with the new location
                    updated_balls.append(frame_reds[index])
                    indexes.append(index)
        # print('indexes: ', indexes)  # prints the indexes or identities of the red balls

        # debugging
        # out = ''
        # for b in updated_balls:
        #     out += f'{b.colour} '
        # print('Updated balls: ', out)

        # tracking is complete
        # --------------------------------------------------------------------------------------------------------------
        # Find the balls in frame.balls that were not found in the new image, remove them and update score accordingly

        # TODO: review this, currently player will still be awarded a point if the red ball is pocketed with the white
        # first ensure that the white ball has not been pocketed
        # remove old elements of white_gone
        for elem in white_gone:
            if frame_count >= consecutive_frames:  # TODO: add functionality for wrap around from max_frame_count
                if elem < frame_count - consecutive_frames:
                    white_gone.remove(elem)

        # if there are more than four consecutive frames where the white is missing, flag a foul
        if len(white_gone) > (consecutive_frames - 1):
            foul_flag = True
            foul_type += 'White ball has been potted.\n'

        # look for differences between the balls that were updated and the balls in frame.balls
        for ball in frame.balls:
            ball_in_updated = False
            for b in updated_balls:
                if b.loc[0] == ball.loc[0]:
                    ball_in_updated = True
            if not ball_in_updated:
                balls_gone.append((ball, frame_count))
        # remove any old balls recorded in balls_gone, this may arise due to inconsistent hough circles results
        for elem in balls_gone:
            if elem[1] < frame_count - consecutive_frames:
                balls_gone.remove(elem)
        # print('Balls gone: ', balls_gone)

        # once balls_gone is longer than or equal to 5 elements, check the balls that are gone
        if len(balls_gone) >= consecutive_frames:
            to_be_removed = []
            for elem in balls_gone:
                count_frames_gone = 0
                for e in balls_gone:
                    if elem[0].loc[0] == e[0].loc[0]:
                        count_frames_gone += 1

                if count_frames_gone > (consecutive_frames-1):  # if the ball is gone in last five frames remove it
                    print('Removed: ', elem[0].colour)
                    if elem[0].colour in ball_to_hit:  # the correct ball colour has been pocketed
                        if len(frame_reds) >= 1:
                            if 'red' in ball_to_hit:
                                ball_to_hit = ['black', 'pink', 'blue', 'green', 'yellow', 'brown']
                            else:
                                ball_to_hit = ['red']
                        else:
                            # TODO: review that this works for second stage of break
                            ball_to_hit = Ball.ball_order[ball_index + 1]
                    else:
                        foul_flag = True
                        foul_type += 'Failed to pot the correct ball colour.\n'
                    frame.balls.remove(elem[0])
                    additional_points += Ball.colour_point_list[elem[0].colour]  # ball has been potted, find points
                    for i in balls_gone:  # empty the balls_gone list of the removed ball
                        if i[0].colour == elem[0].colour:
                            to_be_removed.append(i)
                    for i in to_be_removed:
                        if i in balls_gone:
                            balls_gone.remove(i)
                    break
        # balls which have been potted (or which have left the table) have been removed
        # --------------------------------------------------------------------------------------------------------------
        # Foul and game checks

        # check if balls are moving
        if len(frame.white_ball.ball.loc) >= 5:  # if there are at least five frames to check
            balls_moving = frame.balls_moving()
            if balls_moving:
                # print('Wait, turn is in progress')
                first_ball = white_ball.first_collision(frame.balls)
            else:
                # print('Balls are not moving, take shot')
                first_ball = None
            # print('First ball: ', first_ball)
            if first_ball is not None:
                # print(f'White ball hit the {first_ball.colour} ball!')
                if first_ball.colour not in ball_to_hit:
                    foul_flag = True
                    foul_type += 'Failed to hit the correct ball colour. \n'

        if foul_flag:
            print('Break is over, foul has occurred. \nFoul: ', foul_type)
            exit()

        # update player's score
        frame.update_score(additional_points)

        # --------------------------------------------------------------------------------------------------------------
        # Image Visuals

        # The following code segment draws a line behind the ball which shows it's path
        thickness = 8
        for i in range(1, len(white_ball.ball.loc)):
            cv2.line(img, white_ball.ball.loc[i - 1], white_ball.ball.loc[i],
                     colours_bgr[white_ball.ball.colour], thickness)
        for ball in frame.balls:
            # print(ball.colour)  # debugging
            for i in range(1, len(ball.loc)):
                # if ball.loc[i] != (0, 0) and ball.loc[i - 1] != (0, 0):
                cv2.line(img, ball.loc[i - 1], ball.loc[i], colours_bgr[ball.colour], thickness)

        # make the captured image larger and show it on screen
        img = cv2.resize(img, (960, 540))
        cv2.imshow("Video", img)
        frame_count += 1

        print('Player\'s current score: ', frame.obtain_scores())

        # show the player's current score on the gui window
        # while True:
        #     window.refresh()
        #     event, value = window.Read()
        #     if event == 'EXIT' or event is None:
        #         break  # exit button clicked

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        # end of while True:
        # ==============================================================================================================
    # window.close()  # close gui window
# end of main()
# =====================================================================================================================


# call the main function
if __name__ == '__main__':
    main()
