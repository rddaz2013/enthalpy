import numpy as np

import peak_detection as pdetect
import file_helpers as fh

from scipy.integrate import simps
from bokeh.plotting import figure, output_file, show
from bokeh.io import show, output_notebook
from bokeh.models import LinearAxis, Range1d


def construct_line(x_0, y_0, x_1, y_1, x_array):
    """
    ================
    INPUT: numeric, numeric, numeric, numeric, array
    OUTPUT: array, array
    ================

    Used to create the best fit line once you've found the start and end
    points of the reaction.

    Takes in the x and y coordinates of two endpoints you want to draw a
    line between and returns two arrays of x and y coordinates of the line
    between them.

    - x_N, y_N: the x and y values of point N
    - x_array: the x values you want to map into y values (can be any x values)

    """

    slope = float(y_1 - y_0) / (x_1 - x_0)

    intercept = y_1 - slope * x_1

    def create_a_line(m, x, b):
        return m * x + b

    line_y = create_a_line(slope, x_array, intercept)

    return x_array, line_y

def fit_line(X, y):
    """
    ================
    INPUT: array of X data (temperature), array of Y data (heat flow)
    OUTPUT: array of X data (temperature), array of Y data (best-fit-line heat
    flow)
    ================

    Returns two arrays, of the x's and y's of the best-fit-line.

    """
    peak_X, peak_y = pdetect.get_peak_X_y(X, y)
    onset_point, end_point = pdetect.get_points(X, y)
    (x_0, y_0), (x_1, y_1) = pdetect.get_points_coordinates(X, y)

    line_X, line_y = construct_line(x_0,
                                    y_0,
                                    x_1,
                                    y_1,
                                    peak_X
                                   )
    return line_X, line_y



def get_enthalpy(X, y):
    """
    ================
    INPUT: array of X data (temperature), array of Y data (heat flow)
    OUTPUT: float
    ================

    Returns the enthalpy of the reaction.

    In order, this function:
    1. Gets the interval of the peak
    2. Fits a line between its end points
    3. Takes the difference between the line and the peak
    4. Finds the integral of the difference

    """
    peak_X, peak_y = pdetect.get_peak_X_y(X, y)
    onset_point, end_point = pdetect.get_points(X, y)

    line_X, line_y = fit_line(X, y)
    differences = line_y - peak_y

    return simps(differences, x = peak_X)


def get_statistics(X, y):
    """
    ================
    INPUT: array of X data (temperature), array of Y data (heat flow), int
    OUTPUT: float, float, float, float, tuple
    ================

    Returns four key release characteristics:
    1. Enthalpy
    2. Peak heat flow
    3. Temperature at peak
    4. Rough standard deviation of peak
    5. Onset and end points

    """

    peak_X, peak_y = pdetect.get_peak_X_y(X, y)

    enthalpy = get_enthalpy(X, y)

    peak_heat_flow = np.min(peak_y) # find the minimum y

    peak_temp = peak_X[np.argmin(peak_y)] # find the x for which y is minimized

    heat_flow_std = np.std(peak_y)

    onset, end = pdetect.get_points_coordinates(X, y)

    return enthalpy, peak_heat_flow, peak_temp, heat_flow_std, (onset, end)
