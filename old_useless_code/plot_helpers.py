from integration import *

def plot_file(filepath):
    """
    Plots temp vs heat_flow for a given preparation raw file.
    """
#     sb.set_style('ticks')
    f = clean_file(filepath)
    sb.plt.plot(f.temp, f.heat_flow, color = 'r', alpha = 0.8)

def plot_chart(data):
    """
    Plots temp vs heat_flow for a given preparation for a cleaned file.
    """

    sb.plt.plot(data.temp, data.heat_flow)
    sb.plt.show()

def plot_all_files(filenames, nrows, save = False):
    """
    Plots all files in filenames in a subplot, which may or may not include every
    plot because the last subplot row may not be full.
    """

    fig, axes = sb.plt.subplots(nrows, 3, figsize=(12,40))
    i = 0
    for row in axes:
        for r in xrange(3):
            if i + r < len(filenames):
                f = clean_file(filenames[i])
                x, y = f.temp, f.heat_flow
                row[r].plot(x, y)
                title = re.findall('(.*?).txt', filenames[i + r])[0]
                row[r].set_title(title)
        i += 3
    if save:
        sb.plt.savefig('all_plots.png')
    sb.plt.show()

def plot_difference(temp, heat_flow):
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

    differences = -(g_heat_subset.T[0] - y_predicted) # negative assuming endothermic

    sns.plt.plot(differences)
    return differences

def plot_energy(temp, heat_flow, crop):
    """
    INPUT: array, array
    OUTPUT: none; plotted chart

    Plots heatflow signature as well as best-fit-line and displays
    preparation statistics.
    """
    g_temp_subset, g_heat_subset = get_gelation_subset(temp, heat_flow)
    X, y = get_line_and_model(temp, heat_flow)
    # plot energies
    fig, ax = sns.plt.subplots(1, figsize = (9,9))
    if crop:
        ax.plot(g_temp_subset, g_heat_subset)
    else:
        ax.plot(temp, heat_flow)
    ax.plot(X, y)
    # sns.plt.fill_between(g_temp_subset.T[0], g_heat_subset.T[0], y, color='r', alpha='0.4')

    energy, flow, temp, sd = enthalpy_statistics(temp, heat_flow)
    text = """enthalpy = {0}\npeak flow =  {1}\npeak temp = {2}\nsd = {3}"
    """.format(energy, flow, temp, sd)

    ax.text(0.9, 0.1, text)
    fig.show()
