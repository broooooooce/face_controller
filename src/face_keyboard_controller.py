#!/usr/bin/env python

# Head/Face Controller
#
# Bruce Stracener - University of Arkansas for Medical Sciences
# started 01/30/18

import rospy
import cv2
import cv_bridge
import argparse
import baxter_interface
import baxter_external_devices

from sensor_msgs.msg import Image

from baxter_interface import (
    CHECK_VERSION,
    settings,
)
from baxter_core_msgs.msg import (
    HeadPanCommand, 
    HeadState, 
)

def face(x, y, z):
    pub = rospy.Publisher('/robot/xdisplay', Image, latch=True, queue_size=1)
    directory = '../img/BaxterFaces/BonusFaceFiles/'
    if x == "Angry" or x == "Disgusted":
        directory = '../img/BaxterFaces/StudyFaceFiles/'
        path = str(directory) + str(z) + str(x) + 'BaxterFace.jpg'
    elif x == "SleepOpen" or x == "SleepClosed":
        path = str(directory) + str(x) + str(z) + '.jpg'            
    else:
        path = str(directory) + str(x) + str(y) + str(z) + '.jpg'    
    print ('\x1b[1;32m' + 'Sucessfully published ' + path + '\x1b[0m')
    img = cv2.imread(path)
    msg = cv_bridge.CvBridge().cv2_to_imgmsg(img, encoding="passthrough")
    pub.publish(msg)
    return [x, y, z]

def head(x):
    head = baxter_interface.Head()
    y = head.pan()
    if x == 'Nod':
        head.command_nod()
        print ('\x1b[1;32m' + 'Nod action successfully completed.' + '\x1b[0m')
    if x == 'Forward':
        head.set_pan(0.0, speed = 0.05, timeout=0)
        print ('\x1b[1;32m' 
        + 'Look action successfully completed: Theta = %s.\x1b[0m' %y)
    if x == 'Left':
        if y <= 1.2:        
            head.set_pan(y + 0.25, speed=0.05, timeout=0)
            print ('\x1b[1;32m' 
            + 'Look action started successfully: Theta = %s.\x1b[0m' %y)
        else:
            print ('\x1b[0;31m'
            + 'Can not move further left; extreme reached.'
            + '\x1b[0m')
    if x == 'Right':
        if y >= -1.2:        
            head.set_pan(y - 0.25, speed=0.05, timeout=0)
            print ('\x1b[1;32m' 
            + 'Look action started successfully: Theta = %s.\x1b[0m' %y)
        else:
            print ('\x1b[0;31m'
            + 'Can not move further right; extreme reached.'
            + '\x1b[0m')

