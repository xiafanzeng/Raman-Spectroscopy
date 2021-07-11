from scipy.signal import find_peaks
import numpy as np
import math

def search_peaks(x_data, y_data, height=0.1, distance=10):
    prominence = np.mean(y_data)
    peak_list = find_peaks(y_data, height=height, prominence=prominence, distance=distance)

    peaks = []
    for i in peak_list[0]:
        peak = (x_data[i], y_data[i])
        peaks.append(peak)

    return peaks


def search_database_peaks(all_spectrum, height=0.1, distance=10):
    peaks_database = {}

    for key in list(all_spectrum.keys()):
        x_data = all_spectrum[key][0]
        y_data = all_spectrum[key][1]

        peaks = search_peaks(x_data, y_data, height=height, distance=distance)
        peaks_database.update({key: peaks})

    return peaks_database


def compare_peaks(peaks_database, peaks, abs_tol=5):
    coincide_information = {}

    for key in list(peaks_database.keys()):
        coincide_list = []
        for peak_d in peaks_database[key]:
            for peak in peaks:
                if math.isclose(peak[0], peak_d[0], abs_tol=abs_tol):
                    coincide_list.append([peak_d[0], peak[0]])

        coincide_information.update(
            {key: {'coincide_list': coincide_list, 'coincide_number': [len(peaks_database[key]), len(coincide_list)]}})

    return coincide_information


def judge_matter(coincide_information, criterion=0.99):
    contain_dict = {}
    for key in list(coincide_information.keys()):
        coincide_number = coincide_information[key]['coincide_number']
        key_criterion = coincide_number[1] / coincide_number[0]
        if key_criterion >= criterion:
            contain_dict.update({key: key_criterion})
    return contain_dict


def classify(x_data, y_data, all_spectrum):
    peaks = search_peaks(x_data,y_data)
    database_peaks = search_database_peaks(all_spectrum)
    print(database_peaks)
    compare_result = compare_peaks(database_peaks,peaks)
    # pass
    # print(compare_result)
    return compare_result
    compare_result=judge_matter(compare_result)
