import matplotlib.pyplot as plt


def normalize_ophir_fpu(ophir_time, ophir_signal, caen_laser):
    fig, ax = plt.subplots(figsize=(9, 6))
    sht_count = [x for x in range(len(ophir_time))]

    max_las = []
    for shot in caen_laser:
        max_las.append(max(shot))
    max_las[:] = [sht / max(max_las) for sht in max_las]

    max_ophir = []
    max_ophir[:] = [x / max(ophir_signal) for x in ophir_signal]

    ax.plot(sht_count[:len(max_las)], max_las, '-o', label='ФПУ', linewidth=0.9)
    ax.plot(sht_count, max_ophir, '-o', label='ophir', linewidth=0.9)

    fig.subplots_adjust(right=1)
    ax.legend()
    ax.grid()
    plt.show()


def ophir_fpu(ophir_signal, caen_laser):

    fig, ax = plt.subplots(figsize=(9, 6))
    caen_laser_max = []

    for shot in caen_laser:
        caen_laser_max.append(sum(shot) * 0.3125)

    ax.plot(ophir_signal, caen_laser_max, '.', linewidth=0.9)

    #for i in range(len(ophir_signal)):
        #print(ophir_signal[i], caen_laser_max[i] )

    plt.xlim(0, max(ophir_signal) + max(ophir_signal) * 0.05 )
    plt.ylim(0, max(caen_laser_max) + max(caen_laser_max) * 0.05)

    plt.xlabel('ophir')
    plt.ylabel('mV * ns, fpu')

    ax.grid()
    plt.show()


def fiber_laser(fiber_num, caen_times, caen_laser, caen_signals):

    fig, ax = plt.subplots(figsize=(9, 6))
    for shot in range(len(caen_signals[fiber_num-1])):
    #for shot in range(1):
        # signal_data[shot][:] = [x * 3000/max(laser_data[shot]) for x in signal_data[shot]]
        ax.plot(caen_times[fiber_num - 1][shot], caen_signals[fiber_num - 1][shot], linewidth=0.9)
        ax.plot(caen_times[fiber_num - 1][shot], caen_laser[fiber_num - 1][shot], linewidth=0.9)

    plt.vlines(60, 0, 500)
    plt.vlines(20, 0, 500)
    plt.xlabel('ns')
    plt.ylabel('mV')

    #plt.xlim(0, 150)
    ax.grid()
    plt.show()


