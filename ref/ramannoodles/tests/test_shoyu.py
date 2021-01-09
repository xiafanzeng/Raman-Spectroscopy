"""
Test functions for the shoyu.py module
"""

import os
import pickle
import numpy as np
from ramannoodles import shoyu

# open spectra library
SHOYU_DATA_DICT = pickle.load(open('raman_spectra/shoyu_data_dict.p', 'rb'))


def test_download_cas():
    """
    Test function that confirms that the raman_spectra/ directory exists/was created,
    and confirms that the .jdx file was saved with the correct filename.
    """
    # CAS registry number for water
    cas_num = '7732-18-5'
    shoyu.download_cas(cas_num)
    assert os.path.isdir('raman_spectra/'), 'directory not found'
    assert os.path.isfile(
        'raman_spectra/7732185_NIST_IR.jdx'), 'file not saved correctly'
    # Various try statements to make sure that bad inputs are handled correctly.
    try:
        shoyu.download_cas(7732185)
    except TypeError:
        print(
            'An int was passed to the function, and it was handled well with a TypeError.')


def test_add_jdx():
    """
    Test function that confirms that custom labeling is successful when updating shoyu_data_dict.p,
    and that the y units are correctly converted to ABSORBANCE instead of the default TRANSMITTENCE.
    """
    # .jdx file containing water data
    filename = '7732185_NIST_IR.jdx'
    shoyu_data_dict = shoyu.add_jdx(
        'raman_spectra/'+filename, label='Water_label_test')
    assert 'Water_label_test' in shoyu_data_dict, 'custom label not applied successfully'
    water = shoyu_data_dict['Water_label_test']
    assert water['yunits'] == 'ABSORBANCE', 'Incorrect y units stored'
    assert filename[-4:] == '.jdx', 'File type is not .jdx'
    try:
        shoyu.download_cas(1)
    except TypeError:
        print(
            'An int was passed to the function, and it was handled well with a TypeError.')


def test_initialize_standard_library():
    """
    Test function that confirms the raman_spectra/ directory is created, the .jdx files are
    downloaded and stored correctly, and that the shoyu_data_dict.p file is generated.
    """
    shoyu.initialize_standard_library()
    assert os.path.isdir('raman_spectra/'), 'Directory not found'
    assert os.path.isfile(
        'raman_spectra/7732185_NIST_IR.jdx'), 'file not saved correctly'
    assert os.path.isfile(
        'raman_spectra/shoyu_data_dict.p'), 'shoyu_data_dict.p not found'


def test_more_please():
    """
    Test function that confirms that the pentane .jdx file was downloaded correctly and was
    successfully added to shoyu_data_dict.p
    """
    # CAS registry number for pentane
    cas_num = '109-66-0'
    shoyu_data_dict = shoyu.more_please(cas_num)
    assert os.path.isfile('raman_spectra/109660_NIST_IR.jdx'), 'file not found'
    assert 'N-PENTANE' in shoyu_data_dict, 'N-PENTANE not successfully added to shoyu_data_dict'
    try:
        shoyu.download_cas(109660)
    except TypeError:
        print(
            'An int was passed to the function, and it was handled well with a TypeError.')


def test_clean_spectra():
    """
    Test function for shoyu.clean_spectra. It verifies that the output type is correct,
    that repeated data points were removed from the input data, and that bad input types
    are handled correctly.
    """
    compound = SHOYU_DATA_DICT['WATER']
    comp_data_clean = shoyu.clean_spectra(compound)
    assert isinstance(comp_data_clean, list), 'output type not a list'
    assert len(comp_data_clean) < len(
        compound['x']), 'repeat data points were not removed'
    try:
        shoyu.clean_spectra(compound=[[1, 2, 3, 4], [0.2, 0.4, 1.0, 0.01]])
    except TypeError:
        print(
            'A list was passed to the function, and it was handled well with a TypeError.')


def test_interpolate_spectra():
    """
    Test function for shoyu.interpolate_spectra. It verifies that the output type is correct,
    and that bad input types are handled correctly.
    """
    compound = SHOYU_DATA_DICT['WATER']
    comp_data_clean = shoyu.clean_spectra(compound)
    comp_data_int = shoyu.interpolate_spectra(comp_data_clean)
    assert isinstance(
        comp_data_int, list), 'Output type not correct, a list is expected'
    try:
        shoyu.interpolate_spectra([1, 2, 3, 4])
    except TypeError:
        print('A list of ints was passed to the function, and was handled well with a TypeError.')


def test_sum_spectra():
    """
    Test function for shoyu.sum_spectra. It checks to confirm that the output data lengths match,
    that the output types are correct, and that bad input types are handled well.
    """
    compound1 = SHOYU_DATA_DICT['WATER']
    compound2 = SHOYU_DATA_DICT['CARBON MONOXIDE']
    comp1_data_clean = shoyu.clean_spectra(compound1)
    comp2_data_clean = shoyu.clean_spectra(compound2)
    comp1_data_int = shoyu.interpolate_spectra(comp1_data_clean)
    comp2_data_int = shoyu.interpolate_spectra(comp2_data_clean)
    x_combined, y_combined = shoyu.sum_spectra(comp1_data_int, comp2_data_int)
    assert len(x_combined) == len(
        y_combined), 'Output data lengths do not match'
    assert isinstance(
        x_combined, np.ndarray), 'x_combined type is not a numpy.ndarray.'
    assert isinstance(
        y_combined, np.ndarray), 'y_combined type is not a numpy.ndarray.'
    try:
        shoyu.sum_spectra(1.2, comp2_data_int)
    except TypeError:
        print(
            'A float was passed to the function, and it was handled well with a TypeError.')
    try:
        shoyu.sum_spectra(comp1_data_int, 66.6)
    except TypeError:
        print(
            'A float was passed to the function, and it was handled well with a TypeError.')


def test_combine_spectra():
    """
    Test function that confirms that the two compounds from shoyu_data_dict.p were combined
    sucessfully, that the output data has the correct shape, and that the output range is
    within the overall range of the two individual compounds.
    """
    compound_1 = SHOYU_DATA_DICT['WATER']
    compound_2 = SHOYU_DATA_DICT['CARBON MONOXIDE']
    data = shoyu.combine_spectra(compound_1, compound_2)
    assert len(data[0]) == len(data[1]), 'lengths of x and y data do not match'
    assert len(data) == 2, 'shape of output data different than expected'
    ranges = [max(compound_1['x']), min(compound_1['x']),
              max(compound_2['x']), min(compound_2['x'])]
    assert min(ranges) <= min(data[0]), """
    output data contains values below the minimum range of either compound"""
    assert max(ranges) >= max(data[0]), """
    output data contains values above the maximum range of either compound"""
    try:
        shoyu.combine_spectra([1, 2, 3, 4], compound_2)
    except TypeError:
        print(
            'A list was passed to the function, and it was handled well with a TypeError.')
    try:
        shoyu.combine_spectra(compound_1, [1, 2, 3, 4])
    except TypeError:
        print(
            'A list was passed to the function, and it was handled well with a TypeError.')
