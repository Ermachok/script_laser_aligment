import msgpack
from pathlib import Path
import matplotlib.pyplot as plt

caen_file_number = '43256'
msg_files_num_x10 = [4, 5, 6, 7]

msg_num = 4
#path = Path('C:\TS_data\\10.02.2023\caen_files\%s\%s.msgpk' % (caen_file_number, msg_num))
path = Path('D:\Ioffe\TS\divertor_thomson\measurements\\%s\\%s.msgpk' % (caen_file_number, msg_num))
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

borders_parasite = [32, 51]
borders_signal = []


for caen_channel in range(1, 15):
    fig, ax = plt.subplots(figsize=(9, 6))
    for laser_shot in range(len(times)):
        ax.plot(times[laser_shot], caen_zero_lvl[caen_channel][laser_shot])
    plt.vlines(borders_parasite[0], 0, 100)
    plt.vlines(borders_parasite[1], 0, 100)
    plt.show()

#plt.show()



for laser_shot in range(len(times)):
    t_index = [500, 0]  #500 - потому что знаю, что раньше искать не стоит
    while abs(times[laser_shot][t_index[0]] - borders_parasite[0]) > t_step:
        t_index[0] = t_index[0] + 1

    t_index[1] = t_index[0]
    while abs(times[laser_shot][t_index[1]] - borders_parasite[1]) > t_step:
        t_index[1] = t_index[1] + 1

    parasite_integral = sum(caen_zero_lvl[2][laser_shot][t_index[0]:t_index[1]])
    print(parasite_integral * t_step)


#print('intergated times: ', times[laser_shot][t_index[0]], times[laser_shot][t_index[1]])
print('code ok')