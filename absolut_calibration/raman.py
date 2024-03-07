import json
import math
from spectral_calibration.spectral_calibration import get_filters_data, get_avalanche_data
import bisect
import statistics


def linear_interpolation(x_point: float, Xdata: list, Ydata: list) -> float:
    """

    :param x_point: точка в которой надо найти
    :param Xdata: лист по Х данных
    :param Ydata: лист по Н данных
    :return: линейная интерполяция
    """
    ind_1 = bisect.bisect_right(Xdata, x_point) - 1
    ind_2 = bisect.bisect_right(Xdata, x_point)

    if Xdata[ind_1] > x_point > Xdata[ind_2]:
        raise Exception
    else:
        y_point = Ydata[ind_1] + (Ydata[ind_2] - Ydata[ind_1]) / (Xdata[ind_2] - Xdata[ind_1]) * (
                    x_point - Xdata[ind_1])
        # print(Xdata[ind_1], Ydata[ind_1], Xdata[ind_2], Ydata[ind_2], x_point, y_point)
        return y_point


def get_raman_wl_section(gas_temperature: float, las_wl: float = 1064.4E-9, J_lim: int = 50):
    gamma_squared = 0.51E-60  # m^6
    B_0 = 198.96  # m^-1
    h_plank = 6.63E-34
    c_light = 3E8
    exp = 2.718

    exp_coef = h_plank * c_light * B_0 / (k_bolt * gas_temperature)

    def calculate_normalizing_coef(J_lim):
        A = 0
        for j in range(0, J_lim):
            if j % 2 == 0:
                A += 3 * (2 * j + 1) * exp ** (-exp_coef * j * (j + 1))
            else:
                A += 6 * (2 * j + 1) * exp ** (-exp_coef * j * (j + 1))
        return A

    def population(J, A):
        if J % 2 == 0:
            F = A ** (-1) * 6 * (2 * J + 1) * exp ** (-exp_coef * J * (J + 1))
        else:
            F = A ** (-1) * 3 * (2 * J + 1) * exp ** (-exp_coef * J * (J + 1))
        return F

    A = calculate_normalizing_coef(J_lim)

    raman_wl_list = []
    raman_section_list = []
    const = gamma_squared * 64 * math.pi ** 4 / 45
    for J in range(2, J_lim):
        wl_scat = 1 / ((1 / las_wl) + B_0 * (4 * J - 2))
        ram_sec = const * 3 * J * (J - 1) / (2 * (2 * J + 1) * (2 * J - 1) * wl_scat ** 4)
        raman_wl_list.append(wl_scat * 1E9)
        raman_section_list.append(ram_sec * population(J, A))
    return raman_wl_list, raman_section_list


def load_calibration_phe(phe_file_path, laser_ophir_path):
    ophir_to_J = 0.0275

    with open(phe_file_path, 'r') as calibration_file:
        calibration_data = calibration_file.readlines()

    with open(laser_ophir_path, 'r') as laser_ophir_path:
        laser_data = laser_ophir_path.readlines()

    all_polys = []
    for poly in range(1, 10):
        temp_data = []
        for shot in range(1, len(calibration_data)):
            laser_energy  = float(laser_data[shot - 1].split()[1]) / ophir_to_J
            temp_data.append(
                float(calibration_data[shot].split(',')[poly]) / laser_energy)
        all_polys.append(temp_data)
    return all_polys


if __name__ == '__main__':

    avalanche_Path = (r'D:\Ioffe\TS\divertor_thomson\different_calcuations_py\DTS_main\script'
                      r'\spectral_calibration\aw.csv')

    filter_Path = (r'D:\Ioffe\TS\divertor_thomson\different_calcuations_py\DTS_main\script\spectral_calibration'
                   r'\filters_equator.csv')

    spectral_calibration_Path = (r'D:\Ioffe\TS\divertor_thomson\different_calcuations_py\DTS_main\script'
                                 r'\spectral_calibration\EN_spectral_config_2024-02-15.json')

    k_bolt = 1.38E-23  # J/K
    gas_temperature = 23.4 + 273.15  # K

    avalanche_wl, avalanche_phe = get_avalanche_data(avalanche_Path)
    filters_wl, filters_transm = get_filters_data(filter_Path, filters_transposed=True)
    raman_wl, raman_section = get_raman_wl_section(gas_temperature=gas_temperature, las_wl=1064.4E-9)

    calib_phe_to_laser = load_calibration_phe('D:/Ioffe/TS/divertor_thomson/calibration'
                                              '/16.06.2023/caen_files/00846/1ch_scat_Nphe_00846.csv',
                                              r'D:\Ioffe\TS\divertor_thomson\calibration'
                                              r'\16.06.2023\caen_files\00846\ophir_7564_corrected.dat')

    #with open('../spectral_calibration/EN_spectral_config_2024-01-23.json') as spectral_file:
        #spectral_calibration_data = json.load(spectral_file)

    p_torr = 80  # Tor
    p_pascal = p_torr * 133.3  # pascal
    n = p_pascal / (k_bolt * gas_temperature)

    fiber_poly = {
        1: 0,
        2: 1,
        3: 2,
        4: 3,
        5: 4,
        6: 10,
        7: 5,
        8: 6,
        9: 7,
    }

    all_fibers = {}
    for fiber in fiber_poly.keys():
        #poly_ind = 'poly_ind_{}'.format(fiber_poly[fiber])
        #kappa_list = spectral_calibration_data[poly_ind]
        integral = 0
        all_channels = []
        for x, y in zip(raman_wl, raman_section):
            # print(x, y)
            filter = linear_interpolation(x, filters_wl, filters_transm[0])
            detector = linear_interpolation(x, avalanche_wl, avalanche_phe)

            integral += y * filter * detector
        for ch in range(1):
            calibration = statistics.median(calib_phe_to_laser[fiber-1][:300])
            all_channels.append(calibration / 100 / (integral * n))
        all_fibers['fib_{}'.format(fiber)] = all_channels

    for x in all_fibers.values():
        print('%f'%x[0]+',')
