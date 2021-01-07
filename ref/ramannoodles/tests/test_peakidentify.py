"""
Module used to unit test the functionality and outputs of the peakidentify.py module
"""
# IMPORTING MODULES
import pickle
import numpy as np
from ramannoodles import peakidentify
from ramannoodles import shoyu
from ramannoodles import spectrafit


def test_peak_assignment():
    """This function tests the operation of the peak_assignment function in peakidentify.py"""
    # First, generate a testing dataset.
    shoyu_data_dict = pickle.load(
        open('raman_spectra/shoyu_data_dict.p', 'rb'))
    compound_1 = shoyu_data_dict['WATER']
    compound_2 = shoyu_data_dict['CARBON MONOXIDE']
    compound_3 = shoyu_data_dict['CARBON DIOXIDE']
    unknown_x, unknown_y = shoyu.combine_spectra(
        compound_1, compound_2, plot=False)
    unknown_x = np.asarray(unknown_x)
    unknown_y = np.asarray(unknown_y)
    known_compound_list = [compound_1, compound_2, compound_3]
    precision = 0.03

    # Various try statements to make sure that bad inputs are handled correctly.
    try:
        peakidentify.peak_assignment(
            1, unknown_y, known_compound_list, precision, False)
    except TypeError:
        print("An invalid unknown_x was passed to the function, and it was"
              " handled well with a TypeError.")

    try:
        peakidentify.peak_assignment(
            unknown_x, 2, known_compound_list, precision, False)
    except TypeError:
        print("An invalid unknown_y was passed to the function, and it was "
              "handled well with a TypeError.")

    try:
        peakidentify.peak_assignment(
            unknown_x, unknown_y, 'string', precision, False)
    except TypeError:
        print("An invalid known_compound_list was passed to the function, "
              "and it was handled well with a TypeError.")

    try:
        peakidentify.peak_assignment(unknown_x, unknown_y, [
                                     1, 3, 6], precision, False)
    except TypeError:
        print("An invalid element inside known_compound_list was passed to "
              "the function, and it was handled well with a TypeError.")

    try:
        peakidentify.peak_assignment(
            unknown_x, unknown_y, known_compound_list, 'precision', False)
    except TypeError:
        print("An invalid precision value was passed to the function, and "
              "it was handled well with a TypeError.")

    try:
        peakidentify.peak_assignment(
            1, unknown_y, known_compound_list, precision, 'False')
    except TypeError:
        print("An invalid plot value was passed to the function, and it "
              "was handled well with a TypeError.")


def test_compare_unknown_to_known():
    """This function tests the operation of the compare_unknown_to_known
    function in peakidentify.py"""
    # Build our test dataset.
    shoyu_data_dict = pickle.load(
        open('raman_spectra/shoyu_data_dict.p', 'rb'))
    compound_1 = shoyu_data_dict['WATER']
    compound_2 = shoyu_data_dict['CARBON MONOXIDE']
    compound_3 = shoyu_data_dict['CARBON DIOXIDE']
    unknown_x, unknown_y = shoyu.combine_spectra(
        compound_1, compound_2, plot=False)
    unknown_x = np.asarray(unknown_x)
    unknown_y = np.asarray(unknown_y)
    known_compound_list = [compound_1, compound_2, compound_3]
    precision = 0.03
    known_peaks = []
    for i, _ in enumerate(known_compound_list):
        known_peaks.append(spectrafit.compound_report(
            known_compound_list[i])[0])
    unknown_peaks = spectrafit.data_report(unknown_x, unknown_y)[0]

    try:
        peakidentify.compare_unknown_to_known(1, known_peaks[0], precision)
    except TypeError:
        print("An invalid unknown_peaks value was passed to the function, "
              "and was handled correctly.")

    try:
        peakidentify.compare_unknown_to_known(
            unknown_peaks, 'known_peaks', precision)
    except TypeError:
        print("An invalid known_peaks value was passed to the function, "
              "and was handled correctly.")

    try:
        peakidentify.compare_unknown_to_known(
            unknown_peaks, known_peaks[0], 'precision')
    except TypeError:
        print("An invalid precision value was passed to the function, and "
              "was handled correctly.")

    # After testing for resilience to unexpected inputs, now ensure outputs are performing correctly

    # First, make sure function is returning the list.
    assert isinstance(peakidentify.compare_unknown_to_known(
        unknown_peaks, known_peaks[0], precision), np.ndarray), (""
                                                                 "Function is not returning list")

    # Compare one set of peaks to itself. The full association matrix should have all values = 1.
    self_comp = np.mean(peakidentify.compare_unknown_to_known(known_peaks[0],
                                                              known_peaks[0], precision))
    assert self_comp == 1, ("Peak Assignment Error. Comparison of compound "
                            "against itself should find all peaks.")

    dif_comp = np.mean(peakidentify.compare_unknown_to_known([1, 3, 6],
                                                             [1000, 2000, 5000], precision))
    assert dif_comp == 0, ("Peak Assignment Error. Passed values should "
                           "have no matching assignments.")


