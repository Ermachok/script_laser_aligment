import msgpack
import matplotlib.pyplot as plt
from pathlib import Path


caen_file_number = '00835'
msg_files_num = [4, 5, 6, 7]
config_fiber_poly = {
    '1': '%d' % msg_files_num[0],
    '2': '%d' % msg_files_num[0],
    '3': '%d' % msg_files_num[0],
    '4': '%d' % msg_files_num[1],
    '5': '%d' % msg_files_num[1],
    '6': '%d' % msg_files_num[3],
    '7': '%d' % msg_files_num[1],
    '8': '%d' % msg_files_num[2],
    '9': '%d' % msg_files_num[2],

}
fibers_1_ch = [1, 6, 11, 1, 6, 6, 11, 1, 6]

for iteration, (fib_num, msg_num) in enumerate(config_fiber_poly.items()):
    print('iteration %d, ' % iteration, 'fiber number %s, ' % fib_num, 'caen num %s, ' % msg_num,
          'fiber ch in caen %s' % fibers_1_ch[iteration])

    path = Path('C:\TS_data\%s\%s.msgpk' % (caen_file_number, msg_num))
    with path.open(mode='rb') as file:
        data = msgpack.unpackb(file.read())
        file.close()

    signal_data = []
    ch_num = fibers_1_ch[iteration]
    Pk_Pk_noise_data = []
    laser_max_time = []
    shot_times = []
    noise_road_len = 480

    if int(fib_num) == 1 or int(fib_num) == 4 or int(fib_num) == 6 or int(fib_num) == 8:
        laser_data = []
        for shot in range(len(data)):
            laser_data.append(data[shot]['ch'][0])
            laser_max_time.append(laser_data[shot].index(max(laser_data[shot])))
            signal_data.append(data[shot]['ch'][ch_num])

        for shot in range(len(laser_data)):
            laser_ground = 0
            signal_ground = 0
            for count in range(noise_road_len):
                laser_ground = laser_ground + float(laser_data[shot][count])
                signal_ground = signal_ground + float(signal_data[shot][count])

            laser_data[shot][:] = [float(x) - laser_ground / noise_road_len for x in laser_data[shot]]

            signal_data[shot][:] = [float(x) - signal_ground / noise_road_len for x in signal_data[shot]]
            Pk_Pk_noise_data.append(
                max(signal_data[shot][:noise_road_len]) + abs(min(signal_data[shot][:noise_road_len])))

        laser_max = []

        fig, ax = plt.subplots()
        for shot in range(20):
            # ax.plot(max(laser_data[shot]), max(signal_data[shot]), 'o')
            # plt.xlim(0,1000)
            # plt.ylim(0,1000)
            signal_data[shot][:] = [x * 3000/max(laser_data[shot]) for x in signal_data[shot]]
            time = [100 - laser_max_time[shot] * 0.3125 + 0.3125 * t for t in range(1024)]
            ax.plot(time, laser_data[shot], label=r"laser %i".format(shot) % shot, linewidth=0.9)
            ax.plot(time, signal_data[shot], label=r"signal %i" % shot, linewidth=0.9)

        ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1),
                  ncol=2, borderaxespad=0)
        fig.subplots_adjust(right=0.8)

        ax.grid()
        plt.show()