from spectral_calibration.spectral_calibration import get_filters_data, get_avalanche_data
from absolut_calibration.raman import linear_interpolation
import math
import json


def spect_dens_Selden(temperature: float, wl_grid: list, theta_deg: float, lambda_0: float) -> float:
    m_e = 9.1E-31
    c_light = 3E8
    q_elec = 1.6E-19

    alphaT = m_e * c_light * c_light / (2 * q_elec)
    theta = theta_deg * math.pi / 180.0
    alpha = alphaT / temperature
    section = []
    for wl in wl_grid:
        x = (wl / lambda_0) - 1
        a_loc = math.pow(1 + x, 3) * math.sqrt(2 * (1 - math.cos(theta)) * (1 + x) + math.pow(x, 2))
        b_loc = math.sqrt(1 + x * x / (2 * (1 - math.cos(theta)) * (1 + x))) - 1
        c_loc = math.sqrt(alpha / math.pi) * (1 - (15 / 16) / alpha + 345 / (512 * alpha * alpha))
        section.append((c_loc / a_loc) * math.exp(-2 * alpha * b_loc) / lambda_0)
    return section




avalanche_Path = (r'D:\Ioffe\TS\divertor_thomson\different_calcuations_py\DTS_main\script'
                  r'\spectral_calibration\aw.csv')

filter_Path = (r'D:\Ioffe\TS\divertor_thomson\different_calcuations_py\DTS_main\script\spectral_calibration'
               r'\filters_equator.csv')


def f_e_calc(avalanche_Path, filter_Path):
    avalanche_wl, avalanche_phe = get_avalanche_data(avalanche_Path)
    filters_wl, filters_transm = get_filters_data(filter_Path, filters_transposed=True)
    wl_grid = [700 + 0.2 * step for step in range(1825)]
    Te_grid = [1 + 0.5 * step for step in range(200)]
    result = {'wl_grid': wl_grid,
              'Te_grid': Te_grid}
    for T in Te_grid:
        section = spect_dens_Selden(T, wl_grid, 110, 1064.4)
        all_filters = []
        for filter_ch in range(5):
            integral = 0
            for wl, sec in zip(wl_grid, section):
                filter = linear_interpolation(wl, filters_wl, filters_transm[filter_ch])
                detector = linear_interpolation(wl, avalanche_wl, avalanche_phe)
                integral += sec * filter * detector
            all_filters.append(round(integral, 4))
        result[T] = all_filters
    with open('f_e.json', 'w') as f_file:
        json.dump(result, f_file, indent=4)


#f_e_calc(avalanche_Path, filter_Path)



with open('f_e.json', 'r') as f_file:
    data = json.load(f_file)

for index, (key, value) in enumerate(data.items()):
    if index >= 2:
        try:
            print(key, value[0]/value[1], value[0]/value[2])
            #print](value[0/value[1])
        except ZeroDivisionError:
            pass