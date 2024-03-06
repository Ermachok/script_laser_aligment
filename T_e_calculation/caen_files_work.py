import msgpack
from pathlib import Path


def caen_data(caen_file_number, spectral_channel):
    msg_files_num_x10 = [4, 5, 6, 7]
    msg_files_num_x2 = [0, 1, 2, 3]

    config_fiber_poly = {
        '1': '%d' % msg_files_num_x10[0],
        '2': '%d' % msg_files_num_x10[0],
        '3': '%d' % msg_files_num_x10[0],
        '4': '%d' % msg_files_num_x10[1],
        '5': '%d' % msg_files_num_x10[1],
        '6': '%d' % msg_files_num_x10[3],
        '7': '%d' % msg_files_num_x10[1],
        '8': '%d' % msg_files_num_x10[2],
        '9': '%d' % msg_files_num_x10[2],
    }

    fibers_1_ch = [1, 6, 11, 1, 6, 6, 11, 1, 6]
    fibers_2_ch = [2, 7, 12, 2, 7, 7, 12, 2, 7]
    fibers_3_ch = [3, 8, 13, 3, 8, 8, 13, 3, 8]
    fibers_4_ch = [4, 9, 14, 4, 9, 9, 14, 4, 9]
    fibers_5_ch = [5, 10, 15, 5, 10, 10, 15, 5, 10]
    fiber_channels = [fibers_1_ch, fibers_2_ch, fibers_3_ch, fibers_4_ch, fibers_5_ch]

    t_step = 0.3125

    all_noise = []
    all_signals = []
    all_times = []
    all_laser = []

    for iteration, (fib_num, msg_num) in enumerate(config_fiber_poly.items()):
        # print('iteration %d, ' % iteration, 'fiber number %s, ' % fib_num, 'caen num %s, ' % msg_num,
        # 'fiber ch in caen %s' % fibers_1_ch[iteration])

        path = Path('C:\TS_data\\10.02.2023\caen_files\%s\%s.msgpk' % (caen_file_number, msg_num))
        # path = Path('D:\Ioffe\TS\divertor_thomson\laser(100Hz)\\alignment\\10.02.2023\caen_files\\%s\\%s.msgpk'
        # % (caen_file_number, msg_num))
        # path = Path('D:\Ioffe\TS\divertor_thomson\calibration\\16.06.2023\caen_files\\%s\\%s.msgpk' % (

        # path = Path('D:\Ioffe\TS\divertor_thomson\measurements\\%s\\%s.msgpk' % (caen_file_number, msg_num))
        with path.open(mode='rb') as file:
            data = msgpack.unpackb(file.read())
            file.close()

        caen_ch_num = fiber_channels[spectral_channel - 1][iteration]

        signal_data = []
        Pk_Pk_noise_data = []
        laser_max_time = []
        laser_data = []
        times = []

        noise_road_len = 480

        for shot in range(len(data)):
            laser_data.append(data[shot]['ch'][0])
            laser_max_time.append(laser_data[shot].index(max(laser_data[shot])))
            signal_data.append(data[shot]['ch'][caen_ch_num])

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

        for shot in range(len(laser_data)):
            time = [100 - laser_max_time[shot] * t_step + t_step * t for t in range(1024)]
            times.append(time)

        all_noise.append(Pk_Pk_noise_data)
        all_signals.append(signal_data)
        all_times.append(times)
        all_laser.append(laser_data)

        data.clear()

    return all_times, all_laser, all_signals, all_noise
