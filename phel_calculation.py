import msgpack
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib
import json
import bisect
from matplotlib.backend_bases import MouseButton


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

        fig, ax = plt.subplots(nrows=3, ncols=1, figsize=(14, 9))

        ax[0].set_xlim(95, 120)
        ax[1].set_xlim(20, 60)
        ax[2].set_xlim(20, 60)

        ax[0].set_title('laser shots', loc = 'left')
        ax[1].set_title('shots before plasma', loc = 'left')
        ax[2].set_title('shots with plasma', loc = 'left')

        laser_lines = []
        for laser_shot in range(shots_before_plasma+shots_in_plasma):
            laser_line, = ax[0].plot(times[laser_shot], caen_zero_lvl[0][laser_shot], label ='shot %d' %laser_shot)
            laser_lines.append(laser_line)

        #print(caen_ch, 'parasite')
        parasite_lines = []
        for laser_shot in range(shots_before_plasma):
            parasite_indices = [bisect.bisect_right(times[laser_shot], parasite_lbord) - 1,
                                bisect.bisect_right(times[laser_shot], parasite_rbord) - 1]

            parasite_integral = sum(caen_zero_lvl[1][laser_shot][parasite_indices[0]:parasite_indices[1]])

            parasite_line, = ax[1].plot(times[laser_shot], caen_zero_lvl[caen_ch][laser_shot], label ='shot %d' %laser_shot)
            parasite_lines.append(parasite_line)
           # print(parasite_integral)

        #print('signal')
        for laser_shot in range(shots_before_plasma, shots_before_plasma + shots_in_plasma):
            signal_indices = [bisect.bisect_right(times[laser_shot], signal_lbord) - 1,
                              bisect.bisect_right(times[laser_shot], signal_rbord) - 1]

            signal_integral = sum(caen_zero_lvl[caen_ch][laser_shot][signal_indices[0]:signal_indices[1]])

            ax[2].plot(times[laser_shot], caen_zero_lvl[caen_ch][laser_shot], label ='shot %d' %laser_shot)
            #print(signal_integral)

        ax[1].vlines(parasite_lbord, 0, 100, 'r', '--')
        ax[1].vlines(parasite_rbord, 0, 100, 'r', '--')

        ax[2].vlines(signal_lbord, 0, 100, 'g', '--')
        ax[2].vlines(signal_rbord, 0, 100, 'g', '--')

        leg0 = ax[0].legend(loc='upper right', ncol = 4, fancybox=True, shadow=True)
        leg1 = ax[1].legend(loc='upper right', ncol = 3, fancybox=True, shadow=True)
        ax[2].legend(loc='upper right', ncol = 4)

        lined = dict()
        for legline, origline in zip(leg0.get_lines(), laser_lines):
            legline.set_picker(5)  # 5 pts tolerance
            lined[legline] = origline

        for legline, origline in zip(leg1.get_lines(), parasite_lines):
            legline.set_picker(5)  # 5 pts tolerance
            lined[legline] = origline

        def onpick(event):
            # on the pick event, find the orig line corresponding to the
            # legend proxy line, and toggle the visibility
            legline = event.artist
            origline = lined[legline]
            vis = not origline.get_visible()
            origline.set_visible(vis)
            # Change the alpha on the line in the legend so we can see what lines
            # have been toggled
            if vis:
                legline.set_alpha(1.0)
            else:
                legline.set_alpha(0.2)
            fig.canvas.draw()

        fig.canvas.mpl_connect('pick_event', onpick)
        plt.show()

discharge_num = '43256'
file = open('D:\Ioffe\TS\divertor_thomson\laser(100Hz)\laser_energy\script\сonfig')
config_data = json.load(file)
file.close()
msg_files_num_x10 = [4, 5, 6, 7]
msg_num = 4
caen_ch_num = 15

shots_before_plasma = 10
shots_in_plasma = 20

#path = Path('C:\TS_data\\10.02.2023\caen_files\%s\%s.msgpk' % (caen_file_number, msg_num))
path = Path('D:\Ioffe\TS\divertor_thomson\measurements\\%s\\%s.msgpk' % (discharge_num, msg_num))

caen_data, times = caen_msg_handler(path)

signal_example_file = open('D:\Ioffe\TS\divertor_thomson\laser(100Hz)\laser_energy\script\signal_example')
example_data = signal_example_file.readlines()
signal_example_file.close()

ex_num = 12

signal_lbord = config_data['equator_caens'][msg_num]['channels'][1]['signal_left_border']
signal_rbord = config_data['equator_caens'][msg_num]['channels'][1]['signal_right_border']
time_indices = [bisect.bisect_right(times[ex_num], signal_lbord) - 1,
                                bisect.bisect_right(times[ex_num], signal_rbord) - 1]

print(signal_lbord, signal_rbord)

for i in range(len(example_data)):
    example_data[i] = float(example_data[i]) * max(caen_data[1][ex_num][time_indices[0]:time_indices[1]])

plt.plot(times[ex_num], caen_data[1][ex_num])
plt.plot(times[ex_num], example_data)
plt.show()

#for i in range(len(example_data)-1):
    #print(caen_data[1][ex_num][i+1] - caen_data[1][ex_num][i], example_data[i+1] - example_data[i])


#plot_signals(msg_num, caen_data, times, shots_before_plasma, shots_in_plasma, config_data)


print('code ok')