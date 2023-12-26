import msgpack
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib
import json
import bisect
import numpy as np


def caen_msg_handler(path):
    with path.open(mode='rb') as file:
        data = msgpack.unpackb(file.read())
        file.close()
    noise_len = 400  # counts
    caen_zero_lvl = []  # all caen channels zero lvl
    for caen_channel in range(caen_ch_num):
        caen_ch_0lvl = []
        for laser_shot in range(len(data)):
            signal_lvl = sum(data[laser_shot]['ch'][caen_channel][:noise_len]) / noise_len
            signal_zero_lvl = [float(x) - signal_lvl for x in data[laser_shot]['ch'][caen_channel]]
            caen_ch_0lvl.append(signal_zero_lvl)

            # fig, ax = plt.subplots(figsize=(9, 6))
            # ax.plot(time, signal_zero_lvl)
            # plt.show()
        caen_zero_lvl.append(caen_ch_0lvl)
    t_step = 0.325  # ns
    times = []
    for laser_shot in range(len(caen_zero_lvl[0])):
        time = [100 - caen_zero_lvl[0][laser_shot].index(max(caen_zero_lvl[0][laser_shot])) * t_step + t_step * t
                for t in range(1024)]  # 100 - выбрано случайно
        times.append(time)

    return caen_zero_lvl, times


def plot_signals(msg_num, caen_zero_lvl, times, shots_before_plasma, shots_in_plasma, config_data):

    matplotlib.rcParams['figure.subplot.left'] = 0.05
    matplotlib.rcParams['figure.subplot.bottom'] = 0.06
    matplotlib.rcParams['figure.subplot.right'] = 0.98
    matplotlib.rcParams['figure.subplot.top'] = 0.96

    for caen_ch in range(1, caen_ch_num):
        parasite_lbord = config_data['equator_caens'][msg_num]['channels'][caen_ch]['parasite_left_border']
        parasite_rbord = config_data['equator_caens'][msg_num]['channels'][caen_ch]['parasite_right_border']

        signal_lbord = config_data['equator_caens'][msg_num]['channels'][caen_ch]['signal_left_border']
        signal_rbord = config_data['equator_caens'][msg_num]['channels'][caen_ch]['signal_right_border']

        fig, ax = plt.subplots(nrows=3, ncols=1, figsize=(13, 8))

        ax[0].set_xlim(95, 120)
        ax[1].set_xlim(20, 80)
        ax[2].set_xlim(20, 80)

        ax[0].set_title('laser shots', loc = 'left')
        ax[1].set_title('msg_%d, shots before plasma, caen_ch %d' %(msg_num, caen_ch), loc = 'left')
        ax[2].set_title('msg_%d, shots with plasma, caen_ch %d' %(msg_num, caen_ch), loc = 'left')



        laser_lines = []
        for laser_shot in range(shots_before_plasma+shots_in_plasma):
            laser_line, = ax[0].plot(times[laser_shot], caen_zero_lvl[0][laser_shot], label ='shot %d' %(laser_shot+1))
            laser_lines.append(laser_line)

        #print(caen_ch, 'parasite')
        parasite_lines = []
        for laser_shot in range(shots_before_plasma):
            #parasite_indices = [bisect.bisect_right(times[laser_shot], parasite_lbord) - 1,
                                #bisect.bisect_right(times[laser_shot], parasite_rbord) - 1]

            #parasite_integral = sum(caen_zero_lvl[1][laser_shot][parasite_indices[0]:parasite_indices[1]])

            parasite_line, = ax[1].plot(times[laser_shot], caen_zero_lvl[caen_ch][laser_shot], label ='shot %d' %(laser_shot+1))
            parasite_lines.append(parasite_line)
           # print(parasite_integral)

        #print('signal')
        signal_lines = []
        for laser_shot in range(shots_before_plasma, shots_before_plasma + shots_in_plasma):
            #signal_indices = [bisect.bisect_right(times[laser_shot], signal_lbord) - 1,
                              #bisect.bisect_right(times[laser_shot], signal_rbord) - 1]

            #signal_integral = sum(caen_zero_lvl[caen_ch][laser_shot][signal_indices[0]:signal_indices[1]])

            signal_line, = ax[2].plot(times[laser_shot], caen_zero_lvl[caen_ch][laser_shot], label ='shot %d' %(laser_shot+1))
            signal_lines.append(signal_line)
            #print(signal_integral)

        ax[1].vlines(parasite_lbord, 0, 100, 'r', '--')
        ax[1].vlines(parasite_rbord, 0, 100, 'r', '--')

        ax[2].vlines(signal_lbord, 0, 100, 'g', '--')
        ax[2].vlines(signal_rbord, 0, 100, 'g', '--')

        leg0 = ax[0].legend(loc='upper right', ncol = 4, fancybox=True, shadow=True)
        leg1 = ax[1].legend(loc='upper right', ncol = 3, fancybox=True, shadow=True)
        leg2 = ax[2].legend(loc='upper right', ncol = 4, fancybox=True, shadow=True)

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
            legline = event.artist
            origline = lined[legline]
            x_data = origline.get_xdata().tolist()
            y_data = origline.get_ydata().tolist()
            approx_signal(msg_num, caen_ch, x_data, y_data)
            vis = not origline.get_visible()
            origline.set_visible(vis)
            if vis:
                legline.set_alpha(1.0)
            else:
                legline.set_alpha(0.2)
            fig.canvas.draw()

        fig.canvas.mpl_connect('pick_event', onpick)
        plt.show()