def test_peak_position_comparisons():
    """This function tests the operation of the peak_position_comparisons
    function in peakidentify. Said function returns a list of strings that
    contain text assignments of each peak in the unknown spectrum."""

    # First, generate good data.
    shoyu_data_dict = pickle.load(
        open('raman_spectra/shoyu_data_dict.p', 'rb'))
    compound_1 = shoyu_data_dict['WATER']
    compound_2 = shoyu_data_dict['CARBON MONOXIDE']
    compound_3 = shoyu_data_dict['CARBON DIOXIDE']
    unknown_x, unknown_y = shoyu.combine_spectra(
        compound_1, compound_2, plot=False)
    unknown_x = np.asarray(unknown_x)
    unknown_y = np.asarray(unknown_y)
    known_compound_list = [compound_1, compound_2, compound_3]
    unknown_peaks = spectrafit.data_report(unknown_x, unknown_y)[0]
    known_peaks = []
    association_matrix = []
    for i, _ in enumerate(known_compound_list):
        known_peaks.append(spectrafit.compound_report(
            known_compound_list[i])[0])
        association_matrix.append(peakidentify.compare_unknown_to_known(
            unknown_peaks, known_peaks[i], 0.03))

    # Then, test error handling of bad inputs for the function.
    try:
        peakidentify.peak_position_comparisons(1, known_peaks,
                                               known_compound_list,
                                               association_matrix)
    except TypeError:
        print("An invalid unknown_peaks value was passed to the function, "
              "and was handled correctly.")

    try:
        peakidentify.peak_position_comparisons(unknown_peaks,
                                               'known_peaks',
                                               known_compound_list,
                                               association_matrix)
    except TypeError:
        print("An invalid known_peaks value was passed to the function, "
              "and was handled correctly.")

    try:
        peakidentify.peak_position_comparisons(unknown_peaks,
                                               known_peaks,
                                               'known_compound_list',
                                               association_matrix)
    except TypeError:
        print("An invalid known_compound_list value was passed to the function,"
              "and was handled correctly.")

    try:
        peakidentify.peak_position_comparisons(unknown_peaks,
                                               known_peaks,
                                               known_compound_list,
                                               'association_matrix')
    except TypeError:
        print("An invalid association_matrix value was passed to the function,"
              "and was handled correctly.")

    # Check to make sure the function is returning a list.
    assert isinstance(peakidentify.peak_position_comparisons(
        unknown_peaks, known_peaks, known_compound_list,
        association_matrix), list), "The function is not returning a list."

    # Test a call that says that no peaks have associations
    association_matrix_0 = []
    association_matrix_0.append(peakidentify.compare_unknown_to_known(known_peaks[0],
                                                                      known_peaks[1],
                                                                      0.03))
    zero_output = peakidentify.peak_position_comparisons(known_peaks[0],
                                                         [known_peaks[1]],
                                                         [compound_1],
                                                         association_matrix_0)[0]
    assert zero_output[0] == 'Unassigned', """The function is not properly
    handling unassigned peaks."""

    # Test the function to make sure that it has the right functionality
    association_matrix = []
    # Generate a matrix with all associations equal to 1
    association_matrix.append(peakidentify.compare_unknown_to_known(known_peaks[0],
                                                                    known_peaks[0],
                                                                    0.03))
    # change the middle index to 0
    association_matrix[0][1] = 0
    test_peak_labels = peakidentify.peak_position_comparisons(known_peaks[0],
                                                              [known_peaks[0]],
                                                              [compound_1],
                                                              association_matrix)
    assert test_peak_labels[0][0] == 'WATER', """The function is
    not correctly assigning peaks when association matrix = 1"""
    assert test_peak_labels[1][0] == 'Unassigned', """The function is
    not correctly handling a lack of peak assignments"""
    assert test_peak_labels[2][0] == 'WATER', """The funciton is
    not correctly assigning peaks when association matrix = 1"""


