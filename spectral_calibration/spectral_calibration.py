import json
import bisect

avalanche_Path = 'aw.csv'
calibration_Path = '2023.01.12.json'
lamp_Path = 'Lab_spectrum.txt'
filter_Path = 'filters_equator.csv'

with open(calibration_Path) as calib_file:
    calib_data = json.load(calib_file)


def get_avalanche_data(avalanche_path: str):
    """
    :param avalanche_path:
    :return: 2 списка: длину волны в нм и квантовый выход phe/photon
    """
    h_plank = 6.63E-34
    c = 3E8
    e_charge = 1.602E-19

    full_coef = h_plank * c * 1E9 / e_charge #10E9 переход к метрам

    with open(avalanche_path) as avalanche_data:
        aval_wl = []
        aval_aw = []
        for line in avalanche_data.readlines():
            if any(sym.isalpha() for sym in line):
                pass
            else:
                line = line[:-2]
                wl, aw = line.split(',')
                aval_wl.append(float(wl))
                aval_aw.append(float(aw))
        aval_phe = [aw * full_coef / wl for aw, wl in zip(aval_aw, aval_wl)]

    return aval_wl, aval_phe


def get_lamp_data(lamp_path: str):
    """
    :param lamp_path:
    :return: 2 списка: длину волны в нм и интенсивность лампы на этой длине волны
    """
    with open(lamp_path) as lamp_spectrum_data:
        lamp_wl = []
        lamp_intensity = []
        for line in lamp_spectrum_data.readlines():
            if any(sym.isalpha() for sym in line):
                pass
            else:
                wl, intensity = line.split()
                lamp_wl.append(float(wl) * 1E3) # to nm
                lamp_intensity.append(float(intensity))
        return lamp_wl, lamp_intensity


def get_filters_data(filter_path: str):
    with open(filter_path) as filters_data:
        filters_wl = []
        filters_transmission = []
        for line in filters_data.readlines():
            if any(sym.isalpha() and sym != 'E' and sym != 'e' for sym in line):
                pass
            else:
                wl, *intensity = line.split(',')
                filters_wl.append(float(wl))
                filters_transmission.append(list(float(x) for x in intensity))
        return filters_wl, filters_transmission


def multiplicationLampFiltersAvalanche(lamp_wl: list = None, lamp_intensity: list = None,
                                     avalanche_wl: list = None, avalanche_phe: list = None,
                                     filters_wl: list = None, filter_transm: list = None,
                                     general_gridName: str = 'filters'):

    if general_gridName == 'filters':
        for index, wl in enumerate(filters_wl):
            aval_Xdata = [avalanche_wl[bisect.bisect_right(avalanche_wl, wl) - 1],
                         avalanche_wl[bisect.bisect_right(avalanche_wl, wl)]]

            aval_Ydata = [avalanche_phe[bisect.bisect_right(avalanche_wl, wl) - 1],
                          avalanche_phe[bisect.bisect_right(avalanche_wl, wl)]]

            lamp_Xdata = [lamp_wl[bisect.bisect_right(lamp_wl, wl) - 1],
                          lamp_wl[bisect.bisect_right(lamp_wl, wl)]]

            lamp_Ydata = [lamp_intensity[bisect.bisect_right(lamp_wl, wl) - 1],
                          lamp_intensity[bisect.bisect_right(lamp_wl, wl)]]

            avalanche = linear_intrepolation(wl, aval_Xdata, aval_Ydata)
            lamp = linear_intrepolation(wl, lamp_Xdata, lamp_Ydata)

            coef = avalanche * lamp

            # print(wl, filter_transm[index][0] * coef,
            #           filter_transm[index][1] * coef,
            #           filter_transm[index][2] * coef,
            #           filter_transm[index][3] * coef,
            #           filter_transm[index][4] * coef)
    else:
        print('Write code bitch')
        pass


def linear_intrepolation(x_point: float, Xdata: list, Ydata: list) -> float:
    """
    :param x_point: X-точка, в которой надо найти значение
    :param Xdata: 2 точки имеющихся данных по Х
    :param Ydata: 2 точки имеющихся данных по y
    :return: значение в точке X c помощью линейной интерполяции
    """

    if  Xdata[0] > x_point > Xdata[1]:
        raise Exception
    else:
        y_point = Ydata[0] + (Ydata[1] - Ydata[0]) / (Xdata[1] - Xdata[0]) * (x_point - Xdata[0])
        return y_point



avalanche_wl, avalanche_phe = get_avalanche_data(avalanche_Path)
lamp_wl, lamp_intensity = get_lamp_data(lamp_Path)
filters_wl, filter_transm = get_filters_data(filter_Path)

multiplicationLampFiltersAvalanche(avalanche_wl=avalanche_wl, avalanche_phe=avalanche_phe,
                                   lamp_wl=lamp_wl, lamp_intensity=lamp_intensity,
                                   filters_wl=filters_wl, filter_transm=filter_transm)