def approx_signal(msg_num, caen_ch, x_data, y_data):
    t_step = 0.325
    q_e = 1.6E-19
    M_gain = 1E2
    R_gain = 1E4
    G_magic = 2.43
    divider = 0.5
    gain_out = 10
    mV_2_V = 1E-3
    ns_2_s = 1E-9

    signal_example_file = open('D:\Ioffe\TS\divertor_thomson\laser(100Hz)\laser_energy\script\signal_example')
    example_data = signal_example_file.readlines()
    example_data = [float(example_data[i]) for i in range(len(example_data))]
    signal_example_file.close()

    signal_lbord = config_data['equator_caens'][msg_num]['channels'][caen_ch]['signal_left_border']
    signal_rbord = config_data['equator_caens'][msg_num]['channels'][caen_ch]['signal_right_border']
    time_indices = [bisect.bisect_right(x_data, signal_lbord) - 1,
                    bisect.bisect_right(x_data, signal_rbord) - 1]

    signal_max_value = max(y_data[time_indices[0]:time_indices[1]])
    index_of_max = y_data.index(signal_max_value)

    index_example_max_value = example_data.index(max(example_data))
    t_start = x_data[index_of_max] - index_example_max_value * t_step
    example_time = [t_start + i * t_step for i in range(1024)]

    for i in range(len(example_data)):
        example_data[i] = float(example_data[i]) * signal_max_value

    noise_amplitude = noise_amplitude_subrout(y_data)
    print('Noise amplitude {} '.format(noise_amplitude))

    A = q_e * M_gain * R_gain * G_magic * divider * gain_out

    integral_borders_indices = [500, 560]
    integration_time = (integral_borders_indices[1] - integral_borders_indices[0]) * t_step

    noise_Phe = noise_amplitude * integration_time * mV_2_V * ns_2_s / A
    signal_Phe = sum(example_data[integral_borders_indices[0]: integral_borders_indices[1]]) * t_step * mV_2_V * ns_2_s / A

    #for i in range(1024):
        #print(y_data[i])

    print('signal {}, noise {} '.format(signal_Phe, noise_Phe))

    plt.subplots(figsize=(10, 5))
    plt.plot(x_data, y_data)
    plt.plot(example_time, example_data, '--')
    plt.xlim([0, 120])
    plt.show()


def noise_amplitude_subrout(y_data):
    # bins_ = [-10 + i * 0.3 for i in range(70)]
    # hist, bins = np.histogram(y_data, bins=bins_)
    # #print(hist, bins)
    # cort = dict(zip(hist, bins))
    # hist = sorted(hist)
    # #print(hist, bins)
    # sum_counts = 0
    # count_bins = 0
    # noise_width = 0
    # while sum_counts < 700:
    #     sum_counts += hist[len(hist) - 1 - count_bins]
    #     noise_width += abs(cort[hist[len(hist) - 1 - count_bins]])
    #     count_bins += 1
    # for y in y_data[:400]:
    #     print(y)
    # #print(bins[count_bins-1])
    # #print(sum_counts, count_bins)
    noise_count = 400
    mean_noise = sum(y_data[:noise_count])/noise_count
    std = 0
    for count in y_data[:noise_count]:
        std += (count - mean_noise)**2
    noise_width = (std/noise_count)**0.5
    return noise_width


discharge_num = '43256'
file = open('D:\Ioffe\TS\divertor_thomson\laser(100Hz)\laser_energy\script\сonfig')
config_data = json.load(file)
file.close()
msg_files_num_x10 = [4, 5, 6, 7]
msg_num = 4
caen_ch_num = 16

shots_before_plasma = 10
shots_in_plasma = 20

#path = Path('C:\TS_data\\10.02.2023\caen_files\%s\%s.msgpk' % (caen_file_number, msg_num))
path = Path('D:\Ioffe\TS\divertor_thomson\measurements\\%s\\%s.msgpk' % (discharge_num, msg_num))

caen_data, times = caen_msg_handler(path)

#approx_signal()

#for i in range(len(example_data)-1):
    #print(caen_data[1][ex_num][i+1] - caen_data[1][ex_num][i], example_data[i+1] - example_data[i])


plot_signals(msg_num, caen_data, times, shots_before_plasma, shots_in_plasma, config_data)

print('code ok')