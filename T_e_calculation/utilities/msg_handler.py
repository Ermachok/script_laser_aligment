import msgpack
import statistics
from pathlib import Path



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
        caen_zero_lvl.append(caen_ch_0lvl)

    for laser_shot in range(processed_shots):
        time = [round(time_shift - caen_zero_lvl[0][laser_shot].index(max(caen_zero_lvl[0][laser_shot])) * t_step +
                      t_step * t, 5) for t in range(1024)]
        times.append(time)

    return times, caen_zero_lvl


def handle_all_caens(discharge_num: str) -> list:
    msg_files_num_x10 = [4, 5, 6, 7]

    all_caens = []
    for msg_num in msg_files_num_x10:
        #path = Path('C:\TS_data\\DTS_summer_2023\%s\%s.msgpk' % (discharge_num, msg_num))
        path = Path('D:\Ioffe\TS\divertor_thomson\measurements\\%s\\%s.msgpk' % (discharge_num, msg_num))
        times, caen_data = caen_msg_handler(path)
        all_caens.append({'caen_num': msg_num,
                          'shots_time': times,
                          'caen_channels': caen_data})

    return all_caens


if __name__ == '__main__':
    print('msg_handler worked')