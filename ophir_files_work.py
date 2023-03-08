import matplotlib.pyplot as plt

def ophir_data(file_name):
    with open('C:\TS_data\\10.02.2023\\ophir_files\%s.txt' % file_name, 'r') as file:

        ophir_time = []
        ophir_data = []

        i = 0
        for line in file:
            i += 1
            line = line.rstrip().lstrip()
            if i > 36:
                ophir_time.append(float(line.split()[0]))
                ophir_data.append(float(line.split()[1]))
        file.close()

    plt.plot(ophir_time, ophir_data, '-o')
    plt.show()

    clear_ophir_data = []
    times = []

    for shot in range(len(ophir_data)):
        if ophir_data[shot] < 1E-2:
            continue
        else:
            clear_ophir_data.append(ophir_data[shot])
            times.append(ophir_time[shot])

    return times, clear_ophir_data

