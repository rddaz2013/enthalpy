import numpy as np

from scipy.signal import savgol_filter

from bokeh.plotting import figure, output_file, show
from bokeh.io import show, output_notebook
from bokeh.models import LinearAxis, Range1d

import integration

def smooth_array(arr):
    smoothing = len(arr) // 3 * 2 + 1
    return savgol_filter(arr, smoothing, 5)

def dydx(x_array, y_array):
    dx = np.gradient(x_array)
    return np.gradient(y_array, dx)

def get_second_derivative(x_array, y_array):
    d1 = dydx(x_array, y_array)
    return dydx(x_array, d1)

def alt_dydx(x_array, y_array, h):
    """
    INPUT: ndarray, ndarray, int
    OUTPUT: ndarray

    Takes the derivative of y w.r.t. x over the number of observations around x you evaluate it over.
    """
    derivatives = np.zeros(len(x_array))

    for i in xrange(h, len(x_array)):
        x_subset = x_array[i - h : i ]
        y_subset = y_array[i - h : i ]

        dy = y_subset[-1] - y_subset[0]
        dx = x_subset[-1] - x_subset[0]

        derivatives[i] = float(dy) / float(dx)

    return derivatives

def alt_get_second_derivative(x_array, y_array, h):
    deriv_1 = dydx(x_array, smooth_array(y_array), h)
    return dydx(x_array, smooth_array(deriv_1), h)

def find_last_true_point(arr):
    """
    given array of TRUE / FALSE values, find the point in the array
    for which all elements after it are true
    """
    opposite = -arr
    return np.max(opposite.nonzero()[0]) + 1

def split_data(temp, heat_flow, return_as_list = True):
    split_point = np.argmin(heat_flow)

    before_temp = temp[:split_point]
    after_temp = temp[split_point:]

    before_heat_flow = heat_flow[:split_point]
    after_heat_flow = heat_flow[split_point:]
    if return_as_list:
        return before_temp, before_heat_flow, after_temp, after_heat_flow
    else:
        return {
            'before': {'temp': before_temp, 'heat flow': before_heat_flow},
            'after': {'temp': after_temp, 'heat flow': after_heat_flow},
        }


def find_candidate_points(x_array, y_array, min_points, epsilon, start_temp):
    sample_x = x_array[x_array > start_temp]
    sample_y = y_array[x_array > start_temp]
    d2 = -savgol_filter(smooth_array(get_second_derivative(sample_x, sample_y)),
                        199,
                        3
                      )
    candidates = []

    index = np.min(np.where(x_array > start_temp)) # find first true value after start_temp

    while index < len(d2) - min_points:
        subset = d2[index : index + min_points]
        if all(subset < epsilon):
            candidates.append(index)
        index += 1
    return candidates
    ## this runs fast, but it would run faster if you implement the "find_last_true_point"
    ## method when you find a candidate. Imp'd in alt_find_candidate_points

def alt_find_candidate_points(x_array, y_array, min_points, epsilon, start_temp):
    sample_x = x_array[x_array > start_temp]
    sample_y = y_array[x_array > start_temp]
    d2 = smooth_array(get_second_derivative(x_array, y_array))
    candidates = []
    i = 0
    while i < len(d2) - min_points:
        subset = d2[i : i + min_points]
        if all(subset < epsilon):
            candidates.append(d2[i])
            i += 1
        else:
            i += find_last_true_point(subset)
    return candidates

def find_onset_point(x_array, y_array, min_points, epsilon, start_temp):
    """
    Find the point at the beginning of curve changes
    """
    return find_candidate_points(x_array, y_array, min_points, epsilon, start_temp)[0]

def find_end_point(x_array, y_array, min_points, epsilon, start_temp):
    return -(find_candidate_points(x_array[::-1], y_array, min_points, epsilon, start_temp)[0] + 1)

def construct_line(x0, y0, x1, y1, x_array):
    slope = float(y1 - y0) / (x1 - x0)
    intercept = y1 - slope * x1
    line_func = lambda x: slope * x + intercept
    return x_array, map(line_func, x_array)

def fit_line(x_array, y_array, min_points, epsilon, start_temp, plot = False, second = False):
    """
    Returns arrays of the x and y coordinates of the line connecting the
    onset and end points of the reaction.
    """
    # first_t, first_hf, second_t, second_hf = split_data(x_array, y_array)

    onset_point = find_onset_point(x_array, y_array, min_points, epsilon, start_temp)
    end_point = find_end_point(x_array, y_array, min_points, epsilon, start_temp)

    t0, hf0 = x_array[onset_point], y_array[onset_point]
    t1, hf1 = x_array[end_point], y_array[end_point]

    points_inbetween = x_array[onset_point:end_point]

    X, y = construct_line(t0, hf0, t1, hf1, points_inbetween)

    if plot:
        p = figure(title="Results", x_axis_label='x', y_axis_label='y')
        p.line(x_array, y_array, legend="Heat Flow", line_width=2)
        p.line(X, y, legend="fit line", line_width =2, color = 'green')
        mask = find_candidate_points(x_array, y_array, min_points, epsilon, start_temp)

        sample_x = x_array[x_array > start_temp]
        sample_y = y_array[x_array > start_temp]

        if second:
            d2 = savgol_filter(smooth_array(get_second_derivative(sample_x, sample_y)),
                               333,
                               3
                               )
            p.extra_y_ranges = {"d2": Range1d(start=np.min(d2), end=np.max(d2))}
            p.add_layout(LinearAxis(y_range_name="d2"), 'right')
            p.line(x_array,
                   d2,
                   y_range_name = 'd2',
                   legend = 'second derivative',
                   color = 'purple'
                   )

        p.scatter(x_array[mask], y_array[mask], color='red')
        show(p)
    return X, y
