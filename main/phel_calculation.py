import msgpack
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib
import json
import bisect


def caen_msg_handler(path, t_step=0.325, time_shift=100, noise_len=400, processed_shots=35):
    """
    :param path:путь до файла
    :param t_step: шаг оцифровщика
    :param noise_len: длина для вычисления уровня над нулем и уровня шума
    :param processed_shots: количество обработанных выстрелов
    :time_shift: сдвиг для построения в одной системе координат
    :return:
    """

    times = []
    caen_zero_lvl = []

    with path.open(mode='rb') as file:
        data = msgpack.unpackb(file.read())
        file.close()

    for caen_channel in range(number_of_caen_channels):
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


def plot_signals(msg_num=None, caen_data=None, times=None,
                 config_data=None, shots_before_plasma=10, shots_in_plasma=15, plot_limits=True):
    matplotlib.rcParams['figure.subplot.left'] = 0.05
    matplotlib.rcParams['figure.subplot.bottom'] = 0.06
    matplotlib.rcParams['figure.subplot.right'] = 0.98
    matplotlib.rcParams['figure.subplot.top'] = 0.96

    for caen_ch in range(1, number_of_caen_channels):
        parasite_lbord = config_data['equator_caens'][msg_num]['channels'][caen_ch]['pest_LeftBord']
        parasite_rbord = config_data['equator_caens'][msg_num]['channels'][caen_ch]['pest_RightBord']

        signal_lbord = config_data['equator_caens'][msg_num]['channels'][caen_ch]['sig_LeftBord']
        signal_rbord = config_data['equator_caens'][msg_num]['channels'][caen_ch]['sig_RightBord']

        fig, ax = plt.subplots(nrows=3, ncols=1, figsize=(13, 8))

        if plot_limits:
            ax[0].set_xlim(95, 120)
            ax[1].set_xlim(0, 80)
            ax[2].set_xlim(0, 80)

        ax[0].set_title('laser shots', loc='left')
        ax[1].set_title('msg_%d, shots before plasma, caen_ch %d' % (msg_num, caen_ch), loc='left')
        ax[2].set_title('msg_%d, shots with plasma, caen_ch %d' % (msg_num, caen_ch), loc='left')

        laser_lines = []
        for laser_shot in range(shots_before_plasma + shots_in_plasma):
            laser_line, = ax[0].plot(times[laser_shot], caen_data[0][laser_shot],
                                     label='shot %d' % (laser_shot + 1))
            laser_lines.append(laser_line)

        # print(caen_ch, 'parasite')
        parasite_lines = []
        for laser_shot in range(shots_before_plasma):
            # parasite_indices = [bisect.bisect_right(times[laser_shot], parasite_lbord) - 1,
            # bisect.bisect_right(times[laser_shot], parasite_rbord) - 1]

            # parasite_integral = sum(caen_zero_lvl[1][laser_shot][parasite_indices[0]:parasite_indices[1]])

            parasite_line, = ax[1].plot(times[laser_shot], caen_data[caen_ch][laser_shot],
                                        label='shot %d' % (laser_shot + 1))
            parasite_lines.append(parasite_line)
        # print(parasite_integral)

        # print('signal')
        signal_lines = []
        for laser_shot in range(shots_before_plasma, shots_before_plasma + shots_in_plasma):
            # signal_indices = [bisect.bisect_right(times[laser_shot], signal_lbord) - 1,
            # bisect.bisect_right(times[laser_shot], signal_rbord) - 1]

            # signal_integral = sum(caen_zero_lvl[caen_ch][laser_shot][signal_indices[0]:signal_indices[1]])

            signal_line, = ax[2].plot(times[laser_shot], caen_data[caen_ch][laser_shot],
                                      label='shot %d' % (laser_shot + 1))
            signal_lines.append(signal_line)
            # print(signal_integral)

        ax[1].vlines(parasite_lbord, 0, 100, 'r', '--')
        ax[1].vlines(parasite_rbord, 0, 100, 'r', '--')

        ax[2].vlines(signal_lbord, 0, 100, 'g', '--')
        ax[2].vlines(signal_rbord, 0, 100, 'g', '--')

        leg0 = ax[0].legend(loc='upper right', ncol=4, fancybox=True, shadow=True)
        leg1 = ax[1].legend(loc='upper right', ncol=3, fancybox=True, shadow=True)
        leg2 = ax[2].legend(loc='upper right', ncol=4, fancybox=True, shadow=True)

        lined = dict()
        for legline, origline in zip(leg0.get_lines(), laser_lines):
            legline.set_picker(5)  # 5 pts tolerance
            lined[legline] = origline

        for legline, origline in zip(leg1.get_lines(), parasite_lines):
            legline.set_picker(5)  # 5 pts tolerance
            lined[legline] = origline

        for legline, origline in zip(leg2.get_lines(), signal_lines):
            legline.set_picker(5)  # 5 pts tolerance
            lined[legline] = origline

        def onpick(event):

            parasite_example = [i / max(caen_data[caen_ch][3]) for i in caen_data[caen_ch][3]]
            # 3 - случайный, главное, чтобы до плазмы

            legline = event.artist
            origline = lined[legline]
            x_data = origline.get_xdata().tolist()
            y_data = origline.get_ydata().tolist()
            approx_signal(msg_num, caen_ch, x_data, y_data, parasite_example)
            vis = not origline.get_visible()
            origline.set_visible(vis)
            if vis:
                legline.set_alpha(1.0)
            else:
                legline.set_alpha(0.2)
            fig.canvas.draw()

        fig.canvas.mpl_connect('pick_event', onpick)
        plt.show()


