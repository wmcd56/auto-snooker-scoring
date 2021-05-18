"""
Automatic Snooker Scoring System
Undertaken as part of the Masters of Engineering at Maynooth University
Started    - September 2020
Completed  -


Author: William McDonnell
Specific code segments sourced from others are cited with the url from where they were obtained
Further information on the operation  of this system can be found in the accompanying class and sequence diagrams

Version: 2.0
Version aim: to incorporate functionality for a match play scenario
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
from CVFunctions.FindPockets import find_pockets
from CVFunctions.BGRtoHSV import bgr_to_hsv
# from CVFunctions.ClassifyHSV import classify_hsv
from CVFunctions.ClassifyBGR import classify_bgr
from Functions.CalibrateColours import calibrate_colours
from Functions.CalibrateCircleParameters import calibrate_circle_params
from Functions.PixelsDistance import pixels_distance
from Functions.FreeBallSearch import free_ball_search
from CVFunctions.CaptureFrame import capture_frame


def run_start_menu(fnt):
    menu_layout = [[sg.Text("Enter number of balls on table: ", font=fnt), sg.Input(key='ball number')],
                    [sg.Text("Select game mode.", font=fnt)],
                    [sg.Button('Practice', font=fnt), sg.Button('Match', font=fnt)],
                    [sg.Button('EXIT', font=fnt)]]
    window = sg.Window("AutoSnooker", menu_layout, size=(600, 250))

    while True:
        event, values = window.Read()
        if event:
            ball_number = values['ball number']
            window.close()
            return event, int(ball_number)


def print2app(string, window):
    window['print_line'].update(string)


def open_adjusting_window(names, frame):
    adjusting_layout = [[sg.Text("Select a player to adjust their score.", font=fnt)],
              [sg.Combo(names, key='player to adjust')],
              [sg.Combo(['Add', 'Subtract'], key='add or subtract')],
              [sg.Text("Input the amount of points.", font=fnt), sg.Input(key='number of points')],
              [sg.Text("Select the player who will take the next turn.", font=fnt)],
              [sg.Combo(names, key='next turn')],
              [sg.Button('EXIT', font=fnt)]]
    adjusting_window = sg.Window("AutoSnooker - Adjust scores", adjusting_layout, size=(600, 250))

    while True:
        event, values = adjusting_window.Read()
        if event:
            player_to_adjust = values['player to adjust']
            if values['add or subtract'] == 'Subtract':
                multiplier = -1
            else:
                multiplier = 1
            player_on = values['next turn']

            if frame.player1.name == player_on:
                frame.set_current_player(frame.player1)
            elif frame.player2.name == player_on:
                frame.set_current_player(frame.player2)

            if frame.player1.name == player_to_adjust:
                frame.player1.current_points += multiplier * int(values['number of points'])
            elif frame.player2.name == player_to_adjust:
                frame.player2.current_points += multiplier * int(values['number of points'])

            adjusting_window.close()
            break

def main(window, mode, ball_number):
    # ==================================================================================================================
    # FRAME SET-UP

    # For different lighting conditions the colours should be calibrated first
    # This function requests the user to place balls of a certain colour within view of the camera
    # Can be run separately from the main file if calibrating once before multiple games

    cap_res = (1280, 960)

    # hough_param1, hough_param2 = calibrate_circle_params(cap_res)
    hough_param1, hough_param2 = 4.6, 15
    hough_param1 = 4
    L, a = 0.9, 1.25
    # colours = calibrate_colours(L=L, a=a)

    print("starting...")
    # time.sleep(10)
    # ------------------------------------------------------------------------------------------------------------------
    # access a web cam check

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # comment out for small set up
    # cap_res = (1024, 780)  # small set-up

    # cap_res = (1920, 1080)  # big set-up
    cap.set(3, cap_res[0])
    cap.set(4, cap_res[1])

    img, original = capture_frame(cap)
    # cv2.imshow("Table", original)

    # cv2.imshow('test', img)
    # cv2.waitKey(0)
    # ------------------------------------------------------------------------------------------------------------------

    # setup complete
    # ==================================================================================================================
    # Variable initialisation and locating balls
    # ------------------------------------------------------------------------------------------------------------------
    # start gui
    score = 0
    # fnt = 'Arial 14'
    # layout = [[sg.Text("Player's current score: ", font=fnt), sg.Text("          ", font=fnt, key='score')],
    #           [sg.Text("Ball to hit: ", font=fnt), sg.Text("                     ", font=fnt, key='ball to hit')],
    #           [sg.Button('Input score manually', font=fnt, visible=True)],
    #           [sg.Text("                                        ", font=fnt, key='manual score text'),
    #            sg.Input(key='additional score', visible=False)],
    #           [sg.Button('Input foul manually', font=fnt, visible=True)],
    #           [sg.Text("                                        ", font=fnt, key='manual foul text'),
    #            sg.Input(key='manual foul', visible=False)],
    #           [sg.Button('Submit', font=fnt, key='_SUBMIT_', visible=False),
    #            sg.Button('Cancel', font=fnt, key='_CANCEL_', visible=False)],
    #           [sg.Button('Finish', font=fnt)],
    #           [sg.Text("                                         ", font=fnt, key='final output')]]
    #
    # window = sg.Window("AutoSnooker", layout, size=(400, 600))

    # ------------------------------------------------------------------------------------------------------------------
    # Find pockets

    with open('C:/Users/mcdon/Desktop/AutoSnooker/Resources/pockets.txt', 'r') as file:
        pockets = json.load(file)

    # pockets = find_pockets(cap)
    print(pockets)
    for pocket in pockets:
        centre = (int(pocket[0][0]), int(pocket[0][1]))
        radius = int(pocket[1])
        cv2.circle(original, centre, radius, (100, 255, 0), 6)
    cv2.imshow('pockets', original)
    cv2.waitKey(0)

    print("place all balls in position")
    # time.sleep(10)

    # Find the balls that have been laid on the table (average over consecutive frames)
    consecutive_frames = 100
    votes = 0
    whites_found = []
    balls_found = []
    # use voting algorithm to establish exactly what circles are balls
    for i in range(consecutive_frames):
        # sg.OneLineProgressMeter('Progress', i, consecutive_frames, 'key')
        img, original = capture_frame(cap, L, a)  # captures a frame and performs the necessary preprocessing
        white_ball, balls = find_balls(img, hough_param1, hough_param2, mode='Initial',
                                        show_image=False, pockets=pockets, min_radius=20, max_radius=30)
        if white_ball is not None:
            if i < 5:
                whites_found.append([white_ball, votes])
            elif i < 20:
                distances = []
                for w in whites_found:
                    distances.append(pixels_distance(w[0].ball.loc[0], white_ball.ball.loc[0]))
                if min(distances) >= white_ball.ball.radius:
                    whites_found.append([white_ball, votes])
            else:
                for w in whites_found:
                    if pixels_distance(w[0].ball.loc[0], white_ball.ball.loc[0]) < 10:
                        w[1] += 1

        for ball in balls:
            if i < 1:
                balls_found.append([ball, votes])
            elif i < 20:
                distances = []
                for b in balls_found:
                    distances.append(pixels_distance(b[0].loc[0], ball.loc[0]))
                min_diff = min(distances)
                index = distances.index(min_diff)
                if min_diff >= ball.radius:
                    balls_found.append([ball, votes])
                elif balls_found[index][0].colour != ball.colour:
                    balls_found.append([ball, votes])
            else:
                for b in balls_found:
                    if (pixels_distance(b[0].loc[0], ball.loc[0]) < 10) and (b[0].colour == ball.colour):
                        b[1] += 1

    # sort by votes highest voted white ball is accepted as white
    length = len(whites_found)
    for index in range(0, length):
        for j in range(0, length - index - 1):
            if whites_found[j][1] > whites_found[j + 1][1]:
                temp = whites_found[j]
                whites_found[j] = whites_found[j + 1]
                whites_found[j + 1] = temp
    whites_found.reverse()
    print('White votes: ', whites_found[0][1])
    white_ball = whites_found[0][0]

    # only accept the {ball_number} balls of highest votes
    length = len(balls_found)
    for index in range(0, length):
        for j in range(0, length - index - 1):
            if balls_found[j][1] > balls_found[j + 1][1]:
                temp = balls_found[j]
                balls_found[j] = balls_found[j + 1]
                balls_found[j + 1] = temp
    balls_found.reverse()
    balls_found = balls_found[0: ball_number-1]
    balls_output = ''
    for ball in balls_found:
        balls_output += f'({ball[0].colour}, {ball[1]}), '
    print('balls found: ', balls_output)
    balls = []
    for ball in balls_found:
        balls.append(ball[0])  # don't add the votes to the ball type

    # ensure that no pocket is recognised as a ball
    for ball in balls:
        for pocket in pockets:
            # if the distance between the recognised ball and the pocket is less than the radius of the pocket remove it
            if pixels_distance(ball.loc[0], pocket[0]) <= pocket[1]:
                balls.remove(ball)

    if white_ball is not None:
        frame = Frame(balls, white_ball=white_ball)  # frame is now set up
    else:
        print('White ball not found, restart the application')
        exit()
    # ------------------------------------------------------------------------------------------------------------------
    # variable initialisation

    # for colour lines tracking
    # TODO: Replace this file directory with something more robust
    with open('C:/Users/mcdon/Desktop/AutoSnooker/Resources/colours_bgr_original.txt', 'r') as file:
        colours_bgr_original = json.load(file)

    ball_to_hit = ['red']  # first ball to hit must be red, this is updated once a red is hit
    ball_pocketed = []  # this list holds the balls which were pocketed in the last shot
    ball_index = -1  # used in the second stage, to get what ball should be pocketed next, starts at -1 as +1 is added
    foul_flag = False
    foul_type = ''
    white_gone_flag = False

    manual_foul = None
    manual_additional_score = None

    balls_added = []  # used for spotting balls back on the table
    balls_gone = []  # used to check balls that have left the table
    white_gone = []  # used to count frames that the white ball has not been registered

    initial_white_pos = (0, 0)
    balls_moving = False
    balls_moving_prev = False
    shot_in_progress = False
    shot_in_progress_list = []
    white_moving = False
    white_moving_prev = False
    first_ball = None
    first_ball_flag = False
    white_moving_list = []
    white_moving_count = []
    white_still_count = []
    white_ball_stopped = False

    turn_ended = False
    turn_event = None
    foul_points = 0

    frame_count = 0  # used to ensure certain situations occur in subsequent frames
    max_frame_count = 300000
    consecutive_frames = 100  # used for the number of consecutive frames needed to register a ball as having been potted
    min_frames = 10

    while True:
    # while frame_count < 1000:
        # ==============================================================================================================
        # time.sleep(1)  # debugging
        # print('Ball to hit: ', ball_to_hit)
        # sg.OneLineProgressMeter('My meter title', frame_count, max_frame_count, 'key')
        # --------------------------------------------------------------------------------------------------------------
        # initialise variables
        if frame_count == max_frame_count:  # arbitrarily chosen frame cap
            frame_count = 0

        reds_on_table = []  # list to hold the red balls detected to be on the table in this turn
        frame_colours = []
        frame_reds = []  # list of red balls registered to be in the game
        updated_balls = []  # list of balls which have been successfully updated within this loop
        indexes = []  # index of red balls in frame_reds

        additional_points = 0
        # --------------------------------------------------------------------------------------------------------------
        # capture new frame
        img, original = capture_frame(cap)  # the second output is the original image

        # --------------------------------------------------------------------------------------------------------------
        # find the balls in the new image & update locations (track)
        balls_on_table = find_balls(img, hough_param1, hough_param2, show_image=False)

        # ensure that no pocket is recognised as a ball
        for ball in balls_on_table:
            for pocket in pockets:
                # if the distance between the recognised ball and pocket is less than the radius of the pocket remove it
                if pixels_distance(ball.loc[0], pocket[0]) <= pocket[1]:
                    balls_on_table.remove(ball)

        white_on_table = frame.white_ball.track_white(balls_on_table)
        # if the white ball is not on the table record the frame number
        if white_on_table is False:
            white_gone.append(frame_count)
        if frame_count > 50:
            frame.update_velocities()
        updated_balls = frame.track_balls(balls_on_table)
        # frame.forecast_balls()
        # frame.forecast_balls(frame.white_ball.ball, 5)
        print('White current pos: ', frame.white_ball.ball.loc[0])
        print('Forecasted white pos: ', frame.white_ball.ball.forecast_position)
        # tracking is complete
        # --------------------------------------------------------------------------------------------------------------
        # Update frame.balls with new information
        # 1. Ensure white ball has not been pocketed
        # 2. Add spotted balls back to frame.balls
        # 3. Find the balls in frame.balls that were not found in the new image, remove them and update score

        # 1. """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
        # TODO: review this, currently player will still be awarded a point if the red ball is pocketed with the white
        # first ensure that the white ball has not been pocketed, if so flag it and award no points
        # remove old elements of white_gone
        for elem in white_gone:
            if frame_count == 0:
                white_gone = []
            # if frame_count >= consecutive_frames:  # TODO: add functionality for wrap around from max_frame_count
            if elem <= (frame_count - consecutive_frames):
                white_gone.remove(elem)
        # print(len(white_gone))
        # if there are more than {consecutive_frames} where the white is missing, flag a foul
        if len(white_gone) >= consecutive_frames:
            foul_flag = True
            foul_type += 'White ball has been potted.\n'
            white_gone_flag = True

        # 2. """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
        # if more balls found in the image than in frame.balls, count consecutive frames, add to frame.balls after 5
        # to save on processing this only happens when an extra ball is found
        for ball in frame.balls:
            if ball.colour != 'red':
                frame_colours.append(ball.colour)
            else:
                frame_reds.append(ball.colour)
        # print(f'balls on table: {len(balls_on_table)}, frame balls: {len(frame.balls)}')

        if len(balls_on_table) > len(frame.balls):
            for b in balls_on_table:
                # TODO review this functionality to add white ball back in
                if (white_gone_flag is True) and (b.colour == 'white'):  # and (white_on_table is True):
                    balls_added.append((b, frame_count))
                elif (b.colour == 'red') or (b.colour == 'white') or (b.colour in frame_colours):
                    continue
                else:
                    balls_added.append((b, frame_count))

        # remove any old balls recorded in balls_added
        for elem in balls_added:
            # need to keep balls_added longer than consecutive_frames
            if elem[1] < (frame_count - consecutive_frames*1.5):
                balls_added.remove(elem)
        # if len(balls_added) >= 1:
            # print('Balls added: ', balls_added[0][0].colour)
        # once balls_added is longer than the required consecutive frames, check what balls have been added
        if len(balls_added) >= consecutive_frames:
            to_be_added = []
            to_remove = []
            # TODO add ball vote here
            for elem in balls_added:
                count_frames_present = 0
                for e in balls_added:
                    if pixels_distance(elem[0].loc[0], e[0].loc[0]) <= 10:
                        count_frames_present += 1
                        to_remove.append(e)
                # if the spotted ball has been present in the last consecutive_frames add it to frame.balls
                if count_frames_present >= consecutive_frames:
                    frame.balls.append(elem[0])
                    for e_remove in to_remove:
                        if e_remove in balls_added:
                            balls_added.remove(e_remove)
                    if elem[0].colour == 'white':
                        white_gone_flag = False
                    print(f'The {elem[0].colour} ball has been spotted.')
                    print2app(f'The {elem[0].colour} ball has been spotted.', window)
                    break

        # 3. """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
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

        # once balls_gone is longer than or equal to consecutive_frames, check the balls that are gone
        if len(balls_gone) >= consecutive_frames:
            to_be_removed = []
            for elem in balls_gone:
                count_frames_gone = 0
                for e in balls_gone:
                    if elem[0].loc[0] == e[0].loc[0]:
                        count_frames_gone += 1

                if count_frames_gone >= consecutive_frames:  # if the ball is gone in last consecutive frames remove it
                    pocketed = False  # assume it was removed illegally

                    for pocket in pockets:
                        # calculate the distance from where the ball was last seen to the pocket
                        distance = pixels_distance(elem[0].loc[0], pocket[0])
                        if distance <= pocket[1]+30:  # if the distance is less than the radius of pocket + 10
                            pocketed = True
                            print('Removed: ', elem[0].colour)
                            ball_pocketed.append(elem[0].colour)
                            if elem[0].colour in ball_to_hit:  # the correct ball colour has been pocketed
                                if len(frame_reds) > 1:
                                    if 'red' in ball_to_hit:
                                        ball_to_hit = Ball.ball_order
                                        print('Ball to hit: ', ball_to_hit)
                                    else:
                                        ball_to_hit = ['red']
                                else:
                                    # TODO: review that this works for second stage of break
                                    ball_to_hit = Ball.ball_order[ball_index + 1]
                            else:
                                foul_flag = True
                                foul_type += 'Failed to pot the correct ball colour.\n'
                            frame.balls.remove(elem[0])
                            if foul_flag is False:  # only award the points if no foul occurred in the shot
                                additional_points += Ball.colour_point_list[elem[0].colour]  # ball has been potted, find points
                            for i in balls_gone:  # empty the balls_gone list of the removed ball
                                if i[0].colour == elem[0].colour:
                                    to_be_removed.append(i)
                            for i in to_be_removed:
                                if i in balls_gone:
                                    balls_gone.remove(i)

                    if pocketed is True:
                        break
                    else:
                        foul_flag = True
                        foul_type += f'{elem[0].colour} ball left the table illegally.\n'
                        break
        # balls which have been potted (or which have left the table) have been removed
        # --------------------------------------------------------------------------------------------------------------
        # white ball fouls and game checks
        # 1. check for the first ball that the white collides with
        # 2. check to see if the white collided with a ball

        # remove old elements from lists
        if len(white_moving_list) > consecutive_frames:
            white_moving_list.pop(0)
        if len(shot_in_progress_list) > consecutive_frames:
            shot_in_progress_list.pop(0)


        # check if balls are moving
        if len(frame.white_ball.ball.loc) >= min_frames:  # if there are at least five frames to check
            balls_moving = frame.balls_moving(min_frames)
            if balls_moving:
                shot_in_progress = True
                shot_in_progress_list.append(shot_in_progress)
            else:
                shot_in_progress = False
                shot_in_progress_list.append(shot_in_progress)
            # if len(shot_in_progress_list) > 0:
            #     print(shot_in_progress_list[-1])
            white_moving = white_ball.ball.track_ball()
            white_moving_list.append([white_moving, frame_count])
            # for elem in white_moving_list:
            #     if elem[1] <= (frame_count - consecutive_frames):
            #         white_moving_list.remove(elem)

            # if the white ball started moving
            if len(white_moving_list) >= min_frames:
                if (white_moving_list[-1] and white_moving_list[-2]) and not \
                        (white_moving_list[-3] and white_moving_list[-4]):
                    print("white started moving")
                    first_ball_flag = False  # the white ball hasn't hit a ball yet
                    white_ball_stopped = False

            # for i in range(min_frames):
            #     white_moving = white_moving and white_moving_list[-i]
            if white_moving:
                if first_ball_flag is False:
                    first_ball = frame.white_ball.first_collision(frame.balls)
                if first_ball is not None:
                    first_ball_flag = True
            else:
                first_ball = None

            # determine if the white ball was moving and has now stopped
            out1 = True
            out2 = True
            if (len(white_moving_list) > (min_frames*4)) and (not white_ball_stopped):
                for i in range(1, min_frames*2 + 1):
                    out1 = out1 and white_moving_list[-i][0]

                for i in range(min_frames*2 + 1, ((min_frames * 4) + 1)):
                    out2 = out2 and white_moving_list[-i][0]

            if (not out1) and out2:
                white_ball_stopped = True
                print('First ball flag: ', first_ball_flag)
                # if the white ball is not still in the same position (false trigger of balls_moving)
                # if (initial_white_pos[0] - 5 <= white_ball.ball.loc[0][0] <= initial_white_pos[0] + 5) is False:
                if first_ball_flag is False:
                    foul_flag = True
                    foul_type += 'Failed to hit another ball with the cue ball. \n'
                    first_ball_flag = True
            if first_ball is not None:
                if first_ball.colour not in ball_to_hit:
                    foul_flag = True
                    foul_type += 'Failed to hit the correct ball colour. \n'

        white_moving_prev = white_moving
        # balls_moving_prev = balls_moving

        if manual_foul is not None:
            foul_flag = True
            foul_type = "Manually identified foul"

        if foul_flag:
            turn_ended = True
            print2app(f"Foul: {foul_type}", window)
            # window.close()
            # exit()

        # --------------------------------------------------------------------------------------------------------------
        # Update Players' scores and switch player if needed

        # update player's score
        if manual_additional_score is not None:
            additional_points += int(manual_additional_score)
        frame.update_score(frame.current_player, additional_points)

        # check to see if the turn is over
        # determine if the balls were moving and have now stopped
        out1 = True
        out2 = True
        if len(shot_in_progress_list) > (min_frames * 6):
            t1 = 0
            f1 = 0
            t2 = 0
            f2 = 0

            for i in range(1, min_frames * 3 + 1):
            # for i in shot_in_progress_list[-1: -(min_frames * 2 + 1)]:
                # out1 = out1  shot_in_progress_list[-i]
                if shot_in_progress_list[-i] is True:
                    t1 += 1
                else:
                    f1 += 1
            if t1 > f1:
                out1 = True
            else:
                out1 = False

            for i in range(min_frames * 3 + 1, ((min_frames * 6) + 1)):
                # out2 = out2  shot_in_progress_list[-i]
                if shot_in_progress_list[-i] is True:
                    t2 += 1
                else:
                    f2 += 1
            if t2 > f2:
                out2 = True
            else:
                out2 = False

        # print(f'Shot finished: {out1}, {not out2}')
        if out1 and (not out2):  # a shot has concluded
            if len(ball_pocketed) == 0:
                turn_ended = True
                turn_event = "Turn has ended. Failed to pocket a ball."
                print(turn_event)
                print2app(turn_event, window)
            else:
                ball_pocketed = []

        if mode == 'Match':
            # update opposite player's score for fouls committed
            if foul_flag is True:
                opposite_player = frame.get_opposite_player()
                frame.update_score(opposite_player, (-1 * foul_points))
                foul_flag = False

            if turn_ended is True:
                frame.switch_player()
                turn_ended = False

        elif mode == 'Practice':
            if turn_ended is True:
                output_str = 'Break is over, '
                output_str += foul_type
                if turn_event is not None:
                    output_str += turn_event
                print2app(output_str, window)

        # --------------------------------------------------------------------------------------------------------------
        # Image Visuals

        # The following code segment draws a line behind the ball which shows it's path
        thickness = 8
        for i in range(1, len(white_ball.ball.loc)):
            cv2.line(original, white_ball.ball.loc[i - 1], white_ball.ball.loc[i],
                     colours_bgr_original[white_ball.ball.colour], thickness)
        for ball in frame.balls:
            # print(ball.colour)  # debugging
            for i in range(1, len(ball.loc)):
                # if ball.loc[i] != (0, 0) and ball.loc[i - 1] != (0, 0):
                cv2.line(original, ball.loc[i - 1], ball.loc[i], colours_bgr_original[ball.colour], thickness)
        if white_ball is not None:
            if white_ball.ball.forecast_position is not None:
                cv2.line(original, tuple(white_ball.ball.loc[0]), tuple(white_ball.ball.forecast_position), [50, 245, 150], 5)


        # make the captured image larger and show it on screen
        # img = cv2.resize(img, (960, 540))
        cv2.imshow("Video", original)
        frame_count += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # --------------------------------------------------------------------------------------------------------------
        # GUI events and updates

        # TODO: update events for single and two players
        manual_foul = None
        manual_additional_score = None

        event, values = window.Read(timeout=1)
        if event == 'EXIT' or event is None:
            break  # exit button clicked

        # if the user prompts a manual score input
        if event == 'Input score manually':
            window['manual score text'].update("Manual score addition: ")
            window['additional score'].update(visible=True)
            window['_SUBMIT_'].update(visible=True)
            window['_CANCEL_'].update(visible=True)
            while True:
                event, values = window.Read(timeout=1)  # no timeout, the entire program is paused and awaits input
                if event == '_SUBMIT_':
                    manual_additional_score = values['additional score']
                    break
                elif event == '_CANCEL_':
                    break
            window['manual score text'].update("")
            window['additional score'].update(visible=False)
            window['_SUBMIT_'].update(visible=False)
            window['_CANCEL_'].update(visible=False)

        # if the user prompts a manual foul input
        if event == 'Input foul manually':
            window['manual foul text'].update("Manual foul input (points): ")
            window['manual foul'].update(visible=True)
            window['_SUBMIT_'].update(visible=True)
            window['_CANCEL_'].update(visible=True)
            while True:
                event, values = window.Read(timeout=1)  # no timeout, the entire program is paused and awaits input
                if event == '_SUBMIT_':
                    manual_foul = values['manual foul']
                    break
                elif event == '_CANCEL_':
                    break
            window['manual foul text'].update("")
            window['manual foul'].update(visible=False)
            window['_SUBMIT_'].update(visible=False)
            window['_CANCEL_'].update(visible=False)

        if event == 'Adjust Scores':
            open_adjusting_window([frame.player1.name, frame.player2.name], frame)

        # if the user prompts the program to finish
        if event == 'Finish':
            window['final output'].update(f"Final score: {frame.obtain_scores(frame.current_player)}")
            break

        # debugging and functionality check
        if manual_foul is not None:
            print(f'manual foul: {manual_foul}')
        if manual_additional_score is not None:
            print(f'manual additional score: {manual_additional_score}')

        window['ball'].update(ball_to_hit)
        if mode == 'Practice':
            window['score'].update(str(frame.obtain_scores(frame.current_player)))
        elif mode == 'Match':
            window['Player_on'].update(str(frame.get_current_player().name))
            window['P1_score'].update(str(frame.obtain_scores(frame.player1)))
            window['P2_score'].update(str(frame.obtain_scores(frame.player2)))

        window.refresh()

        # end of while True:
        # ==============================================================================================================
    # window.close()  # close gui window
