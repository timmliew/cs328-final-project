# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 16:02:58 2016

@author: cs390mb

Assignment 2 : Activity Recognition

This is the starter script used to train an activity recognition
classifier on accelerometer data.

See the assignment details for instructions. Basically you will train
a decision tree classifier and vary its parameters and evalute its
performance by computing the average accuracy, precision and recall
metrics over 10-fold cross-validation. You will then train another
classifier for comparison.

Once you get to part 4 of the assignment, where you will collect your
own data, change the filename to reference the file containing the
data you collected. Then retrain the classifier and choose the best
classifier to save to disk. This will be used in your final system.

Make sure to chek the assignment details, since the instructions here are
not complete.

"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn import svm
from features import extract_features # make sure features.py is in the same directory
from util import slidingWindow, reorient, reset_vars
from sklearn import cross_validation, neighbors
from sklearn.metrics import confusion_matrix
import pickle
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score


# %%---------------------------------------------------------------------------
#
#		                 Load Data From Disk
#
# -----------------------------------------------------------------------------

print("Loading data...")
sys.stdout.flush()
data_file = 'final-data.csv'
data = np.genfromtxt(data_file, delimiter=',')
print("Loaded {} raw labelled activity data samples.".format(len(data)))
sys.stdout.flush()

# %%---------------------------------------------------------------------------
#
#		                    Pre-processing
#
# -----------------------------------------------------------------------------

print("Reorienting accelerometer data...")
sys.stdout.flush()
reset_vars()
reoriented = np.asarray([reorient(data[i,1], data[i,2], data[i,3]) for i in range(len(data))])
reoriented_data_with_timestamps = np.append(data[:,0:1],reoriented,axis=1)
data = np.append(reoriented_data_with_timestamps, data[:,-1:], axis=1)


# %%---------------------------------------------------------------------------
#
#		                Extract Features & Labels
#
# -----------------------------------------------------------------------------

# you may want to play around with the window and step sizes
window_size = 20
step_size = 20

# sampling rate for the sample data should be about 25 Hz; take a brief window to confirm this
n_samples = 1000
time_elapsed_seconds = (data[n_samples,0] - data[0,0]) / 1000
sampling_rate = n_samples / time_elapsed_seconds

feature_names = [
     "mean X", "mean Y", "mean Z",
     "median X", "median Y", "median Z",
     "var X", "var Y", "var Z",
     "stddev X", "stddev Y", "stddev Z",
     "min X", "min Y", "min Z",
     "max X", "max Y", "max Z",
     "mean mag", "median mag", "var Z",
     "stddev mag", "min mag", "max mag",
     "fftx", "ffty", "fftz",
     "entropy"]
class_names = ["Attention", "Horns Up", "Trail Arms"]

print("Extracting features and labels for window size {} and step size {}...".format(window_size, step_size))
sys.stdout.flush()

n_features = len(feature_names)

X = np.zeros((0,n_features))
y = np.zeros(0,)

for i,window_with_timestamp_and_label in slidingWindow(data, window_size, step_size):
    # omit timestamp and label from accelerometer window for feature extraction:
    window = window_with_timestamp_and_label[:,1:-1]
    # extract features over window:
    x = extract_features(window)
    # append features:
    X = np.append(X, np.reshape(x, (1,-1)), axis=0)
    # append label:
    y = np.append(y, window_with_timestamp_and_label[10, -1])

print("Finished feature extraction over {} windows".format(len(X)))
print("Unique labels found: {}".format(set(y)))
sys.stdout.flush()

# %%---------------------------------------------------------------------------
#
#		                    Plot data points
#
# -----------------------------------------------------------------------------

# We provided you with an example of plotting two features.
# We plotted the mean X acceleration against the mean Y acceleration.
# It should be clear from the plot that these two features are alone very uninformative.
print("Plotting data points...")
sys.stdout.flush()

def plotFeatures(feature1, feature2, index1, index2 ):
    plt.figure()
    formats = ['bo', 'go']
    for i in range(0,len(y),10): # only plot 1/10th of the points, it's a lot of data!
        plt.plot(X[i,index1], X[i,index2], formats[int(y[i])])
    plt.title("Relationship between " + feature1 + " and " + feature2)
    plt.xlabel(feature1)
    plt.ylabel(feature2)
    plt.show()


# plotFeatures("Mean Z", "Median Z", 2, 5)
# plotFeatures("Var Z", "Std. Dev. Z", 8, 11)
# plotFeatures("Min Z", "Max Z", 14, 17)
# %%---------------------------------------------------------------------------
#
#		                Train & Evaluate Classifier
#
# -----------------------------------------------------------------------------

n = len(y)
n_classes = len(class_names)

# TODO: Train and evaluate your decision tree classifier over 10-fold CV.
# Report average accuracy, precision and recall metrics.

cv = cross_validation.KFold(n, n_folds=10, shuffle=True, random_state=None)

def train_classifier(classifier, label):

    treeaprscores = {'accuracy_scores': 0, 'precision_scores': 0, 'recall_scores': 0}
    for i, (train_indexes, test_indexes) in enumerate(cv):
        print("Fold {}".format(i))
        X_train = X[train_indexes]
        y_train = y[train_indexes]
        X_test = X[test_indexes]
        y_test = y[test_indexes]

        classifier.fit(X_train, y_train)
        y_pred = classifier.predict(X_test)
        conf = confusion_matrix(y_test, y_pred)

        treeaprscores['accuracy_scores'] = accuracy_score(y_test, y_pred) + treeaprscores['accuracy_scores']
        treeaprscores['precision_scores'] = precision_score(y_test, y_pred, average='macro') + treeaprscores['precision_scores']
        treeaprscores['recall_scores'] = recall_score(y_test, y_pred, average='macro') + treeaprscores['recall_scores']
    print treeaprscores, label


# tree32 = DecisionTreeClassifier(criterion="entropy", max_depth=3, max_features=2)
# train_classifier(tree32, "max depth = 3, max features = 2")

# tree62 = DecisionTreeClassifier(criterion="entropy", max_depth=6, max_features=2)
# train_classifier(tree62, "max depth = 6, max features = 2")

# tree310 = DecisionTreeClassifier(criterion="entropy", max_depth=3, max_features=10)
# train_classifier(tree310, "max depth = 3, max features = 10")
# export_graphviz(tree310, out_file='tree.dot', feature_names = feature_names)

# tree86 = DecisionTreeClassifier(criterion="entropy", max_depth=8, max_features=6)
# train_classifier(tree86, "max depth = 8, max features = 6")

# TODO: Evaluate another classifier, i.e. SVM, Logistic Regression, k-NN, etc.
knn = neighbors.KNeighborsClassifier(n_neighbors=4, weights='uniform')  # uniform or distance
train_classifier(knn, "k-NN")
# export_graphviz(knn, out_file='tree.dot', feature_names = feature_names)

# TODO: Once you have collected data, train your best model on the entire
# dataset. Then save it to disk as follows:
best = knn
best.fit(X,y)

# when ready, set this to the best model you found, trained on all the data:
best_classifier = best
with open('classifier.pickle', 'wb') as f: # 'wb' stands for 'write bytes'
    pickle.dump(best_classifier, f)