def test_percentage_of_peaks_found():
    """This function tests the operation of the
    percentage_of_peaks_found function in peakidentify.py"""
    # First, generate good data.
    shoyu_data_dict = pickle.load(
        open('raman_spectra/shoyu_data_dict.p', 'rb'))
    compound_1 = shoyu_data_dict['WATER']
    compound_2 = shoyu_data_dict['CARBON MONOXIDE']
    compound_3 = shoyu_data_dict['CARBON DIOXIDE']
    unknown_x, unknown_y = shoyu.combine_spectra(
        compound_1, compound_2, plot=False)
    unknown_x = np.asarray(unknown_x)
    unknown_y = np.asarray(unknown_y)
    known_compound_list = [compound_1, compound_2, compound_3]
    unknown_peaks = spectrafit.data_report(unknown_x, unknown_y)[0]
    known_peaks = []
    association_matrix = []
    for i, _ in enumerate(known_compound_list):
        known_peaks.append(spectrafit.compound_report(
            known_compound_list[i])[0])
        association_matrix.append(peakidentify.compare_unknown_to_known(unknown_peaks,
                                                                        known_peaks[i],
                                                                        0.03))

    # Test for input error handling.
    try:
        peakidentify.percentage_of_peaks_found(
            1, association_matrix, known_compound_list)
    except TypeError:
        print("""The function correctly handled the error when an int
        was input instead of the known_peaks list""")

    try:
        peakidentify.percentage_of_peaks_found(
            known_peaks, 1, known_compound_list)
    except TypeError:
        print("""The function correctly handled the error when an int
        was input instead of the association matrix""")

    try:
        peakidentify.percentage_of_peaks_found(known_peaks,
                                               association_matrix,
                                               'known_compound_list')
    except TypeError:
        print("""The function correctly handled the error when a string
        was input instead of the known_compound_list""")

    try:
        peakidentify.percentage_of_peaks_found(known_peaks,
                                               association_matrix,
                                               [compound_1,
                                                compound_2,
                                                'compound_3'])
    except TypeError:
        print("""The function correctly handled the case where the compound
        list contains something that is not a compound""")

    # Test to make sure function returns a dictionary.
    assert isinstance(peakidentify.percentage_of_peaks_found(
        known_peaks,
        association_matrix,
        known_compound_list), dict), """The function is not
        returning a dictionary."""

    # Test for function output.
    water_peaks = spectrafit.compound_report(compound_1)[0]
    water_dict_0 = peakidentify.percentage_of_peaks_found([water_peaks],
                                                          [[0, 0, 0]],
                                                          [compound_1])
    assert water_dict_0['WATER'] == 0, """The function is not correctly
    calculating percentages when no peaks are found"""

    water_dict_1 = peakidentify.percentage_of_peaks_found([water_peaks],
                                                          [[1, 1, 1]],
                                                          [compound_1])
    assert water_dict_1['WATER'] == 100, """The function is not correctly
    calculating percentages when all peaks are found"""


def test_plotting_peak_assignments():
    """This function tests the operation of the peak_assignment
    function in peakidentify.py"""
    # First, generate good data.
    shoyu_data_dict = pickle.load(
        open('raman_spectra/shoyu_data_dict.p', 'rb'))
    compound_1 = shoyu_data_dict['WATER']
    compound_2 = shoyu_data_dict['CARBON MONOXIDE']
    compound_3 = shoyu_data_dict['CARBON DIOXIDE']
    unknown_x, unknown_y = shoyu.combine_spectra(
        compound_1, compound_2, plot=False)
    unknown_x = np.asarray(unknown_x)
    unknown_y = np.asarray(unknown_y)
    known_compound_list = [compound_1, compound_2, compound_3]
    precision = 0.03
    unknown_peaks = spectrafit.data_report(unknown_x, unknown_y)[0]
    known_peaks = []
    association_matrix = []
    for i, _ in enumerate(known_compound_list):
        known_peaks.append(spectrafit.compound_report(
            known_compound_list[i])[0])
        association_matrix.append(peakidentify.compare_unknown_to_known(
            unknown_peaks, known_peaks[i], precision))
    unknown_peak_assignments = peakidentify.peak_position_comparisons(
        unknown_peaks,
        known_peaks,
        known_compound_list,
        association_matrix)

    # Test for input error handling.
    try:
        peakidentify.plotting_peak_assignments(1,
                                               unknown_y,
                                               unknown_peaks,
                                               unknown_peak_assignments)
    except TypeError:
        print("""The function correctly handled the error
        when an int was input instead of the unknown_x list""")

    try:
        peakidentify.plotting_peak_assignments(unknown_x,
                                               3,
                                               unknown_peaks,
                                               unknown_peak_assignments)
    except TypeError:
        print("""The function correctly handled the error when an int
        was input instead of the unknown_y list""")

    try:
        peakidentify.plotting_peak_assignments(unknown_x,
                                               unknown_y,
                                               'unknown_peaks',
                                               unknown_peak_assignments)
    except TypeError:
        print("""The function correctly handled the error when a string
        was input instead of the unknown_peaks list""")

    try:
        peakidentify.plotting_peak_assignments(unknown_x,
                                               unknown_y,
                                               unknown_peaks,
                                               3)
    except TypeError:
        print("""The function correctly handled the error when an int
        was input instead of the unknown_peak_assignments""")

    try:
        peakidentify.plotting_peak_assignments(unknown_x,
                                               unknown_y,
                                               unknown_peaks,
                                               ['WATER', 23, 'CO'])
    except TypeError:
        print("""The function correctly handled the case when an int
        was passed in the unknown_peak_assignment list""")