# end of main()
# =====================================================================================================================

fnt = 'Arial 18'
break_layout = [[sg.Text("Player's current score: ", font=fnt), sg.Text("   ", font=fnt, key='score')],
                    [sg.Text("Ball on: ", font=fnt), sg.Text("                                  "
                                                             "                                  "
                                                             "                                  ",
                                                             font=fnt, key='ball')],
                    [sg.Text("                                                                  "
                             "                                                                  ",
                             font=fnt, key='print_line')],
                    [sg.Button('Finish', font=fnt), sg.Button('EXIT', font=fnt)],
                    [sg.Text("                                         ", font=fnt, key='final output')]]

match_layout = [[sg.Text("Player 1's current score: ", font=fnt), sg.Text("      ", font=fnt, key='P1_score')],
                [sg.Text("Player 2's current score: ", font=fnt), sg.Text("      ", font=fnt, key='P2_score')],
                [sg.Text("Current player: ", font=fnt), sg.Text("            ", font=fnt, key='Player_on')],
                [sg.Text("Ball on: ", font=fnt), sg.Text("                                  "
                                                         "                                  "
                                                         "                                  ",
                                                         font=fnt, key='ball')],
                [sg.Text("                                                                  "
                         "                                                                  ",
                         font=fnt, key='print_line')],

                # [sg.Button('Input score manually', font=fnt, visible=True)],
                [sg.Text("                                        ", font=fnt, key='manual score text'),
                 sg.Input(key='additional score', visible=False)],
                # [sg.Button('Input foul manually', font=fnt, visible=True)],
                #[sg.Text("                                        ", font=fnt, key='manual foul text'),
                 # sg.Input(key='manual foul', visible=False)],
                # [sg.Button('Submit', font=fnt, key='_SUBMIT_', visible=False),
                # sg.Button('Cancel', font=fnt, key='_CANCEL_', visible=False)],
                [sg.Button('Replace Balls', font=fnt)],
                [sg.Button('Adjust Current Player', font=fnt)],
                [sg.Button('Adjust Scores', font=fnt)],
                [sg.Button('Finish', font=fnt)],
                [sg.Text("                                         ", font=fnt, key='final output')]]


while True:
    mode, ball_number = run_start_menu(fnt)

    if mode == 'Practice':
        window = sg.Window("AutoSnooker", break_layout, size=(800, 250))
        break
    elif mode == 'Match':

        window = sg.Window("AutoSnooker", match_layout, size=(800, 600))
        break

# call the main function
if __name__ == '__main__':
    main(window, mode, ball_number)


