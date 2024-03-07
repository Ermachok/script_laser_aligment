from pathlib import Path
import json
import matplotlib.pyplot as plt
import bisect
import statistics
from T_e_calculation.utilities.masg_handler import handle_all_caens
import time


class Polychromator:

    def __init__(self, poly_number: int, fiber_number: int, caen_time: list, caen_data: list,
                 config=None, absolut_calib: Path = '../absolut_calibration/fibers_A_26_02_2024.json',
                 spectral_calib: Path = '../spectral_calibration/EN_spectral_config_2024-01-23.json'):

        """
        :param poly_number: номер полихроматора в стойке!
        :param fiber_number: номер волокна, 1 - вверх
        :param caen_time: приведенные к по максимуму времена
        :param caen_data: данные с каена, 5 каналов
        :param config: конфиг
        :param absolut_calib:
        """

        self.poly_number = poly_number
        self.fiber_number = fiber_number

        self.__signals = caen_data
        self.__signals_time = caen_time

        self.__expected_data = None
        self.__config = config

        with open(spectral_calib, 'r') as spec_file:
            self.spectral_calibration = json.load(spec_file)['poly_ind_%d' % self.poly_number]

        with open(absolut_calib, 'r') as absolut_file:
            self.abs_calib = json.load(absolut_file)['fibers_A'][self.fiber_number-1]

        self.temperatures = []
        self.density = []


    def get_signal_integrals(self, shots_before_plasma: int = 9, shots_after: int = 15,
                             number_of_ch: int = 5, t_step: float = 0.325):
        """
        RETURNS PHE
        :param shots_before_plasma:
        :param shots_after:
        :param number_of_ch:
        :param t_step:
        :return:
        """
        q_e = 1.6E-19
        M_gain = 1E2
        R_gain = 1E4
        G_magic = 2.43
        divider = 0.5
        gain_out = 10
        mV_2_V = 1E-3
        ns_2_s = 1E-9
        A = q_e * M_gain * R_gain * G_magic * divider * gain_out
        all_const = mV_2_V * ns_2_s / A

        # for poly_ch in range(number_of_ch):
        # print('\nFiber number {fiber}\nChannel number {channel}'.format(fiber=self.fiber_number,
        #                                                                 channel=poly_ch + 1))
        # pestCheck = self.rude_pestCheck(self.__signals[poly_ch][1:shots_before_plasma])

        # if pestCheck:
        #     average_parasite = 0
        #     for shot in range(1, shots_before_plasma):
        #         parasite_indices = [
        #             bisect.bisect_left(self.__signals_time[shot], self.__config[poly_ch]['pest_LeftBord']),
        #             bisect.bisect_right(self.__signals_time[shot], self.__config[poly_ch]['pest_RightBord'])]
        #
        #         average_parasite += sum(
        #             self.__signals[poly_ch][shot][parasite_indices[0]:parasite_indices[1]]) * t_step
        #
        #     average_parasite = average_parasite / (shots_before_plasma - 1)
        # print('Average integral parasite(before plasma) {} mV*ns'.format(average_parasite))
        # for shot in range(shots_before_plasma, shots_before_plasma + shots_after):
        #     signal_indices = [bisect.bisect_left(self.__signals_time[shot], self.__config[poly_ch]['sig_LeftBord']),
        #                        bisect.bisect_right(self.__signals_time[shot], self.__config[poly_ch]['sig_RightBord'])]
        #     signal_integral = sum(self.__signals[poly_ch][shot][signal_indices[0]:signal_indices[1]]) * t_step
        # pass

        # print('\nIntegrals mV * ns')
        # print('\nIntegrals phe')
        all_shots_signal = []
        all_shots_noise = []
        for shot in range(1, shots_before_plasma + shots_after):
            # print(shot, end=' ')
            all_ch_signal = []
            all_ch_noise = []
            for poly_ch in range(number_of_ch):
                signal_indices = [bisect.bisect_left(self.__signals_time[shot], self.__config[poly_ch]['sig_LeftBord']),
                                  bisect.bisect_right(self.__signals_time[shot],
                                                      self.__config[poly_ch]['sig_RightBord'])]

                signal_integral = sum(self.__signals[poly_ch][shot][signal_indices[0]:signal_indices[1]]) * t_step

                all_ch_signal.append(signal_integral * all_const)
                all_ch_noise.append(statistics.stdev(self.__signals[poly_ch][shot][:200]) * all_const * t_step *
                                    (signal_indices[1] - signal_indices[0]))

                # print('signal', round(signal_integral * all_const, 2),
                #       'noise', round(statistics.stdev(self.__signals[poly_ch][shot][:200]) * t_step * all_const *
                #                      (signal_indices[1] - signal_indices[0]), 2), end='; ')

            all_shots_signal.append(all_ch_signal)
            all_shots_noise.append(all_ch_noise)

        return all_shots_signal, all_shots_noise


    def get_temperatures(self, print_flag = False):
        """
        GIVES TEMPERATURE LIST
        :return:
        """
        fe_data = self.get_expected_fe()
        signals, noises = self.get_signal_integrals()

        results = []
        for shot, noise in zip(signals, noises):
            ans = []
            for index, (T_e, f_e) in enumerate(fe_data.items()):
                khi = 0
                if index >= 2:

                    sum_1 = 0
                    for ch in range(3):
                        sum_1 += shot[ch] * (f_e[ch] * self.spectral_calibration[ch]) / noise[ch] ** 2

                    sum_2 = 0
                    for ch in range(3):
                        sum_2 += (f_e[ch] * self.spectral_calibration[ch]) ** 2 / noise[ch] ** 2

                    for ch in range(3):
                        khi += (shot[ch] - sum_1 * (f_e[ch] * self.spectral_calibration[ch]) / sum_2) ** 2 / noise[ch] ** 2
                    ans.append({T_e: khi})

            results.append(ans)

        for shot in results:
            sort = sorted(shot, key=lambda x: list(x.values())[0])
            for T in sort[0].keys():
                self.temperatures.append(T)
                if print_flag:
                    print(T, end=' ')
        print()

    def get_density(self, print_flag=False):
        laser_energy = 1.5
        fe_data = self.get_expected_fe()
        signals, noises = self.get_signal_integrals()
        elector_radius = 6.652E-29

        for shot, noise, T_e in zip(signals, noises, self.temperatures):
            sum_numerator = 0
            sum_divider = 0
            for ch in range(5):
                sum_numerator += shot[ch] * (fe_data[T_e][ch] * self.spectral_calibration[ch]) / noise[ch] ** 2
                sum_divider += (fe_data[T_e][ch] * self.spectral_calibration[ch]) ** 2 / noise[ch] ** 2

            self.density.append(sum_numerator / (sum_divider * laser_energy * self.abs_calib * elector_radius))
            if print_flag:
                print('%.2e' % (sum_numerator / (sum_divider * laser_energy * self.abs_calib * elector_radius)), end=' ')
        #print()


    @staticmethod
    def rude_pestCheck(signals_before_plasma, start_ind: int = 500, end_ind: int = 700, t_step: float = 0.325):
        """
        :param signals_before_plasma: количество выстрелов перед плазмой
        :param start_ind: номер ячейки из оцифровщика, с которой начинается считаться интеграл
        :param end_ind: конец окна интегрирования - старт и конец выбраны с запасом из знания о том, где расположен паразит
        :param t_step: шаг оцифровщика
        :return: есть паразит или нет
        """
        pestSum = 0
        for shot in signals_before_plasma:
            pestSum += sum(shot[start_ind:end_ind])
        pest = pestSum / len(signals_before_plasma) * t_step
        if pest > 100:
            print('Average summ in pest area: {pest} mV * ns\n'
                  'There is a chance of a parasite existing'.format(pest=pest))
            return True
        return False

    def signal_approx(self):
        pass

    @staticmethod
    def get_expected_fe(path: str = '../temperature_estimation/f_e.json'):
        with open(path, 'r') as f_file:
            fe_data = json.load(f_file)
        return fe_data

    def plot_expected(self):
        pass

    def plot_rawSignals(self, from_shot: int = 10, to_shot: int = 20):
        fig, ax = plt.subplots(nrows=5, ncols=1, figsize=(13, 8))

        for ch in range(5):
            for shot in range(from_shot, to_shot):
                time, signal = self.get_raw_data(shot_num=shot, ch_num=ch)
                ax[ch].plot(time, signal, label='shot %d' % shot)
                ax[ch].set_xlim([0, 80])
        ax[0].legend(ncol=3)
        plt.subplots_adjust(left=0.05, right=0.95, top=0.93, bottom=0.07)
        plt.show()

    def get_raw_data(self, shot_num: int = None, ch_num: int = None):
        if ch_num is None and shot_num is None:
            return self.__signals_time, self.__signals
        return self.__signals_time[shot_num], self.__signals[ch_num][shot_num]



