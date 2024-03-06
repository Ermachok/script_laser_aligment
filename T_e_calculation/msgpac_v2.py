import ophir_files_work
from main import caen_files_work, plots
import time

start = time.time()
caen_file_number = '43256'
ophir_file_name = '534475_68'


def ophir(ophir_fname):
    ophir_data = ophir_files_work.ophir_data(ophir_fname)
    ophir_time = ophir_data[0]
    ophir_signal = ophir_data[1]

    del ophir_data
    for i in range(len(ophir_signal)):
        print(ophir_signal[i])

    return ophir_time, ophir_signal


fiber_num = 1
spectral_channel = 1

caen_data = caen_files_work.caen_data(caen_file_number, spectral_channel)

caen_times = caen_data[0]
caen_laser = caen_data[1]
caen_signals = caen_data[2]
caen_noise = caen_data[3]

del caen_data

plots.fiber_laser(fiber_num, caen_times, caen_laser, caen_signals)

q_e = 1.6E-19
M_gain = 1E2
R_gain = 1E4
G_magic = 2.43
divider = 0.5
gain_out = 10
mV_2_V = 1E-3
ns_2_s = 1E-9

ev_ns = []
A = q_e * M_gain * R_gain * G_magic * divider * gain_out

'''
for shot in range(len(all_signals[fiber_num-1])):
    fiber = fiber_num - 1

    start_time = 20
    end_time = 55

    integral = 0
    for ind in range(all_times[fiber][shot].index(start_time), all_times[fiber][shot].index(end_time)):
        integral += all_signals[fiber][shot][ind]
    ev_ns.append(integral * t_step)

n_phe = ev_ns
n_phe[:] = [x * mV_2_V * ns_2_s / A for x in n_phe]
'''
