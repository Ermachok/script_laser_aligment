import msgpack
from pathlib import Path
import matplotlib.pyplot as plt

caen_file_number = '43256'
msg_files_num_x10 = [4, 5, 6, 7]

msg_num = 4
path = Path('C:\TS_data\\10.02.2023\caen_files\%s\%s.msgpk' % (caen_file_number, msg_num))
with path.open(mode='rb') as file:
    data = msgpack.unpackb(file.read())
    file.close()

noise_len = 400  # counts

caen_zero_lvl = [] # all caen channels zero lvl
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
print('code ok')


t_step = 0.325 #ns
times = []
for laser_shot in range(len(caen_zero_lvl[0])):
    time = [100 - caen_zero_lvl[0][laser_shot].index(max(caen_zero_lvl[0][laser_shot])) * t_step + t_step * t for t in range(1024)]
    times.append(time)

fig, ax = plt.subplots(figsize=(9, 6))

for laser_shot in range(21):
    ax.plot(times[laser_shot], caen_zero_lvl[11][laser_shot])
plt.vlines(42, 0, 300)
plt.vlines(23, 0, 300)
plt.show()