def approx_signal(msg_num, caen_ch, signal_time, signal_data, parasite_example, t_step=0.325):
    q_e = 1.6E-19
    M_gain = 1E2
    R_gain = 1E4
    G_magic = 2.43
    divider = 0.5
    gain_out = 10
    mV_2_V = 1E-3
    ns_2_s = 1E-9

    # with open('D:\Ioffe\TS\divertor_thomson\laser(100Hz)\laser_energy\script\signal_example') as signal_example_file:
    with open('signal_example') as signal_example_file:
        example_data = signal_example_file.readlines()
        example_data = [float(example_data[i]) for i in range(len(example_data))]

    signal_lbord = config_data['equator_caens'][msg_num]['channels'][caen_ch]['sig_LeftBord']
    signal_rbord = config_data['equator_caens'][msg_num]['channels'][caen_ch]['sig_RightBord']
    signal_time_indices = [bisect.bisect_left(signal_time, signal_lbord),
                           bisect.bisect_right(signal_time, signal_rbord)]

    parasite_lbord = config_data['equator_caens'][msg_num]['channels'][caen_ch]['pest_LeftBord']
    parasite_rbord = config_data['equator_caens'][msg_num]['channels'][caen_ch]['pest_RightBord']
    parasite_time_indices = [bisect.bisect_left(signal_time, parasite_lbord),
                             bisect.bisect_right(signal_time, parasite_rbord)]

    signal_max_value = max(signal_data[signal_time_indices[0]:signal_time_indices[1]])
    parasite_max_value = max(signal_data[parasite_time_indices[0]:parasite_time_indices[1]])

    index_of_max_signal = signal_data.index(signal_max_value)
    index_of_max_parasite = signal_data.index(parasite_max_value)

    index_example_max_value = example_data.index(max(example_data))

    t_start_signal = signal_time[index_of_max_signal] - index_example_max_value * t_step
    t_start_parasite = signal_time[index_of_max_parasite] - index_example_max_value * t_step

    example_for_parasite_time = [t_start_parasite + i * t_step for i in range(1024)]
    example_for_signal_time = [t_start_signal + i * t_step for i in range(1024)]

    difference_in_time = round((example_for_parasite_time[0] - example_for_signal_time[0]) / t_step)
    # difference_in_time = 0

    signal_example_data = []
    parasite_example_data = []

    for i in range(len(example_data)):
        # example_data[i] = float(example_data[i]) * signal_max_value
        signal_example_data.append(float(example_data[i]) * signal_max_value)
        parasite_example_data.append(float(parasite_example[i]) * parasite_max_value)

    signal_parasite_both = [signal_example_data[i] + parasite_example_data[i]
                            for i in range(len(signal_example_data))]

    noise_amplitude = noise_amplitude_subroutine(signal_data)
    print('Noise amplitude {} '.format(noise_amplitude))

    A = q_e * M_gain * R_gain * G_magic * divider * gain_out

    integral_borders_indices = [500, 560]
    integration_time = (integral_borders_indices[1] - integral_borders_indices[0]) * t_step

    noise_Phe = noise_amplitude * integration_time * mV_2_V * ns_2_s / A
    signal_Phe = sum(
        example_data[integral_borders_indices[0]: integral_borders_indices[1]]) * t_step * mV_2_V * ns_2_s / A

    # print('signal {} eV, noise {} eV '.format(signal_Phe, noise_Phe))

    plt.subplots(figsize=(10, 5))
    plt.plot(signal_time, signal_data)
    plt.plot(example_for_signal_time, signal_example_data, '--')
    plt.plot(example_for_parasite_time[:-difference_in_time], parasite_example_data[difference_in_time:], '-')
    plt.plot(example_for_signal_time, signal_parasite_both, '.')
    plt.xlim([0, 120])
    plt.show()


def noise_amplitude_subroutine(y_data):
    noise_count = 400
    mean_noise = sum(y_data[:noise_count]) / noise_count
    std = 0
    for count in y_data[:noise_count]:
        std += (count - mean_noise) ** 2
    noise_width = (std / noise_count) ** 0.5
    return noise_width


with open('сonfig') as file:
    config_data = json.load(file)

# path = Path('C:\TS_data\\DTS_summer_2023\%s\%s.msgpk' % (discharge_num, msg_num))
# path = Path('C:\TS_data\\10.02.2023\caen_files\%s\%s.msgpk' % (caen_file_number, msg_num))
# path = Path('D:\Ioffe\TS\divertor_thomson\measurements\\%s\\%s.msgpk' % (discharge_num, msg_num))

msg_files_num_x10 = [4, 5, 6, 7]
number_of_caen_channels = 16

discharge_num = '43256'
caen_file_number = '00825'
all_caens = []

for msg_num in msg_files_num_x10:
    # path = Path('C:\TS_data\\DTS_summer_2023\%s\%s.msgpk' % (discharge_num, msg_num))
    path = Path('D:\Ioffe\TS\divertor_thomson\measurements\\%s\\%s.msgpk' % (discharge_num, msg_num))
    times, caen_data = caen_msg_handler(path)
    all_caens.append({'caen_num': msg_num,
                      'shots_time': times,
                      'caen_channels': caen_data})

# for ch in range(number_of_caen_channels):
#     for shot in range(len(all_caens[0]['shots_time'])):
#         print(ch, shot, sum(all_caens[0]['caen_channels'][ch][shot]))
#     print('-' * 20)

# fig, ax = plt.subplots(figsize=(9, 6))
# ax.plot(all_caens[0]['shots_time'][11], all_caens[0]['caen_channels'][1][11])
# plt.show()
for msg_num in msg_files_num_x10:
    plot_signals(msg_num=msg_num, caen_data=all_caens[msg_num - 4]['caen_channels'],
                 times=all_caens[msg_num - 4]['shots_time'], config_data=config_data)

print('code ok')
