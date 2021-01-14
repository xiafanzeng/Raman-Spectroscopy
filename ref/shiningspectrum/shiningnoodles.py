# -*- coding: utf-8 -*-
"""
@Time:2020/8/20 20:19
@Auth"JunLin615
@File:shiningnoodles.py
@IDE:PyCharm
@Motto:With the wind light cloud light mentality, do insatiable things
@email:ljjjun123@gmail.com 
"""
import os

from scipy import interpolate

import numpy as np

import math

from multiprocessing import  Manager, Pool
import time
from shiningspectrum import peak_processing
import spectrafit

# ————————————————————————————————————————————————————————————
def clean_spectra(compound):
    """
    清除重复X数据。
    :param compound:
    :return:
    """
    x_comp = compound['x']
    y_comp = compound['y']
    y_comp = spectrafit.subtract_baseline(y_comp)
    # zip x and y values
    comp_data = list(zip(x_comp, y_comp))
    # clean comp1
    comp_data_clean = []
    for i in range(1, len(comp_data) - 1):
        if comp_data[i][0] == comp_data[i - 1][0]:
            pass
        else:
            comp_data_clean.append(comp_data[i])
    return comp_data_clean


def interpolate_spectra(comp_data_clean):
    """
    插值
    :param comp_data_clean:
    :return:
    """
    # unzip data
    x_comp, y_comp = zip(*comp_data_clean)
    # interpolate data
    comp_int = interpolate.interp1d(x_comp, y_comp, kind='cubic')
    # define ranges
    comp_range = np.arange(int(min(x_comp)) + 1, int(max(x_comp)), 1)
    # run interpolations
    y_comp_interp = comp_int(comp_range)
    # zip interpolated values
    comp_data_int = list(zip(comp_range, y_comp_interp))

    return comp_data_int


def sum_spectra(comp1_data_int, comp2_data_int):
    """
    相加
    :param comp1_data_int:
    :param comp2_data_int:
    :return:
    """
    # add the two spectra
    combined = sorted(comp1_data_int + comp2_data_int)
    # add by like
    same_x = {x: 0 for x, _ in combined}
    for name, num in combined:
        same_x[name] += num
    sum_combined = list(map(tuple, same_x.items()))
    # unzip
    x_combined, y_combined = zip(*sum_combined)
    # set as arrays
    x_combined = np.asarray(x_combined)
    y_combined = np.asarray(y_combined)
    return x_combined, y_combined


def combine_spectra(compound_1, compound_2):
    data1 = clean_spectra(compound_1)
    data2 = clean_spectra(compound_2)

    comp1_data_int = interpolate_spectra(data1)
    comp2_data_int = interpolate_spectra(data2)

    x_combined, y_combined = sum_spectra(comp1_data_int, comp2_data_int)

    return x_combined, y_combined


# ————————————————————————————————————————————————————————————
def shining2noodles(all_spectrum):
    list_of_compounds = []
    for key in list(all_spectrum.keys()):
        x = np.array(all_spectrum[key][0])
        y = np.array(all_spectrum[key][1])

        list_of_compounds.append(({"title": key, "x": x, "y": y}))

    return list_of_compounds

