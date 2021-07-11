"""
This module allows for baseline subtraction using polynomial subtraction at a user-specified
degree, peak detection using scipy.signal find_peaks module, and then utilizes
Lorentzian fitting of spectra data, enabling extraction of full-width, half-max peak data.
Note that Lorentzian fitting was chosen explicitly as it is the proper descriptor of peak
shapes from Raman spectra.
Developed by the Raman-Noodles team.
"""


import matplotlib.pyplot as plt
import numpy as np
from peakutils.baseline import baseline

def subtract_baseline(y_data, deg=3, plot=False, x_data=None):
    """
    Function that fits an n-degree polynomial (default: n = 3) baseline
    to the spectral data, and subtracts it from the input data.
    Args:
        y_data (list like): The intensity data of the spectra to be baselined.
        deg (integer): (Optional) Integer value for the degree of the polynomial
                       to be used to baseline data. The value defaults to 3 if
                       no value is specified.
        plot (boolean): (Optional) Boolean value that indicates whether or not to
                        plot the baselined and original data. If true, it plots
                        both spectra on the same plot. Note that if the user wants
                        plotting functionality, x_data must be provided.
        x_data (list like): (Optional) The x-values associated with the y_data that
                            is being baselined. These values are only needed for
                            the function if the user desires plotting.
    Returns:
        y_out (list like): The baselined values of the y-axis.
    """
    # handling errors in inputs
    if not isinstance(y_data, (list, np.ndarray)):
        raise TypeError('Passed value of `y_data` is not a list or numpy.ndarray! Instead, it is: '
                        + str(type(y_data)))
    y_base = baseline(y_data, deg=deg, max_it=200)
    # to avoid strange results,
    # change all negative values to zero
    yb_plus = [0 if i < 0 else i for i in y_base]
    y_out = y_data - yb_plus
    # plot that lets you see the baseline fitting
    if plot and x_data is None:
        raise ValueError('Please add x_data as input to plot')
    elif plot:
        plt.figure(figsize=(10, 4))
        plt.plot(x_data, y_data, 'b--', label='input')
        plt.plot(x_data, y_out, 'b', label='output')
        plt.plot(x_data, yb_plus, 'r', label='baseline')
        plt.plot(x_data, y_base, 'r--', label='negative baseline')
        plt.axhline(y=0, color='orange', alpha=0.5, label='zero')
        plt.legend()
    else:
        pass
    return y_out