def test_peak_1d_score():
    """Evaluates the functionality of the peak_1D_score function"""
    # Initialize the test arguments
    row_i = [0, 1]
    row_j = [2, 1]
    rowcat = row_i + row_j
    arraya = np.array([[0, 1], [2, 1], [0, 3]])
    arraycat = np.concatenate((arraya[0], arraya[2]))

    # Run Bad Function for lists
    try:
        testscore = peakidentify.peak_1d_score(row_i, row_j, -1)
    except ValueError:
        print("An invalid scoremax value was passed to the function, "
              "and was handled correctly.")

    # Run Bad Function for arrays
    try:
        arrayscore = peakidentify.peak_1d_score(arraya[0], arraya[2], -1)

    except ValueError:
        print("An invalid scoremax value was passed to the function, "
              "and was handled correctly.")

    # Running a good example
    testscore = peakidentify.peak_1d_score(row_i, row_j, 1)
    arrayscore = peakidentify.peak_1d_score(arraya[0], arraya[2], 1)

    # make assertions
    assert len(row_i) == len(row_j), 'Input lengths do not match'
    assert len(arrayscore[0][:]) == len(arraycat), """Output list length
    different than concatenated lists length"""
    for i in range(len(rowcat)):
        assert 0 <= testscore[0][i] <= 1, 'Output value outside acceptable range'
        assert 0 <= arrayscore[0][i] <= 1, 'Output value outside acceptable range'


def test_score_max():
    """Evaluates the functionality of the score_max function"""
    # Initialize the test arguments
    k = 2
    row_i = [0, 3]
    row_j = [2, 1]
    rowcat = row_i + row_j
    arraya = np.array([[0, 1], [2, 1], [0, 3]])

    arraycat = np.concatenate((arraya[0], arraya[1]))

    # Run Function for lists
    try:

        maxscores = peakidentify.score_max(row_i, row_j, -1)

    except ValueError:

        print("An invalid k value was passed to the function, "
              "and was handled correctly.")

     # Run Function for arrays
    try:

        arrmaxscores = peakidentify.score_max(arraya[0], arraya[1], -1)

    except ValueError:

        print("An invalid k value was passed to the function, "
              "and was handled correctly.")

    # Run good examples
    maxscores = peakidentify.score_max(row_i, row_j, k)
    arrmaxscores = peakidentify.score_max(arraya[0], arraya[1], k)

    # make assertions
    assert len(arrmaxscores[0]) == len(arraycat), """Output list length different
    than concatenated lists length"""
    for i, _ in enumerate(rowcat):
        assert 0 <= arrmaxscores[0][i] <= 2, 'Output value outside acceptable range'
        assert 0 <= maxscores[0][i] <= 2, 'Output value outside acceptable range'
    for i, _ in enumerate(maxscores, 1):
        assert maxscores[0][i -
                            1] >= maxscores[0][-1], 'Output values are less than the max value'


def test_score_sort():
    """Evaluates the functionality of the score_sort function"""
    # Initialize the test arguments
    row_i = [0, 1]
    row_j = [2, 1]
    rowcat = row_i + row_j
    arraya = np.array([[0, 1], [2, 1], [0, 3]])
    k = 2
    arraycat = np.concatenate((arraya[0], arraya[1]))
    # Run Previous Function to get max score normalization
    maxscores = peakidentify.score_max(row_i, row_j, k)

    # Run Function for lists

    try:
        sortedscores = peakidentify.score_sort(row_i, row_j, max(maxscores[0]))

    except TypeError:

        print("An invalid maxscores from score_max was passed to the function, "
              "and was handled correctly.")

    # Run Function for arrays

    try:

        arrsortedscores = peakidentify.score_sort(
            arraya[0], arraya[1], max(maxscores[0]))

    except TypeError:

        print("An invalid maxscores from score_max was passed to the function, "
              "and was handled correctly.")

    # Run good examples
    sortedscores = peakidentify.score_sort(
        row_i, row_j, int(max(maxscores[0])))
    arrsortedscores = peakidentify.score_sort(arraya[0],
                                              arraya[1],
                                              int(max(maxscores[0])))
    # make assertions
    assert len(arraycat) == len(arrsortedscores[0][0]), """Output list length
    different than concatenated lists length"""
    assert len(rowcat) == len(sortedscores[0][0]), """Output list length
    different than concatenated lists length"""
    for i, _ in enumerate(sortedscores):
        assert sortedscores[0][0][i] <= sortedscores[0][0][i+1], """Output values
        is sorted from smallest to largest"""
        assert arrsortedscores[0][0][i] <= arrsortedscores[0][0][i+1], """Output
        values is sorted from smallest to largest"""
