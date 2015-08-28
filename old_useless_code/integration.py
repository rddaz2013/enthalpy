import pandas as pd
import numpy as np
import seaborn as sns

from sklearn.linear_model import LinearRegression
from scipy.integrate import simps

import plot_helpers
import file_helpers

def get_line_subset(temp, heat_flow):
    """
    INPUT: array, array
    OUTPUT: array, array

    Removes gelation action data, as well as the beginning "ramp", so that the
    output only reflects the linear data to model a best-fit-line to.
    """
    mask = (temp > 50) & ((temp < 60) | (temp > 92)) ## NOTE: Arbitrary cutoff
    temp_subset = temp[mask]
    heat_subset = heat_flow[mask]
    temp_subset = temp_subset.reshape((len(temp_subset), 1))
    heat_subset = heat_subset.reshape((len(heat_subset), 1))
    # temp_subset = temp_subset.reshape((1, len(temp_subset)))
    # heat_subset = heat_subset.reshape((1, len(heat_subset)))
    return temp_subset, heat_subset

def get_gelation_subset(temp, heat_flow):
    """
    INPUT: array, array
    OUTPUT: array, array

    Removes beginning and end intervals so that the output only reflects the
    gelation action.
    """

    mask = (temp > 60) & (temp < 92) ## NOTE: Arbitrary cutoff
    temp_subset = temp[mask]
    heat_subset = heat_flow[mask]
    temp_subset = temp_subset.reshape((len(temp_subset), 1))
    heat_subset = heat_subset.reshape((len(heat_subset), 1))
    # temp_subset = temp_subset.reshape((1, len(temp_subset)))
    # heat_subset = heat_subset.reshape((1, len(heat_subset)))
    return temp_subset, heat_subset

def get_line(intercept, slope, min_x, max_x, size):
    """
    INPUT: numeric, numeric, numeric, int
    OUTPUT: array, array

    Get X and y values of some arbitrary line
    """
    X = np.linspace(min_x, max_x, size)
    y = intercept + slope * X
    return X, y

def get_line_from_model(model, min_x, max_x, size):
    """
    INPUT: sklearn linear model, numeric, numeric, int
    OUTPUT: array, array

    Get X and y values of some arbitrary line from an sklearn model
    """
    X = np.linspace(min_x, max_x, size)
    slope = model.coef_[0][0]
    intercept = model.intercept_[0]
    y = intercept + slope * X

    return X, y

def get_line_and_model(temp, heat_flow):
    l_temp_subset, l_heat_subset = get_line_subset(temp, heat_flow)

    # fit a line
    lm = LinearRegression()
    lm.fit(l_temp_subset, l_heat_subset)
    X_actual, y_predicted = get_line_from_model(lm,
                                                min(l_temp_subset),
                                                max(l_temp_subset),
                                                len(l_temp_subset))
    return X_actual, y_predicted

def get_enthalpy(temp, heat_flow):
    """
    INPUT: array, array
    OUTPUT: float

    For a given heat flow signature over a range of temperatures, return
    the total amount of energy released.
    """
    # get appropriate line-fitting subset of data
    l_temp_subset, l_heat_subset = get_line_subset(temp, heat_flow)
    g_temp_subset, g_heat_subset = get_gelation_subset(temp, heat_flow)

    # fit a line during gelation period
    lm = LinearRegression()
    lm.fit(l_temp_subset, l_heat_subset)
    X_actual, y_predicted = get_line_from_model(lm,
                                                min(g_temp_subset),
                                                max(g_temp_subset),
                                                len(g_heat_subset))

    # generate line, actual differences
    differences = -(g_heat_subset.T[0] - y_predicted) # negative assuming endothermic
    return simps(differences, x = g_temp_subset.T[0])

def enthalpy_statistics(temp, heat_flow):
    """
    INPUT: array, array
    OUTPUT: (float, float, float, float)

    Returns four key release characteristics & features
    """
    g_temp_subset, g_heat_subset = get_gelation_subset(temp, heat_flow)

    enthalpy = get_enthalpy(temp, heat_flow)

    peak_heat_flow = np.min(g_heat_subset)

    peak_temp = g_temp_subset[np.argmin(g_heat_subset)][0]

    heat_flow_std = np.std(g_heat_subset)

    return enthalpy, peak_heat_flow, peak_temp, heat_flow_std

def get_energy_file(filepath, plot = False, crop = False):
    """
    INPUT: filepath
    OUTPUT: float
    """
    data = file_helpers.clean_file(filepath)
    temp, heat_flow = data.temp, data.heat_flow
    if plot:
        plot_helpers.plot_energy(temp, heat_flow, crop)
        sns.plt.show()
    return get_enthalpy(temp, heat_flow)

def get_energy_all_files(filenames, plot = False, crop = False):
    """
    INPUT: list of filepaths
    OUTPUT: 2D array with C1 = filename, C2 = energy release
    """
    releases = []
    for f in filenames:
        releases.append(get_energy_file(f, plot, crop))
    return np.array(releases)