class component_testing:

    def __init__(self, height=0.1, prominence_unknow='auto', prominence_know='auto', distance=10, precision=0.03):
        """

        :param height: 峰值高度阈值
        :param prominence_unknow: 对待测物寻峰时，使用的prominence参数，可以是"auto"或者一个浮点数。
        :param prominence_know: 对光谱数据库进行寻峰时，使用的prominence参数，可以是"auto"或者一个浮点数。
        :param distance: 峰之间的最小水平距离，如果距离小于指定值，会从高度低的峰开始删除，直到满足限制。
        :param precision: 比对峰时的精确度，数字越小越精确。
        :param peak_algorithm: 可以定义为"noodles"或“shining”，更改此参数会使用不同的寻峰算法，"shining"速度很快，"noodles"精细一些。
        """
        self.height = height
        self.prominence_unknow = prominence_unknow
        self.prominence_know = prominence_know
        self.distance = distance
        self.precision = precision

    def run_mp(self, unknown_peaks, known_compound):
        t_start = time.time()
        print("进程{}启动".format(os.getpid()))

        peaks = peak_processing.search_peaks(known_compound["x"], known_compound["y"], height=self.height,
                                                distance=self.distance)
        known_compound_peaks = []
        for i in peaks:
            known_compound_peaks.append(i[0])


        #known_compound_peaks = self.compound_report(known_compound, schema='know')[0]

        assignment_matrix = self.compare_unknown_to_known(unknown_peaks, known_compound_peaks, self.precision)

        result_dic = {"known_compound_peaks": known_compound_peaks, "assignment_matrix": assignment_matrix}
        #known_compound_peaks.append(self.compound_report(known_compound))

        #assignment_matrix.append(self.compare_unknown_to_known(unknown_peaks, known_compound, self.precision))

        t_stop = time.time()
        print("进程{}结束，耗时{}".format(os.getpid(), t_stop - t_start))

        return result_dic


    def peak_assignment(self, unknow_compound, known_compound_list, processes_max=7):


        t_start = time.time()
        print("开始寻找未知物峰值。")
        
        peaks = peak_processing.search_peaks(unknow_compound["x"], unknow_compound["y"], height=self.height,
                                                distance=self.distance)
        unkonw_peak_center = []
        for i in peaks:
            unkonw_peak_center.append(i[0])

        t_stop = time.time()
        print("未知物寻峰结束，耗时{}".format(t_stop - t_start))

        if len(known_compound_list) > processes_max:
            processes = len(known_compound_list)
        else:
            processes = processes_max
        manager = Manager()


        #known_compound_peaks = manager.list()

        #assignment_matrix = manager.list()
        datalist = []
        po = Pool(processes)
        print("建立进程池")

        for known_compound in known_compound_list:

            datalist.append(po.apply_async(self.run_mp, (unkonw_peak_center, known_compound)))

        po.close()
        po.join()

        print("进程池计算完毕，开始比对")
        print("datalist:{},known_compound_list:{}".format(len(datalist), len(known_compound_list)))

        known_compound_peaks = []

        assignment_matrix = []
        for data_ele_pool in datalist:
            data_ele = data_ele_pool.get()
            known_compound_peaks.append(data_ele["known_compound_peaks"])
            assignment_matrix.append(data_ele["assignment_matrix"])

        # import ipdb; ipdb.set_trace()
        unknown_peak_assignments = self.peak_position_comparisons(unkonw_peak_center,
                                                             known_compound_peaks,
                                                             known_compound_list,
                                                             assignment_matrix)

        percentages = self.percentage_of_peaks_found(known_compound_peaks,
                                                assignment_matrix,
                                                known_compound_list)
        
        return unkonw_peak_center, unknown_peak_assignments, percentages

    def percentage_of_peaks_found(self, known_peaks, association_matrix, list_of_known_compounds):
        """This function takes in a list of classified peaks, and returns a percentage of
        how many of the material's peaks are found in the unknown spectrum.
        This can be used as a metric of confidence."""

        # Handle bad inputs
        if not isinstance(known_peaks, list):
            raise TypeError("""Passed value of `known_peaks` is not a list!
            Instead, it is: """ + str(type(known_peaks)))

        if not isinstance(list_of_known_compounds, list):
            raise TypeError("""Passed value of `list_of_known_compounds` is not a list!
            Instead, it is: """ + str(type(list_of_known_compounds)))

        # Now we need to check the elements within the
        # list_of_known_compounds to make sure they are correct.
        for i, _ in enumerate(list_of_known_compounds):
            if not isinstance(list_of_known_compounds[i], dict):
                raise TypeError("""Passed value within `list_of_known_compounds` is not a dictionary!
                Instead, it is: """ + str(type(list_of_known_compounds[i])))

        if not isinstance(association_matrix, list):
            raise TypeError("""Passed value of `association_matrix` is not a float or int!
            Instead, it is: """ + str(type(association_matrix)))

        percentage_dict = {}
        for i, _ in enumerate(list_of_known_compounds):
            count_number = sum(association_matrix[i])
            percentage_dict[list_of_known_compounds[i]
            ['title']] = (count_number / len(known_peaks[i])) * 100

        return percentage_dict

    def peak_position_comparisons(self,unknown_peaks, known_compound_peaks,
                                  known_compound_list,
                                  association_matrix):
        """This function takes in an association matrix and turns the numbers
        given by said matrix into a text label."""

        # Handling errors in inputs.
        if not isinstance(unknown_peaks, list):
            raise TypeError("""Passed value of `unknown_peaks` is not a list!
            Instead, it is: """ + str(type(unknown_peaks)))

        if not isinstance(known_compound_peaks, list):
            raise TypeError("""Passed value of `known_compound_peaks` is not a list!
            Instead, it is: """ + str(type(known_compound_peaks)))

        if not isinstance(known_compound_list, list):
            raise TypeError("""Passed value of `known_compound_list` is not a list!
            Instead, it is: """ + str(type(known_compound_list)))

        # Now we need to check the elements within the known_compound_list to make sure they are correct.
        for i, _ in enumerate(known_compound_list):
            if not isinstance(known_compound_list[i], dict):
                raise TypeError("""Passed value within `known_compound_list` is not a dictionary!
                Instead, it is: """ + str(type(known_compound_list[i])))

        if not isinstance(association_matrix, list):
            raise TypeError("""Passed value of `association_matrix` is not a float or int!
            Instead, it is: """ + str(type(association_matrix)))

        unknown_peak_assignment = []
        # Step through the unknown peaks to make an assignment for each unknown peak.

        for i, _ in enumerate(unknown_peaks):
            # We might be able to make a small performance improvement if we were to somehow
            # not search the peaks we already had searched, but that seems to not be trivial.
            position_assignment = []
            # We'll need an outer loop that walks through all the different compound positions
            for j, _ in enumerate(known_compound_peaks):
                if association_matrix[j][i] == 1:
                    position_assignment.append(known_compound_list[j]['title'])
                else:
                    pass
            if position_assignment == []:
                position_assignment.append("Unassigned")
            unknown_peak_assignment.append(position_assignment)

        return unknown_peak_assignment

    def compare_unknown_to_known(self, combined_peaks, known_peaks, precision):
        """This function takes in peak positions for the spectrum to be
        analyzed and a single known compound and determines if the peaks
        found in the known compound are present in the unknown spectrum."""

        # Handling errors in inputs.
        if not isinstance(combined_peaks, list):
            raise TypeError("""Passed value of `combined_peaks` is not a list!
            Instead, it is: """ + str(type(combined_peaks)))

        if not isinstance(known_peaks, list):
            raise TypeError("""Passed value of `known_peaks` is not a list!
            Instead, it is: """ + str(type(known_peaks)))

        if not isinstance(precision, (float, int)):
            raise TypeError("""Passed value of `precision` is not a float or int!
            Instead, it is: """ + str(type(precision)))

        assignment_matrix = np.zeros(len(combined_peaks))
        peaks_found = 0
        for i, _ in enumerate(combined_peaks):
            for j, _ in enumerate(known_peaks):
                # instead of If, call peak_1D_score
                if math.isclose(combined_peaks[i], known_peaks[j],
                                rel_tol=precision):
                    # Instead of using a 1, just input the score
                    # from the score calculator.
                    # Bigger is better.
                    # Storing only the second component in the list.
                    assignment_matrix[i] = 1
                    peaks_found += 1
                    continue
                else:
                    pass
            if peaks_found == len(known_peaks):
                continue
            else:
                pass
        return assignment_matrix