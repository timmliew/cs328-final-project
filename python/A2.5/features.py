# -*- coding: utf-8 -*-
"""
Created on Tue Sep 27 13:08:49 2016

@author: cs390mb

This file is used for extracting features over windows of tri-axial accelerometer 
data. We recommend using helper functions like _compute_mean_features(window) to 
extract individual features.

As a side note, the underscore at the beginning of a function is a Python 
convention indicating that the function has private access (although in reality 
it is still publicly accessible).

"""

import numpy as np


#####################################################################
# Statistical Feature
def _compute_statistical_features(window):
    statistical = []
    statistical = np.append(statistical, np.mean(window, axis=0))
    statistical = np.append(statistical, np.median(window, axis=0))
    statistical = np.append(statistical, np.var(window, axis=0))
    statistical = np.append(statistical, np.std(window, axis=0))
    statistical = np.append(statistical, np.amin(window, axis=0))
    statistical = np.append(statistical, np.amax(window, axis=0))
    return statistical


def _compute_magnitude(data):
    return np.sqrt(np.sum(np.square(data), axis=1))

def _compute_magnitude_features(window):
    magnitudes = _compute_magnitude(window)

    magnitude = []
    magnitude = np.append(magnitude, np.mean(magnitudes))
    magnitude = np.append(magnitude, np.median(magnitudes))
    magnitude = np.append(magnitude, np.var(magnitudes))
    magnitude = np.append(magnitude, np.std(magnitudes))
    magnitude = np.append(magnitude, np.amin(magnitudes))
    magnitude = np.append(magnitude, np.amax(magnitudes))
    # print(magnitude)
    return magnitude

#####################################################################
# FFT Feature
def _compute_fft_features(window):
    xVal = np.fft.rfft(window[:, 0]).astype(float)
    yVal = np.fft.rfft(window[:, 1]).astype(float)
    zVal = np.fft.rfft(window[:, 2]).astype(float)
    dominantX = xVal.argmax()
    dominantY = yVal.argmax()
    dominantZ = zVal.argmax()
    # print( np.array([dominantX, dominantY, dominantZ]) )
    return np.array([dominantX, dominantY, dominantZ])


def _compute_entropy_features(window):
    histo = np.histogram(window, bins = 10)[0]
    entropy = 0
    filterArr = [values for values in histo if values > 0]
    for values in filterArr:
        entropy += -values * np.log(values)
    # print(np.asarray(entropy))
    return np.asarray(entropy)


def extract_features(window):
    """
    Here is where you will extract your features from the data over
    the given window. We have given you an example of computing
    the mean and appending it to the feature matrix X.

    Make sure that X is an N x d matrix, where N is the number
    of data points and d is the number of features.

    """
    x = []
    x = np.append(x, _compute_statistical_features(window))
    x = np.append(x, _compute_magnitude_features(window))
    x = np.append(x, _compute_fft_features(window))
    x = np.append(x, _compute_entropy_features(window))
    return x
