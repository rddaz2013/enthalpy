import sys

import numpy as np
import matplotlib.pyplot as plt

import peak_detection as pdetect
import peak_statistics as pstats
import file_helpers as fh

def process_data(filepath, plot = False):
    """
    ================
    INPUT: string (filepath), boolean
    OUTPUT: several statistics, and a plot if "plot" parameter is True
    ================

    Returns enthalpy about the data, and plots it, the endpoints and the
    line if you want (as well as statistics)

    """

    # clean the data
    data = fh.clean_file(filepath)

    #find the first number in the filename and use as the title
    name_of_preparation = fh.get_file_title(filepath)

    # ensure that the data is formatted correctly, as arrays
    temp, heat_flow = np.array(data.temp), np.array(data.heat_flow)

    # generate statistics
    e, hf, t, sd, (onset_point, end_point) = pstats.get_statistics(temp, heat_flow)

    statistics_text = """=== Preparation {0} ===
    Enthalpy: {1}
    Peak Heat Flow: {2}
    Peak Temperature: {3}
    Heat Flow Standard Devation: {4}
    Onset point: {5}, {6}
    End point: {7}, {8}
    """.format(name_of_preparation,
               round(e, 3),
               round(hf, 3),
               round(t, 2),
               round(sd, 4),
               round(onset_point[0], 2),
               round(onset_point[1], 3),
               round(end_point[0], 2),
               round(end_point[1], 3)
               )

    if plot:
        # get line for plotting
        line_X, line_y = pstats.fit_line(temp, heat_flow)

        # get onset and end points
        (x0, y0), (x1, y1) = pdetect.get_points_coordinates(temp, heat_flow)

        # set up plot
        fig, ax = plt.subplots(1)
        ax.set_title("Preparation {}".format(name_of_preparation))
        ax.set_xlabel("Temperature")
        ax.set_ylabel("Heat Flow")
        ax.annotate(statistics_text,
                    xy=(0.5, 0.4),
                    xycoords='axes fraction'
                    )

        # plot original data
        plt.plot(temp,
               heat_flow,
               color = 'black',
               label = "Original data"
              )

        # plot best fit line
        plt.plot(line_X,
               line_y,
               color = 'red',
               label = "Best fit line"
              )

        # plot onset point
        plt.scatter(x0,
                  y0,
                  color = 'green',
                  label = 'Onset: {}, {}'.format(round(x0,2), round(y0, 2))
                 )

        # plot end point
        plt.scatter(x1,
                  y1,
                  color = 'purple',
                  label = 'End: {}, {}'.format(round(x1, 2), round(y1, 2))
                 )
        plt.legend()
        plt.show()

    return e # this is short for enthalpy, as defined above

if __name__ == '__main__':
    filename = sys.argv[-1]
    process_data(filepath, plot = True)
