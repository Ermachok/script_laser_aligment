import msgpack
from pathlib import Path
import json
import matplotlib.pyplot as plt
import bisect


def caen_msg_handler(path, t_step=0.325, time_shift=100, noise_len=400, processed_shots=35):
    """
    :param time_shift: сдвиг для построения в одной системе координат
    :param path:путь до файла
    :param t_step: шаг оцифровщика
    :param noise_len: длина для вычисления уровня над нулем и уровня шума
    :param processed_shots: количество обработанных выстрелов
    :return:
    """

    times = []
    caen_zero_lvl = []
    caen_channels_number = 16
    with path.open(mode='rb') as file:
        data = msgpack.unpackb(file.read())
        file.close()

    for caen_channel in range(caen_channels_number):
        caen_ch_0lvl = []
        for laser_shot in range(processed_shots):
            signal_lvl = sum(data[laser_shot]['ch'][caen_channel][:noise_len]) / noise_len
            signal_zero_lvl = [float(x) - signal_lvl for x in data[laser_shot]['ch'][caen_channel]]
            caen_ch_0lvl.append(signal_zero_lvl)

            # fig, ax = plt.subplots(figsize=(9, 6))
            # ax.plot(time, signal_zero_lvl)
            # plt.show()
        caen_zero_lvl.append(caen_ch_0lvl)

    for laser_shot in range(len(caen_zero_lvl[0])):
        time = [time_shift - caen_zero_lvl[0][laser_shot].index(max(caen_zero_lvl[0][laser_shot])) * t_step +
                t_step * t for t in range(1024)]
        times.append(time)

    return times, caen_zero_lvl


class Polychromator:

    def __init__(self, poly_number: int, caen_time: list, caen_data: list, config=None, expected_table: Path = None):
        self.poly_number = poly_number
        self.__signals = caen_data
        self.__signals_time = caen_time
        self.__expected_data = None
        self.__config = config
        self.shots_number = len(caen_time)


    def signal_integrals(self, shots_before_plasma: int = 9, shots_after: int = 10, t_step: float = 0.325):
        number_of_channels = 5
        for poly_ch in range(number_of_channels):

            print('Channel number {}'.format(poly_ch + 1))
            average_parasite = 0

            for shot in range(1, shots_before_plasma):
                parasite_indices = [bisect.bisect_left(self.__signals_time[shot], self.__config[poly_ch]['pest_LeftBord']),
                                    bisect.bisect_right(self.__signals_time[shot], self.__config[poly_ch]['pest_RightBord'])]
                if shot == 3:
                    pest_example = self.__signals[poly_ch][shot][
                                       parasite_indices[0]:parasite_indices[1]]  # 3 - cлучайный выстрел
                    pest_example[:] = [sig/max(pest_example) for sig in pest_example]
                average_parasite += sum(self.__signals[poly_ch][shot][parasite_indices[0]:parasite_indices[1]]) * t_step

            average_parasite = average_parasite / (shots_before_plasma - 1)
            print('Average integral parasite(before plasma) {} mV*ns'.format(average_parasite))

            print('shot, signal integral, after subtraction average, pest_approx, after subtraction approx ')
            for shot in range(shots_before_plasma, shots_before_plasma + shots_after):
                signal_indices = [bisect.bisect_left(self.__signals_time[shot], self.__config[poly_ch]['sig_LeftBord']),
                                  bisect.bisect_right(self.__signals_time[shot], self.__config[poly_ch]['sig_RightBord'])]
                signal_integral = sum(self.__signals[poly_ch][shot][signal_indices[0]:signal_indices[1]]) * t_step

                pest_indices = [bisect.bisect_left(self.__signals_time[shot], self.__config[poly_ch]['pest_MaxBord'][0]),
                                  bisect.bisect_right(self.__signals_time[shot], self.__config[poly_ch]['pest_MaxBord'][1])]
                pest_example_integral = (sum(pest_example)
                                         * max(self.__signals[poly_ch][shot][pest_indices[0]:pest_indices[1]]) * t_step)

                print(shot, signal_integral,
                      signal_integral - average_parasite,
                      pest_example_integral,
                      signal_integral - pest_example_integral)

            print('-'*40)

    def signal_approx(self):
        pass


    def set_expected_data(self):
        pass


    def plot_expected(self):
        pass

    def get_data(self, shot_num: int = None, ch_num: int = None):
        return self.__signals_time[shot_num], self.__signals[ch_num][shot_num]


