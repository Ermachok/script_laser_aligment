import msgpack
from pathlib import Path
import json
import matplotlib.pyplot as plt
import bisect
import statistics


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
            median = statistics.median(data[laser_shot]['ch'][caen_channel][:noise_len])
            signal_zero_lvl = [round(float(x) - median, 5) for x in data[laser_shot]['ch'][caen_channel]]
            caen_ch_0lvl.append(signal_zero_lvl)

            # fig, ax = plt.subplots(figsize=(9, 6))
            # ax.plot(time, signal_zero_lvl)
            # plt.show()
        caen_zero_lvl.append(caen_ch_0lvl)

    for laser_shot in range(processed_shots):
        time = [round(time_shift - caen_zero_lvl[0][laser_shot].index(max(caen_zero_lvl[0][laser_shot])) * t_step +
                t_step * t, 5) for t in range(1024)]
        times.append(time)

    return times, caen_zero_lvl


class Polychromator:

    def __init__(self, poly_number: int, fiber_number: int, caen_time: list, caen_data: list,
                 config=None, expected_table: Path = None):

        """
        :param poly_number: номер полихроматора в стойке!
        :param fiber_number: номер волокна, 1 - вверх
        :param caen_time: приведенные к по максимуму времена
        :param caen_data: данные с каена, 5 каналов
        :param config: конфиг
        :param expected_table:
        """

        self.poly_number = poly_number
        self.fiber_number = fiber_number
        self.__signals = caen_data
        self.__signals_time = caen_time
        self.__expected_data = None
        self.__config = config


    def signal_integrals(self, shots_before_plasma: int = 9, shots_after: int = 15,
                         number_of_ch: int = 5, t_step: float = 0.325):



        for poly_ch in range(number_of_ch):
            print('\nFiber number {fiber}\nChannel number {channel}'.format(fiber=self.fiber_number,
                                                                            channel=poly_ch + 1))
            pestCheck = self.rude_pestCheck(self.__signals[poly_ch][1:shots_before_plasma])

            if pestCheck:
                average_parasite = 0

                for shot in range(1, shots_before_plasma):
                    parasite_indices = [bisect.bisect_left(self.__signals_time[shot], self.__config[poly_ch]['pest_LeftBord']),
                                        bisect.bisect_right(self.__signals_time[shot], self.__config[poly_ch]['pest_RightBord'])]

                    average_parasite += sum(self.__signals[poly_ch][shot][parasite_indices[0]:parasite_indices[1]]) * t_step

                average_parasite = average_parasite / (shots_before_plasma - 1)
                print('Average integral parasite(before plasma) {} mV*ns'.format(average_parasite))
                # for shot in range(shots_before_plasma, shots_before_plasma + shots_after):
                #     signal_indices = [bisect.bisect_left(self.__signals_time[shot], self.__config[poly_ch]['sig_LeftBord']),
                #                        bisect.bisect_right(self.__signals_time[shot], self.__config[poly_ch]['sig_RightBord'])]
                #     signal_integral = sum(self.__signals[poly_ch][shot][signal_indices[0]:signal_indices[1]]) * t_step
                pass

        print('\nIntegrals mV * ns')
        for shot in range(shots_before_plasma + shots_after):
            print(shot+1, end=' ')
            for poly_ch in range(number_of_ch):
                signal_indices = [bisect.bisect_left(self.__signals_time[shot], self.__config[poly_ch]['sig_LeftBord']),
                                  bisect.bisect_right(self.__signals_time[shot], self.__config[poly_ch]['sig_RightBord'])]
                signal_integral = sum(self.__signals[poly_ch][shot][signal_indices[0]:signal_indices[1]]) * t_step
                print(signal_integral, end=' ')
            print()


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


    def set_expected_data(self):
        pass


    def plot_expected(self):
        pass

    def get_data(self, shot_num: int = None, ch_num: int = None):
        if ch_num is None and shot_num is None:
            return self.__signals_time, self.__signals
        return self.__signals_time[shot_num], self.__signals[ch_num][shot_num]


msg_files_num_x10 = [4, 5, 6, 7]
discharge_num = '43256'


all_caens = []
for msg_num in msg_files_num_x10:
    #path = Path('C:\TS_data\\DTS_summer_2023\%s\%s.msgpk' % (discharge_num, msg_num))
    path = Path('D:\Ioffe\TS\divertor_thomson\measurements\\%s\\%s.msgpk' % (discharge_num, msg_num))
    times, caen_data = caen_msg_handler(path)
    all_caens.append({'caen_num': msg_num,
                      'shots_time': times,
                      'caen_channels': caen_data})

with open('сonfig') as file:
    config_data = json.load(file)


poly_1 = Polychromator(poly_number=1, fiber_number=1,
                       config=config_data['equator_caens'][4]['channels'][1:6], expected_table=None,
                       caen_time=all_caens[0]['shots_time'], caen_data=all_caens[0]['caen_channels'][1:6])

poly_2 = Polychromator(poly_number=2, fiber_number=2,
                       config=config_data['equator_caens'][4]['channels'][6:11], expected_table=None,
                       caen_time=all_caens[0]['shots_time'], caen_data=all_caens[0]['caen_channels'][6:11])

poly_3 = Polychromator(poly_number=3, fiber_number=3,
                       config=config_data['equator_caens'][4]['channels'][11:16], expected_table=None,
                       caen_time=all_caens[0]['shots_time'], caen_data=all_caens[0]['caen_channels'][11:16])

poly_4 = Polychromator(poly_number=4, fiber_number=4,
                       config=config_data['equator_caens'][5]['channels'][1:6], expected_table=None,
                       caen_time=all_caens[1]['shots_time'], caen_data=all_caens[1]['caen_channels'][1:6])

poly_5 = Polychromator(poly_number=5, fiber_number=5,
                       config=config_data['equator_caens'][5]['channels'][6:11], expected_table=None,
                       caen_time=all_caens[1]['shots_time'], caen_data=all_caens[1]['caen_channels'][6:11])

poly_6 = Polychromator(poly_number=6, fiber_number=6,
                       config=config_data['equator_caens'][7]['channels'][6:11], expected_table=None,
                       caen_time=all_caens[3]['shots_time'], caen_data=all_caens[3]['caen_channels'][6:11])

poly_7 = Polychromator(poly_number=7, fiber_number=7,
                       config=config_data['equator_caens'][5]['channels'][11:16], expected_table=None,
                       caen_time=all_caens[1]['shots_time'], caen_data=all_caens[1]['caen_channels'][11:16])

poly_8 = Polychromator(poly_number=8, fiber_number=8,
                       config=config_data['equator_caens'][6]['channels'][1:6], expected_table=None,
                       caen_time=all_caens[2]['shots_time'], caen_data=all_caens[2]['caen_channels'][1:6])

poly_9 = Polychromator(poly_number=9, fiber_number=9,
                       config=config_data['equator_caens'][6]['channels'][6:11], expected_table=None,
                       caen_time=all_caens[2]['shots_time'], caen_data=all_caens[2]['caen_channels'][6:11])


poly_2.signal_integrals()

# #
fig, ax = plt.subplots(nrows=5, ncols=1, figsize=(13, 8))
for ch in range(5):
    for shot in range(10,19):
        time, signal = poly_2.get_data(shot_num=shot, ch_num=ch)
        ax[ch].plot(time, signal, label='shot %d' %shot)

plt.tight_layout()
plt.show()