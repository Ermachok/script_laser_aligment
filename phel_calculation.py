import msgpack
from pathlib import Path
import matplotlib.pyplot as plt
import json
import bisect

file = open('D:\Ioffe\TS\divertor_thomson\laser(100Hz)\laser_energy\script\сonfig')
config_data = json.load(file)

discharge_num = '43256'
msg_files_num_x10 = [4, 5, 6, 7]

msg_num = 4
#path = Path('C:\TS_data\\10.02.2023\caen_files\%s\%s.msgpk' % (caen_file_number, msg_num))
path = Path('D:\Ioffe\TS\divertor_thomson\measurements\\%s\\%s.msgpk' % (discharge_num, msg_num))
with path.open(mode='rb') as file:
    data = msgpack.unpackb(file.read())
    file.close()

noise_len = 400  # counts
caen_zero_lvl = []  #all caen channels zero lvl
for caen_channel in range(15):
    caen_ch_0lvl = []
    for laser_shot in range(len(data)):
        signal_lvl = sum(data[laser_shot]['ch'][caen_channel][:noise_len]) / noise_len
        signal_zero_lvl = [float(x) - signal_lvl for x in data[laser_shot]['ch'][caen_channel]]
        caen_ch_0lvl.append(signal_zero_lvl)

        #fig, ax = plt.subplots(figsize=(9, 6))
        #ax.plot(time, signal_zero_lvl)
        #plt.show()
    caen_zero_lvl.append(caen_ch_0lvl)


t_step = 0.325 #ns
times = []
for laser_shot in range(len(caen_zero_lvl[0])):
    time = [100 - caen_zero_lvl[0][laser_shot].index(max(caen_zero_lvl[0][laser_shot])) * t_step + t_step * t
            for t in range(1024)]   # 100 - выбрано случайно
    times.append(time)

for caen_ch in range(15):

    parasite_lbord = config_data['equator_caens'][0]['channels'][caen_ch]['parasite_left_border']
    parasite_rbord = config_data['equator_caens'][0]['channels'][caen_ch]['parasite_right_border']

    signal_lbord = config_data['equator_caens'][0]['channels'][caen_ch]['signal_left_border']
    signal_rbord = config_data['equator_caens'][0]['channels'][caen_ch]['signal_right_border']


    shots_before_plasma = 10
    print(caen_ch)
    for laser_shot in range(len(times)):

        parasite_indices = [bisect.bisect_right(times[laser_shot], parasite_lbord) - 1,
                            bisect.bisect_right(times[laser_shot], parasite_rbord) - 1]

        signal_indices = [bisect.bisect_right(times[laser_shot], signal_lbord) - 1,
                            bisect.bisect_right(times[laser_shot], signal_rbord) - 1]

        parasite_integral = sum(caen_zero_lvl[1][laser_shot][parasite_indices[0]:parasite_indices[1]])
        signal_integral = sum(caen_zero_lvl[1][laser_shot][signal_indices[0]:signal_indices[1]])

        print(parasite_integral, signal_integral)

    fig, ax = plt.subplots(figsize=(9, 6))
    # for laser_shot in range(len(times)):
    for laser_shot in range(len(times)):
        ax.plot(times[laser_shot], caen_zero_lvl[caen_ch][laser_shot])

    plt.vlines(parasite_lbord, 0, 200, 'r', '--')
    plt.vlines(parasite_rbord, 0, 200, 'r', '--')

    plt.vlines(signal_lbord, 0, 200, 'g', '--')
    plt.vlines(signal_rbord, 0, 200, 'g', '--')

    plt.xlim([20, 120])

    plt.show()


print('code ok')