msg_files_num_x10 = [4, 5, 6, 7]
discharge_num = '43256'


all_caens = []
for msg_num in msg_files_num_x10:
    path = Path('C:\TS_data\\DTS_summer_2023\%s\%s.msgpk' % (discharge_num, msg_num))
    times, caen_data = caen_msg_handler(path)
    all_caens.append({'caen_num': msg_num,
                      'shots_time': times,
                      'caen_channels': caen_data})

with open('сonfig') as file:
    config_data = json.load(file)


poly_1 = Polychromator(poly_number=1, config=config_data['equator_caens'][4]['channels'][1:6], expected_table=None,
                       caen_time=all_caens[0]['shots_time'], caen_data=all_caens[0]['caen_channels'][1:6])

poly_2 = Polychromator(poly_number=2, config=config_data['equator_caens'][4]['channels'][6:11], expected_table=None,
                       caen_time=all_caens[0]['shots_time'], caen_data=all_caens[0]['caen_channels'][6:11])

poly_3 = Polychromator(poly_number=3, config=config_data['equator_caens'][4]['channels'][11:16], expected_table=None,
                       caen_time=all_caens[0]['shots_time'], caen_data=all_caens[0]['caen_channels'][11:16])

poly_4 = Polychromator(poly_number=4, config=config_data['equator_caens'][5]['channels'][1:6], expected_table=None,
                       caen_time=all_caens[0]['shots_time'], caen_data=all_caens[0]['caen_channels'][1:6])

poly_5 = Polychromator(poly_number=5, config=config_data['equator_caens'][5]['channels'][1:6], expected_table=None,
                       caen_time=all_caens[0]['shots_time'], caen_data=all_caens[0]['caen_channels'][1:6])

poly_6 = Polychromator(poly_number=6, config=config_data['equator_caens'][5]['channels'][1:6], expected_table=None,
                       caen_time=all_caens[0]['shots_time'], caen_data=all_caens[0]['caen_channels'][1:6])

poly_7 = Polychromator(poly_number=7, config=config_data['equator_caens'][6]['channels'][1:6], expected_table=None,
                       caen_time=all_caens[0]['shots_time'], caen_data=all_caens[0]['caen_channels'][1:6])

poly_8 = Polychromator(poly_number=8, config=config_data['equator_caens'][6]['channels'][1:6], expected_table=None,
                       caen_time=all_caens[0]['shots_time'], caen_data=all_caens[0]['caen_channels'][1:6])

poly_9 = Polychromator(poly_number=9, config=config_data['equator_caens'][6]['channels'][1:6], expected_table=None,
                       caen_time=all_caens[0]['shots_time'], caen_data=all_caens[0]['caen_channels'][1:6])

poly_10 = Polychromator(poly_number=10, config=config_data['equator_caens'][7]['channels'][1:6], expected_table=None,
                        caen_time=all_caens[0]['shots_time'], caen_data=all_caens[0]['caen_channels'][1:6])

poly_1.signal_integrals()

fig, ax = plt.subplots(nrows=5, ncols=1, figsize=(13, 8))


for ch in range(5):
    for shot in range(1, 9):
        time, signal = poly_1.get_data(shot_num=shot, ch_num=ch, )
        ax[ch].plot(time, signal, label='shot %d' %shot)
    ax[ch].set_xlim(20, 70)


#ax[0].legend()
#ax[0].set_xlim(0, 80)
#ax[1].set_xlim(0, 80)

plt.tight_layout()
#plt.show()