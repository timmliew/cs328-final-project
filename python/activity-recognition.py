import matplotlib
matplotlib.use('Agg')

# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 15:34:11 2016

Assignment A0 : Data Collection

@author: cs390mb

This Python script receives incoming unlabelled accelerometer data through
the server and uses your trained classifier to predict its class label.
The label is then sent back to the Android application via the server.

"""

import socket
import sys
import json
import threading
import numpy as np
import pickle
from features import extract_features # make sure features.py is in the same directory
from util import reorient, reset_vars
import time
import matplotlib.pyplot as plt

# TODO: Replace the string with your user ID
user_id = "102017"

count = 0

'''
    This socket is used to send data back through the data collection server.
    It is used to complete the authentication. It may also be used to send
    data or notifications back to the phone, but we will not be using that
    functionality in this assignment.
'''
send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
send_socket.connect(("none.cs.umass.edu", 9999))

# Load the classifier:

with open('classifier.pickle', 'rb') as f:
    classifier = pickle.load(f)

if classifier == None:
    print("Classifier is null; make sure you have trained it!")
    sys.exit()


def expectedposition(curtime):
    timediff = curtime
    if timediff < MOVETOHORNSUP:
        return "Attention", 0
    elif timediff < MOVETOATTENTION:
        return "HornsUp", 1
    elif timediff < MOVETOTRAILARMS:
        return "Attention", 0
    elif timediff < ENDTIME:
        return "TrailArms", 2
    else:
        return "none"

def onActivityDetected(actualactivity, expectedactivity):
    """
    Notifies the client of the current activity
    """

    ## use this to send buzz or sound that the person is in the wrong position
    send_socket.send(json.dumps({'user_id' : user_id, 'sensor_type' : 'SENSOR_SERVER_MESSAGE', 'message' : 'ACTIVITY_DETECTED', 'data': {'expectedactivity' : expectedactivity, 'actualactivity': actualactivity}}) + "\n")

def predict(window, runreview):
    """
    Given a window of accelerometer data, predict the activity label.
    Then use the onActivityDetected(activity) function to notify the
    Android must use the same feature extraction that you used to
    train the model.
    """

    print("Buffer filled. Run your classifier.")

    curtime = time.time()

    x = extract_features(window)
    activity = classifier.predict([x])
    actualpos = ''
    exppos = expectedposition(curtime)
    if int(activity[0]) == 0:
        print "Expected: %s, Actual: Attention" % exppos[0]
        onActivityDetected("Attention", exppos[0])
        actualpos = "Attention"
    elif int(activity[0]) == 1:
        print "Expected: %s, Actual: HornsUp" % exppos[0]
        onActivityDetected("HornsUp", exppos[0])
        actualpos = "HornsUp"
    elif int(activity[0]) == 2:
        print "Expected: %s, Actual: TrailArms" % exppos[0]
        onActivityDetected("TrailArms", exppos[0])
        actualpos = "TrailArms"

    # append here actual verus expected
    runreview["actual"]["x"].append(curtime-STARTTIME)
    runreview["actual"]["y"].append(activity[0])
    runreview["expected"]["x"].append(curtime-STARTTIME)
    runreview["expected"]["y"].append(exppos[1])
    return

#################   Server Connection Code  ####################

'''
    This socket is used to receive data from the data collection server
'''
receive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
receive_socket.connect(("none.cs.umass.edu", 8888))
# ensures that after 1 second, a keyboard interrupt will close
receive_socket.settimeout(1.0)

msg_request_id = "ID"
msg_authenticate = "ID,{}\n"
msg_acknowledge_id = "ACK"

def authenticate(sock):
    """
    Authenticates the user by performing a handshake with the data collection server.

    If it fails, it will raise an appropriate exception.
    """
    message = sock.recv(256).strip()
    if (message == msg_request_id):
        print("Received authentication request from the server. Sending authentication credentials...")
        sys.stdout.flush()
    else:
        print("Authentication failed!")
        raise Exception("Expected message {} from server, received {}".format(msg_request_id, message))
    sock.send(msg_authenticate.format(user_id))

    try:
        message = sock.recv(256).strip()
    except:
        print("Authentication failed!")
        raise Exception("Wait timed out. Failed to receive authentication response from server.")

    if (message.startswith(msg_acknowledge_id)):
        ack_id = message.split(",")[1]
    else:
        print("Authentication failed!")
        raise Exception("Expected message with prefix '{}' from server, received {}".format(msg_acknowledge_id, message))

    if (ack_id == user_id):
        print("Authentication successful.")
        sys.stdout.flush()
    else:
        print("Authentication failed!")
        raise Exception("Authentication failed : Expected user ID '{}' from server, received '{}'".format(user_id, ack_id))


try:
    print("Authenticating user for receiving data...")
    sys.stdout.flush()
    authenticate(receive_socket)

    print("Authenticating user for sending data...")
    sys.stdout.flush()
    authenticate(send_socket)

    print("Successfully connected to the server! Waiting for incoming data...")
    sys.stdout.flush()

    previous_json = ''

    sensor_data = []
    window_size = 10 # ~1 sec assuming 25 Hz sampling rate
    step_size = 10 # no overlap
    index = 0 # to keep track of how many samples we have buffered so far
    reset_vars() # resets orientation variables

    # set up timer to see what the activity should be vs what it is
    #start tracking motions
    STARTTIME = time.time()
    # starts in attention position for 5 seconds, keep clicks going
    MOVETOHORNSUP = STARTTIME + 5
    # from horns up position move back to attention for 5 seconds, keep clicks going
    MOVETOATTENTION = MOVETOHORNSUP + 5
    # from attention position move to trail arms for 5 seconds, keep clicks going
    MOVETOTRAILARMS = MOVETOATTENTION + 5
    # end the exercise
    ENDTIME = MOVETOTRAILARMS + 5

    runreview = {"actual": {"x":[], "y":[]}, "expected": {"x":[], "y":[]}}

    while (time.time() < ENDTIME):
        try:
            message = receive_socket.recv(1024).strip()
            json_strings = message.split("\n")
            json_strings[0] = previous_json + json_strings[0]
            for json_string in json_strings:
                try:
                    data = json.loads(json_string)
                except:
                    previous_json = json_string
                    continue
                previous_json = '' # reset if all were successful
                sensor_type = data['sensor_type']
                if (sensor_type == u"SENSOR_ACCEL"):
                    t=data['data']['t']
                    x=data['data']['x']
                    y=data['data']['y']
                    z=data['data']['z']

                    sensor_data.append(reorient(x,y,z))
                    index+=1
                    # make sure we have exactly window_size data points :
                    while len(sensor_data) > window_size:
                        sensor_data.pop(0)

                    if (index >= step_size and len(sensor_data) == window_size):
                        t = threading.Thread(target=predict, args=(np.asarray(sensor_data[:]),runreview,))
                        t.start()
                        index = 0

            sys.stdout.flush()
        except KeyboardInterrupt:
            # occurs when the user presses Ctrl-C
            print("User Interrupt. Quitting...")
            break
        except Exception as e:
            # ignore exceptions, such as parsing the json
            # if a connection timeout occurs, also ignore and try again. Use Ctrl-C to stop
            # but make sure the error is displayed so we know what's going on
            if (e.message != "timed out"):  # ignore timeout exceptions completely
                print(e)
            pass

    # use runreview down here to generate plot

    plt.figure()
    plt.plot(runreview["actual"]["x"], runreview["actual"]["y"], label="Actual",linewidth=10)
    plt.plot(runreview["expected"]["x"], runreview["expected"]["y"], label="Expected",linewidth=10)
    plt.yticks([0, 1, 2], ["Attention", "HornsUp", "TrailArms"])
    # plt.set_yticklabels(["Attention", "HornsUp", "TrailArms"])
    plt.title("Review of Run")
    plt.xlabel("Time")
    plt.ylabel("Position")
    plt.legend()
    plt.savefig('runreview.png')

except KeyboardInterrupt:
    # occurs when the user presses Ctrl-C
    print("User Interrupt. Qutting...")
finally:
    print >>sys.stderr, 'closing socket for receiving data'
    receive_socket.shutdown(socket.SHUT_RDWR)
    receive_socket.close()

    print >>sys.stderr, 'closing socket for sending data'
    send_socket.shutdown(socket.SHUT_RDWR)
    send_socket.close()
