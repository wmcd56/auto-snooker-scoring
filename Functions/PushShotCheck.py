import cv2
import numpy as np
import PySimpleGUI as sg
import json
import time

from Classes.Frame import Frame
from Classes.WhiteBall import WhiteBall
from Classes.Ball import Ball
from Classes.Player import Player

from CVFunctions.CaptureFrame import capture_frame
from CVFunctions.FindBalls import find_balls
from CVFunctions.FindPockets import find_pockets
from Functions.BallVelocity import ball_velocity
from Functions.CueSearch import cue_search
from Functions.CueTipVelocity import cue_tip_velocity
from Functions.PixelsDistance import pixels_distance
from Functions.FreeBallSearch import free_ball_search


def print2app(string, window):
    window['print_line'].update(string)


fnt = 'Arial 18'
layout = [[sg.Text("Player's current score: ", font=fnt), sg.Text("   ", font=fnt, key='score')],
                    [sg.Text("Ball on: ", font=fnt), sg.Text("                                  "
                                                             "                                  "
                                                             "                                  ",
                                                             font=fnt, key='ball')],
                    [sg.Text("                                                                  "
                             "                                                                  ",
                             font=fnt, key='print_line')],
                    [sg.Button('Finish', font=fnt), sg.Button('EXIT', font=fnt)],
                    [sg.Text("                                         ", font=fnt, key='final output')]]

window = sg.Window("AutoSnooker", layout, size=(800, 250))

# cap_res = (1920, 1080)
cap_res = (1280, 960)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # comment out for small set up
cap.set(3, cap_res[0])
cap.set(4, cap_res[1])
img, original = capture_frame(cap)
cv2.imshow('cue tips', original)
cv2.waitKey(0)
# cue_colour_calibration(original)
p1_cue_tip_list = []
p2_cue_tip_list = []

frame_count = 0
max_frames = 50
max_frame_count = 200
hough_param1, hough_param2 = 4.6, 15
min_radius = 20
max_radius = 30
L, a = 0.9, 1.25
ball_number = 5  # should be taken as user input
ball_on = ['red']

white_gone = []

c1_velocity = None
c2_velocity = None

with open('C:/Users/mcdon/Desktop/AutoSnooker/Resources/colours_bgr_original.txt', 'r') as file:
    colours_bgr_original = json.load(file)

# Find or load pockets
with open('C:/Users/mcdon/Desktop/AutoSnooker/Resources/pockets.txt', 'r') as file:
    pockets = json.load(file)

# pockets = find_pockets(cap, min_radius=min_radius, max_radius=max_radius, hough_param1=3.3, hough_param2=100)
print(pockets)
for pocket in pockets:
    centre = (int(pocket[0][0]), int(pocket[0][1]))
    radius = int(pocket[1])
    cv2.circle(original, centre, radius, (0, 255, 0), 2)
cv2.imshow('pockets', original)
cv2.waitKey(0)

print("place all balls in position")
time.sleep(5)

# Find the balls that have been laid on the table (average over consecutive frames)
consecutive_frames = 100
min_frames = 10
votes = 0
whites_found = []
balls_found = []


# use voting algorithm to establish exactly what circles are balls
for i in range(consecutive_frames):
    sg.OneLineProgressMeter('Progress', i, consecutive_frames-1, 'key')
    img, original = capture_frame(cap, L, a)  # captures a frame and performs the necessary preprocessing
    white_ball, balls = find_balls(img, 4, hough_param2, mode='Initial',
                                   show_image=False, pockets=pockets, min_radius=min_radius, max_radius=max_radius)
    print(len(balls))
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






