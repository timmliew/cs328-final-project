# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 15:34:11 2016

@author: cs390mb

Step Detection

This Python script receives incoming accelerometer data through the
server, detects step events and sends them back to the server for
visualization/notifications.

"""

import numpy as np
from filters import ButterworthFilter, ExponentialFilter

from save_display_data import CSVSaver

# TODO (optional): you can create additional CSVSaver objects here with different filenames to save multiple files
# (for example, if you want to compare different types of filtering on the same data)
csv_saver = CSVSaver("accel_data.csv")
stored_data = np.array([])
main_axis = ''
num_seen = 0
threshold = ''
# butterworth = ButterworthFilter(5)
startTime = 0
exponential = ExponentialFilter(50)
def detect_steps(data, on_step_detected, *args):
    """
    Accelerometer-based step detection algorithm.

    Implement your step detection algorithm. This may be functionally
    equivalent to your Java step detection algorithm if you like.
    Remember to use the global keyword if you would like to access global
    variables such as counters or buffers. When a step has been detected,
    call the onStepDetected method, passing in the timestamp:

        onStepDetected("STEP_DETECTED", timestamp)

    """

    timestamp = data['t']
    x = data['x']
    y = data['y']
    z = data['z']

    global stored_data
    global threshold
    global main_axis
    global num_seen
    global butterworth
    global exponential
    global startTime

    if startTime == 0:
        startTime = timestamp

    # filter using ButterworthFilter first
    # filtered_sample = butterworth.getFilteredValues([x, y, z])

    # then filter with the ExponentialFilter on top of the ButterworthFilter
    filtered_sample = exponential.getFilteredValues([x, y, z])

    current_sample = filtered_sample
    if len(stored_data):
        stored_data = np.append(stored_data, [current_sample], axis=0)
    else:
        stored_data = [current_sample]

    # TODO: Implement step detection algorithm
    if len(stored_data) == 25:
        maxx = max(p[0] for p in stored_data)
        maxy = max(p[1] for p in stored_data)
        maxz = max(p[2] for p in stored_data)
        if maxx > maxy and maxx > maxz:
            main_axis = 0
        elif maxy > maxx and maxy > maxz:
            main_axis = 1
        else:
            main_axis = 2
    elif len(stored_data) == 50:
        num_seen += 1

        # set every 50 samples
        if num_seen == 50:
            num_seen = 0
            threshold = ((max(p[main_axis] for p in stored_data) + min(p[main_axis] for p in stored_data)) / 2)
        stored_data = np.delete(stored_data, 0, 0)

    # This saves the data to accel_data.csv
    # TODO: You can plot this later using save_display_data.plot_csv_data("accel_data.csv")
    # TODO: You can (and should) change this to save the data after it's been filtered once you are doing filtering
    # (which will help you to determine window size and what filtering parameters to use)

    print current_sample[0],current_sample[1],current_sample[2],timestamp
    csv_saver.save_data_item([current_sample[0],current_sample[1],current_sample[2],timestamp])


    # TODO: call on_step_detected only when you detect a step:
    if len(stored_data) > 1 and main_axis != '' and threshold != '' and abs(max(p[main_axis] for p in stored_data)) - abs(threshold) > 7 :
        print('hi')
        step = timestamp - startTime
        if step > 200:
            previous_sample = stored_data[-2]
            if previous_sample[main_axis] > threshold and current_sample[main_axis] < threshold:
                on_step_detected("STEP_DETECTED", {"timestamp" : timestamp})
                startTime = timestamp

    return
