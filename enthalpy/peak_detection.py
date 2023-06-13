import numpy as np

from scipy.interpolate import UnivariateSpline
from scipy.signal import argrelextrema


def get_spline(X, y):
    """
    Given a typical reaction, this returns a smoothed approximation of the reaction.
    """
    output = np.zeros(X.shape)
    for deg in xrange(1, 5):
        s = UnivariateSpline(X, y, deg)
        output += s(X)
    return output

def find_onset_point(X, y):
    """
    ================
    INPUT: array of X data (temperature), array of Y data (heat flow)
    OUTPUT: int
    ================

    In order, this function:

    1. Smooths the data and approximates it with a spline.

    2. Finds the second derivative.

    3. Finds where the second derivative of the approximation is minimized,
    which in this data coincides with just before the reaction begins.
    That point is the starting point for the reaction.

    """
    second_derivative = UnivariateSpline(X, y, k = 5).derivative(2)(X)

    local_minima = argrelextrema(second_derivative, np.less)[0]
    relevant_minima_points = local_minima[local_minima > 100] # crop off the first tail

    return relevant_minima_points[0]

def find_ending_point(X, y, start_point, use_alternative = False):
    """
    ================
    INPUT: array of X data (temperature), array of Y data (heat flow), int
    OUTPUT: int
    ================

    Finds the end point of the reaction to estimate enthalpy.

    - NOTE: use_alternative: this variable decides which "end point finder" you
    want to use. if you want to take the post-peak max point, select True. If
    you want to use the end-point derived from the second derivative, select
    False.

    In order, this function:

    1. Isolates data after the peak

    2. Approximates the data with a spline.

    3. Finds the point where the first derivative is closest to zero and nearest
    to the end of the reaction. This is the end point.
        ## note, you could also set the end point to be when the function
        ## has returned closest to the gradient at the start_point

    4. If this point is < post-peak max point, choose the maximum point.

    """
    start_point = 1405
    reaction_x = X[start_point:] # x's after the start_point
    reaction_y = y[start_point:] # y's after the start_point
    index_of_peak = start_point + reaction_y.argmin()


    if use_alternative:
        end_point_id = index_of_peak + y[index_of_peak : ].argmax()
    else:
        pp_X, pp_y = X[index_of_peak: ], y[index_of_peak: ]
        spline = UnivariateSpline(pp_X, pp_y, k = 5)
        second_derivative = spline.derivative(2)(pp_X)
        relevant_end_points = np.abs(second_derivative)
        end_point = np.max(relevant_end_points.argsort()[:50]) # get the largest of all the zero points
        end_point_id = index_of_peak + end_point

        # just in case there are larger points between peak & end point
        if np.max(y[index_of_peak : end_point_id]) > y[end_point_id]:
            index = y[index_of_peak : end_point_id].argmax()
            end_point_id = index_of_peak + index

    return end_point_id

def get_points(X, y):
    onset_point = find_onset_point(X, y)
    end_point = find_ending_point(X, y, onset_point)
    return onset_point, end_point

def get_points_coordinates(X, y):
    onset_point, end_point = get_points(X, y)
    (x_0, y_0) = (X[onset_point], y[onset_point])
    (x_1, y_1) = (X[end_point], y[end_point])
    return (x_0, y_0), (x_1, y_1)

def get_peak_X_y(X, y):
    onset_point, end_point = get_points(X, y)
    peak_X = X[onset_point : end_point]
    peak_y = y[onset_point : end_point]
    return peak_X, peak_y
