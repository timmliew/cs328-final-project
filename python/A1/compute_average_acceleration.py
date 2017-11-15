# -*- coding: utf-8 -*-
"""
Created on Fri Nov  4 13:07:01 2016

@author: cs390mb

Data Collection : Data Processing
"""

import numpy as np
stored_data = np.array([])

def compute_average(data, send_notification):
    """
    Compute the average for each axis of accelerometer data every 100 samples.
    This method is called for each sample and the data is stored in "data".
    You can access it as follows:

        data['x'], data['y'], data['z'] or data['t']

    for the x-, y-, z-values and time respectively.
    """

    # TODO: Compute average acceleration and print value for each window
    global stored_data
    stored_data = np.append(stored_data, data)
    # this will start computing average for windows once it has seen 100 points, then clear down to 75 for the next 25 to come in
    if len(stored_data) == 100:
       print "x: " + str(sum(p['x'] for p in stored_data) / 100)
       print "y: " + str(sum(p['y'] for p in stored_data) / 100)
       print "z: " + str(sum(p['z'] for p in stored_data) / 100)
       print
       # does not need to store data for the first 25 as the new 25 will come in
       stored_data = np.delete(stored_data, range(25))
    return