def map_keyboard(x):
    if x == 1:
        start_expression = 'Neutral'
        start_eyes = 'SW'
        start_color = 'Gray'
        state=[start_expression, start_eyes, start_color]
        x = 0

    bindings = {
        'a': ('color', 'Gray', "BG Color:    Gray"),
        'b': ('color', 'Blue', "BG Color:    Blue"),
        'g': ('color', 'Green', "BG Color:    Green"),
        'o': ('color', 'Orange', "BG Color:    Orange"),
        'p': ('color', 'Purple', "BG Color:    Purple"),
        'r': ('color', 'Red', "BG Color:    Red"),
        'w': ('color', 'White', "BG Color:    White"),
        'y': ('color', 'Yellow', "BG Color:    Yellow"),
        '`': ('expression', 'Afraid', "Expression:  Afraid"),
        '1': ('expression', 'Angry', "Expression:  Angry"),
        '2': ('expression', 'Confused', "Expression:  Confused"),
        '3': ('expression', 'Disgusted', "Expression:  Disgusted"),
        '4': ('expression', 'Happy', "Expression:  Happy"),
        '5': ('expression', 'Joy', "Expression:  Joy"),
        '6': ('expression', 'Neutral', "Expression:  Neutral"),
        '7': ('expression', 'Reactive', "Expression:  Reactive"),
        '8': ('expression', 'Sad', "Expression:  Sad"),
        '9': ('expression', 'Sassy', "Expression:  Sassy"),
        '0': ('expression', 'Silly', "Expression:  Silly"),
        '-': ('expression', 'Surprise', "Expression:  Surprise"),
        '=': ('expression', 'Worried', "Expression:  Worried"),
        '[': ('sleep', 'SleepOpen', "Expression:  SleepOpen"),
        ']': ('sleep', 'SleepClosed', "Expression:  SleepClosed"),
        ';': ('eyes', 'NW', "Eye State:   Eyes NW"),
        '\'': ('eyes', 'NE', "Eye State:   Eyes NE"),
        '.': ('eyes', 'SW', "Eye State:   Eyes SW"),
        '/': ('eyes', 'SE', "Eye State:   Eyes SE"),
        ',': ('eyes', 'Blink', "Eye State:   Blink"),
        'c': ('head', 'Nod', "Head Action: Nod"),
        's': ('head', 'Forward', "Head Action: Look forward"),
        'z': ('head', 'Left', "Head Action: Pan left"),
        'x': ('head', 'Right', "Head Action: Pan right"),
    }                         

    done = False
    face(*state)
    print('\033[H\033[J' + '\x1b[1;34m' 
        + '\nControlling face and head. Press ? for help, Esc to quit.' 
        + '\x1b[0m')
    while not done and not rospy.is_shutdown():
        c = baxter_external_devices.getch()
        if c:
            #catch Esc or ctrl-c
            if c in ['\x1b', '\x03']:
                done = True
                rospy.signal_shutdown("Finished.")
            elif c in bindings:
                cmd = bindings[c]
                print('\x1b[1;34;1m' 
                    + '\nCOMMAND>>>  ' 
                    + '\x1b[0m' +' %s' % (cmd[2],))                
                if cmd[0] == 'head':
                    head(cmd[1])
                elif cmd[0] == 'expression':
                    state = face(cmd[1], state[1], state[2])
                elif cmd[0] == 'sleep':
                    state = face(cmd[1], state[1], state[2])
                elif cmd[0] == 'color':
                    if (state[0] == 'Angry' 
                    or state[0] == 'Disgusted'):
                        print('\x1b[0;31m' 
                        + 'White background is not available when '
                        + 'Baxter is ' 
                        + '\x1b[1;31m' + 'angry' + '\x1b[0;31m' + ', or ' 
                        + '\x1b[1;31m' + 'disgusted' + '\x1b[0;31m' + '.' 
                        + '\x1b[0m')
                    else:
                        state = face(state[0], state[1], cmd[1])
                elif cmd[0] == 'eyes':
                    if (state[0] == 'Angry' 
                    or state[0] == 'Disgusted' 
                    or state[0] == 'SleepOpen' 
                    or state[0] == 'SleepClosed'):
                        print('\x1b[0;31m' 
                        + 'Eye movements are not available when '
                        + 'Baxter is ' 
                        + '\x1b[1;31m' + 'angry' + '\x1b[0;31m' + ', ' 
                        + '\x1b[1;31m' + 'disgusted' + '\x1b[0;31m' + ', or '
                        + '\x1b[1;31m' + 'sleeping' + '\x1b[0;31m' + '.' 
                        + '\x1b[0m')
                    elif cmd[1] == 'Blink':
                        face(state[0], 'Blink', state[2])
                        rospy.sleep(0.075)
                        face(*state)
                    else:                                 
                        state = face(state[0], cmd[1], state[2])
            else:
                #print("\nkey bindings: ")
                print('\n  \x1b[0;34m<\x1b[1;37mEsc\x1b[0;34m>  '
                + '\x1b[1;36m' + 'Quit')
                print('    \x1b[0;34m<\x1b[1;37m?\x1b[0;34m>  '
                + '\x1b[1;36m' + 'Help\n')
                for key, val in sorted(bindings.items(),
                                       key=lambda x: x[1][2]):
                    print('\x1b[0;34m    <\x1b[1;37m' +
                    '%s\x1b[0;34m>  \x1b[1;36m%s'
                     % (key, val[2]))

def main():
    print("Initializing node... ")
    rospy.init_node("face_and_head_keyboard_controller", anonymous=True)
    print("Getting robot state... ")
    rs = baxter_interface.RobotEnable(CHECK_VERSION)
    init_state = rs.state().enabled

    def clean_shutdown():
        print("\nExiting example...")
        if not init_state:
            print("Disabling robot...")
            rs.disable()
    rospy.on_shutdown(clean_shutdown)

    print("Enabling robot... ")
    rs.enable()

    map_keyboard(1)

    print("Done.")

if __name__ == '__main__':
    main()