while True:
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
    # search for cues

    b1, b2 = cue_search(original)
    if b1[0] is not None:
        b1_area = cv2.contourArea(b1[0], False)
    if b2[0] is not None:
        b2_area = cv2.contourArea(b2[0], False)

    colour = [0, 0, 255]

    if b1[0] is not None and (b1_area >= 200):
        p1_cue_tip_list.append(b1)
        cv2.drawContours(original, [b1[0]], 0, colour, thickness=3)
        # print(f'cue tip list: {p1_cue_tip_list[-1]}')
        # print(f'cue tip box x y: {p1_cue_tip_list[-1][0][0]}')
        if len(p1_cue_tip_list) > 10:
            c1_velocity = cue_tip_velocity(p1_cue_tip_list)
            # print(f'cue speed: {c1_velocity[0]}, direction: {c1_velocity[1]}')

    if b2[0] is not None and (b2_area >= 200):
        p2_cue_tip_list.append(b2)
        cv2.drawContours(original, [b2[0]], 0, colour, thickness=3)
        if len(p2_cue_tip_list) > 10:
            c2_velocity = cue_tip_velocity(p2_cue_tip_list)
            # print(f'cue speed: {c2_velocity[0]}, direction: {c2_velocity[1]}')


    # --------------------------------------------------------------------------------------------------------------
    # find the balls in the new image & update locations (track)
    balls_on_table = find_balls(img, hough_param1, hough_param2, show_image=False)

    # ensure that no pocket is recognised as a ball
    for ball in balls_on_table:
        for pocket in pockets:
            # if the distance between the recognised ball and pocket is less than the radius of the pocket remove it
            if pixels_distance(ball.loc[0], pocket[0]) <= pocket[1]:
                balls_on_table.remove(ball)

    white_on_table = white_ball.track_white(balls_on_table)
    if len(white_ball.ball.loc) > min_frames:
        white_v = white_ball.ball.ball_velocity()
        # print(f'white speed: {white_v[0]}, direction: {white_v[1]}')
    # if the white ball is not on the table record the frame number
    if white_on_table is False:
        white_gone.append(frame_count)

    updated_balls = frame.track_balls(balls_on_table)


    ball_velocities = []
    for ball in frame.balls:
        if len(ball.loc) > min_frames:
            ball_velocities.append(ball_velocity(ball))
            ball.ball_velocity()

    if c1_velocity is not None and len(ball_velocities) > 0:
        for v in ball_velocities:
            if (white_v[1] > 0) and (c1_velocity[1] > 0):
                # if the distance between the cue and the white ball is less than the white ball radius plus the
                # distance from the centre of the tip to the corner then they are touching (+5 buffer)
                if ((pixels_distance(p1_cue_tip_list[-1][1], white_ball.ball.loc[0])) <=
                (white_ball.ball.radius + pixels_distance(p1_cue_tip_list[-1][1], p1_cue_tip_list[-1][0][0]) + 8)):
                    print('cue touching white')
                    if v[0] > 0:
                        if (v[0] - 5 <= white_v[0] <= v[0] + 5) and (v[0] - 5 <= c1_velocity[0] <= v[0] + 5):
                            print2app('Push shot detected', window)
                            event, values = window.Read(timeout=1)
                            if event == 'EXIT' or event is None:
                                break  # exit button clicked
                            time.sleep(5)
                            print2app('', window)
                            print('PUSH SHOT 1')
                        elif (v[0] >= 2):
                            print2app('Push shot detected', window)
                            event, values = window.Read(timeout=1)
                            if event == 'EXIT' or event is None:
                                break  # exit button clicked
                            time.sleep(5)
                            print2app('', window)
                            print('PUSH SHOT 2')
    # TODO change ball velocities to use ball.velocity so that distances can be compared between the cue tip and ball
    if c2_velocity is not None and len(ball_velocities) > 0:
        for v in ball_velocities:
            if (white_v[1] > 0) and (c2_velocity[1] > 0):
                # if the distance between the cue and the white ball is less than the white ball radius plus the
                # distance from the centre of the tip to the corner then they are touching (+5 buffer)
                if ((pixels_distance(p2_cue_tip_list[-1][1], white_ball.ball.loc[0])) <=
                (white_ball.ball.radius + pixels_distance(p2_cue_tip_list[-1][1], p2_cue_tip_list[-1][0][0]) + 8)):
                    print('cue touching white')
                    if v[0] > 0:
                        if (v[0] - 5 <= white_v[0] <= v[0] + 5) and (v[0] - 5 <= c2_velocity[0] <= v[0] + 5): # and
                            # (pixels_distance()):
                            print2app('Push shot detected', window)
                            event, values = window.Read(timeout=1)
                            if event == 'EXIT' or event is None:
                                break  # exit button clicked
                            time.sleep(5)
                            print2app('', window)
                            print('PUSH SHOT 1')
                        elif (v[0] >= 2):
                            print2app('Push shot detected', window)
                            event, values = window.Read(timeout=1)
                            if event == 'EXIT' or event is None:
                                break  # exit button clicked
                            time.sleep(5)
                            print2app('', window)
                            print('PUSH SHOT 2')

    event, values = window.Read(timeout=1)
    if event == 'EXIT' or event is None:
        break  # exit button clicked

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

    snooker_out = free_ball_search(white_ball, frame.balls, ball_on, True, original)

    if snooker_out is not None:
        if snooker_out[0] is True:
            print2app(snooker_out[1], window)
    else:
        print2app('', window)

    cv2.imshow('live', original)
    frame_count += 1
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
