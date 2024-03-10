import msgpack
import statistics
import matplotlib.pyplot as plt


class Gains:
    q_e = 1.6E-19
    M_gain = 1E2
    R_gain = 1E4
    G_magic = 2.43
    divider = 0.5
    gain_out = 10
    mV_2_V = 1E-3
    ns_2_s = 1E-9

    full_gain = q_e * M_gain * R_gain * G_magic * divider * gain_out
    converter = mV_2_V * ns_2_s


raman_data_path = r'C:\TS_data\846calib\\'
ophir_data_path = r'ophir_7564_corrected.dat'


fibers_1ch = [1, 6, 11, 1, 6, 6, 11, 1, 6]

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


with open(raman_data_path + r'6.msgpk', 'rb') as msg_file:
    caen_data = msgpack.unpackb(msg_file.read())

with open(raman_data_path + ophir_data_path) as ophir_file:
    ophir_data = ophir_file.readlines()

caen_step = 0.325
ophir_to_J = 0.0275
caen_ch = 6
sig_bord = {'left': 500,
            'right': 600}
noise_count = 400


all_shots = []
for shot in caen_data[:200]:
    signalGround_integral = statistics.mean(shot['ch'][caen_ch][:noise_count]) * (sig_bord['right'] - sig_bord['left'])

    # mV * ns!
    signal_integral = (sum(shot['ch'][caen_ch][sig_bord['left']:sig_bord['right']]) - signalGround_integral) * caen_step
    #Phe
    signalPhe = signal_integral * Gains.converter / Gains.full_gain

    laser_energy = float(ophir_data[caen_data.index(shot)].split()[1]) / ophir_to_J
    signalPhe_to_laser = round(signalPhe / laser_energy, 3)
    all_shots.append(signalPhe_to_laser)
    #print(signalPhe, laser_energy, signalPhe_to_laser)

print(statistics.median(all_shots))