with open('сonfig') as file:
    config_data = json.load(file)
discharge_num = '43256'


all_caens = handle_all_caens(discharge_num=discharge_num)


poly_0 = Polychromator(poly_number=0, fiber_number=1,
                       config=config_data['equator_caens'][4]['channels'][1:6],
                       caen_time=all_caens[0]['shots_time'], caen_data=all_caens[0]['caen_channels'][1:6])

poly_1 = Polychromator(poly_number=1, fiber_number=2,
                       config=config_data['equator_caens'][4]['channels'][6:11],
                       caen_time=all_caens[0]['shots_time'], caen_data=all_caens[0]['caen_channels'][6:11])

poly_2 = Polychromator(poly_number=2, fiber_number=3,
                       config=config_data['equator_caens'][4]['channels'][11:16],
                       caen_time=all_caens[0]['shots_time'], caen_data=all_caens[0]['caen_channels'][11:16])

poly_3 = Polychromator(poly_number=3, fiber_number=4,
                       config=config_data['equator_caens'][5]['channels'][1:6],
                       caen_time=all_caens[1]['shots_time'], caen_data=all_caens[1]['caen_channels'][1:6])

poly_4 = Polychromator(poly_number=4, fiber_number=5,
                       config=config_data['equator_caens'][5]['channels'][6:11],
                       caen_time=all_caens[1]['shots_time'], caen_data=all_caens[1]['caen_channels'][6:11])

poly_5 = Polychromator(poly_number=5, fiber_number=7,
                       config=config_data['equator_caens'][7]['channels'][6:11],
                       caen_time=all_caens[1]['shots_time'], caen_data=all_caens[1]['caen_channels'][11:16])

poly_6 = Polychromator(poly_number=6, fiber_number=8,
                       config=config_data['equator_caens'][5]['channels'][11:16],
                       caen_time=all_caens[2]['shots_time'], caen_data=all_caens[2]['caen_channels'][1:6])

poly_7 = Polychromator(poly_number=7, fiber_number=9,
                       config=config_data['equator_caens'][6]['channels'][1:6],
                       caen_time=all_caens[2]['shots_time'], caen_data=all_caens[2]['caen_channels'][6:11])

poly_10 = Polychromator(poly_number=10, fiber_number=6,
                        config=config_data['equator_caens'][6]['channels'][6:11],
                        caen_time=all_caens[3]['shots_time'], caen_data=all_caens[3]['caen_channels'][6:11])


fibers = [poly_0, poly_1, poly_2, poly_3, poly_4, poly_10, poly_5, poly_6, poly_7]

for fiber in fibers[1:]:
    fiber.get_temperatures(print_flag=True)
    fiber.get_density(print_flag=False)

