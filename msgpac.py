import msgpack
import matplotlib.pyplot as plt
from pathlib import Path


def interactive_legend(ax=None):
    if ax is None:
        ax = plt.gca()
    if ax.legend_ is None:
        ax.legend()

    return InteractiveLegend(ax.get_legend())


class InteractiveLegend(object):
    def __init__(self, legend):
        self.legend = legend
        self.fig = legend.axes.figure

        self.lookup_artist, self.lookup_handle = self._build_lookups(legend)
        self._setup_connections()

        self.update()

    def _setup_connections(self):
        for artist in self.legend.texts + self.legend.legend_handles:
            artist.set_picker(10)  # 10 points tolerance

        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

    def _build_lookups(self, legend):
        labels = [t.get_text() for t in legend.texts]
        handles = legend.legend_handles
        label2handle = dict(zip(labels, handles))
        handle2text = dict(zip(handles, legend.texts))

        lookup_artist = {}
        lookup_handle = {}
        for artist in legend.axes.get_children():
            if artist.get_label() in labels:
                handle = label2handle[artist.get_label()]
                lookup_handle[artist] = handle
                lookup_artist[handle] = artist
                lookup_artist[handle2text[handle]] = artist

        lookup_handle.update(zip(handles, handles))
        lookup_handle.update(zip(legend.texts, handles))

        return lookup_artist, lookup_handle

    def on_pick(self, event):
        handle = event.artist
        if handle in self.lookup_artist:
            artist = self.lookup_artist[handle]
            artist.set_visible(not artist.get_visible())
            self.update()

    def on_click(self, event):
        if event.button == 3:
            visible = False
        elif event.button == 2:
            visible = True
        else:
            return

        for artist in self.lookup_artist.values():
            artist.set_visible(visible)
        self.update()

    def update(self):
        for artist in self.lookup_artist.values():
            handle = self.lookup_handle[artist]
            if artist.get_visible():
                handle.set_visible(True)
            else:
                handle.set_visible(False)
        self.fig.canvas.draw()

    def show(self):
        plt.show()


caen_file_number = '00825'
#caen_file_number = '43256'
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
fibers_2_ch = [2, 7, 12, 2, 7, 7, 12, 2, 7]
fibers_3_ch = [3, 8, 13, 3, 8, 8, 13, 3, 8]
fibers_4_ch = [4, 9, 14, 4, 9, 9, 14, 4, 9]
fibers_5_ch = [5, 10, 15, 5, 10, 10, 15, 5, 10]
fiber_channels = [fibers_1_ch, fibers_2_ch, fibers_3_ch, fibers_4_ch, fibers_5_ch]

all_integrals = []
Pk_Pk_all_noise = []

all_caen_laser = []

q_e = 1.6E-19
M_gain = 1E2
R_gain = 1E4
G_magic = 2.43
divider = 0.5
gain_out = 10
mV_2_V = 1E-3
ns_2_s = 1E-9

spectral_ch = 1

for iteration, (fib_num, msg_num) in enumerate(config_fiber_poly.items()):
    print('iteration %d, '%iteration,'fiber number %s, ' %fib_num, 'caen num %s, ' %msg_num, 'spec_ch%s, ' %(spectral_ch),
          'fiber ch in caen %s' % fiber_channels[spectral_ch-1][iteration])

    path = Path('D:\Ioffe\TS\divertor_thomson\calibration\\10.02.2023\caen_files\\%s\\%s.msgpk'% (caen_file_number, msg_num))
    #path = Path('D:\Ioffe\TS\divertor_thomson\measurements\%s\\%s.msgpk' % (caen_file_number, msg_num))
    with path.open(mode='rb') as file:
        data = msgpack.unpackb(file.read())
        file.close()

    #print(len(data))

    signal_data = []
    ch_num = fiber_channels[spectral_ch - 1][iteration]
    Pk_Pk_noise_data = []
    x_ar = [ind * 0.3125 for ind in range(1024)]

    noise_road_len = 480

    if int(fib_num) == 1 or int(fib_num) == 4 or int(fib_num) == 6 or int(fib_num) == 8:
        laser_data = []
        for shot in range(1, len(data)):
            laser_data.append(data[shot]['ch'][0])

        for j in range(len(laser_data)):
            laser_ground = 0
            for i in range(noise_road_len):
                laser_ground = laser_ground + float(laser_data[j][i])
            #print(laser_ground/noise_road_len)
            laser_data[j][:] = [float(x) - laser_ground / noise_road_len for x in laser_data[j]]

        #with open('D:\Ioffe\TS\divertor_thomson\measurements\\%s\\%s_laser_msg_%s.csv'
        with open('D:\Ioffe\TS\divertor_thomson\calibration\\10.02.2023\caen_files\\%s\\%s_laser_msg_%s.csv'
                % (caen_file_number, caen_file_number, msg_num), 'w') as file:
            for i in range(len(laser_data[ch_num])):
                raw = '%.4f, ' % x_ar[i]
                for j in range(len(laser_data)):
                    raw = raw + '%.3f, ' % (laser_data[j][i])
                file.write(raw + '\n')
            file.close()

        laser_max = []

        for k in range(len(laser_data)):
            laser_max.append(max(laser_data[k]))

        with open('D:\Ioffe\TS\divertor_thomson\calibration\\10.02.2023\caen_files\\%s\\%s_rel_laser_max_msg%s.csv'
                % (caen_file_number, caen_file_number, msg_num), 'w') as file:
            for l in range(len(laser_max)):
                row = '%d, %f' % (l, laser_max[l] / max(laser_max))
                file.write(row + '\n')
            file.close()

    for shot in range(1, len(data)):
        signal_data.append(data[shot]['ch'][ch_num])

    for j in range(len(signal_data)):
        ground = 0
        for i in range(noise_road_len):
            ground = ground + float(signal_data[j][i])
        signal_data[j][:] = [float(x) - ground / noise_road_len for x in signal_data[j]]
        Pk_Pk_noise_data.append(max(signal_data[j][:noise_road_len]) + abs(min(signal_data[j][:noise_road_len])))


    borders = [480, 640]
    fig, ax = plt.subplots()
    for i in range(20):
        ax.plot(x_ar, laser_data[i], label=r"laser %i".format(i) % (i), linewidth=0.9)
        ax.plot(x_ar, signal_data[i], label=r"signal %i" % (i), linewidth=0.9)
       # if int(fib_num) == 1:
            #ax.plot(x_ar[laser_data[i].index(max(laser_data[i]))], max(laser_data[i]), 'o')
            #ax.plot(x_ar[signal_data[i].index(max(signal_data[i]))], max(signal_data[i]), 'o')

    plt.vlines(x_ar[borders[0]], 0, 300)
    plt.vlines(x_ar[borders[1]], 0, 300)
    ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1),
              ncol=2, borderaxespad=0)
    fig.subplots_adjust(right=0.8)

    #leg = interactive_legend()
    ax.grid()
    plt.show()

    with open('D:\Ioffe\TS\divertor_thomson\calibration\\10.02.2023\caen_files\\%s\\%s_%sch_fib%s.csv'
              % (caen_file_number, caen_file_number, spectral_ch, fib_num), 'w') as file:
        for sht_num in range(len(signal_data)):
            if sht_num == len(signal_data):
                file.write('%d\n' %(sht_num+1))
            else:
                file.write('%d,' %(sht_num+1))

        file.write('\n')
        for i in range(len(signal_data[ch_num])):
            row = '%f, ' % x_ar[i]
            for j in range(len(signal_data)):
                row = row + '%.3f, ' % (signal_data[j][i])
            file.write(row + '\n')
        file.close()

    integrals = []
    for j in range(len(signal_data)):
        sum = 0
        for i in range(borders[0], borders[1]):
            sum += signal_data[j][i]
        sum += signal_data[j][borders[0]] / 2 + signal_data[j][borders[1]] / 2
        ans = sum * x_ar[1]
        integrals.append(ans)

    A = q_e * M_gain * R_gain * G_magic * divider * gain_out
    integrals[:] = [x * mV_2_V * ns_2_s / A for x in integrals]

    all_integrals.append(integrals)
    Pk_Pk_all_noise.append(Pk_Pk_noise_data)

with open('D:\Ioffe\TS\divertor_thomson\calibration\\10.02.2023\caen_files\\%s\\%sch_scat_Nphe_%s.csv'
          % (caen_file_number, spectral_ch, caen_file_number), 'w') as file:
    row = 'sht num, '
    for j in range(len(all_integrals)):
        row += 'fib_%d, ' % (j + 1)
    file.write(row + '\n')
    for i in range(len(all_integrals[0])):
        row = '%d, ' %(i+1)
        for j in range(len(all_integrals)):
            row += '%f, ' % all_integrals[j][i]
        file.write(row + '\n')
    file.close()

with open('D:\Ioffe\TS\divertor_thomson\calibration\\10.02.2023\caen_files\\%s\\%sch_Pk_Pk_noise_mV_%s.csv'
          % (caen_file_number, spectral_ch, caen_file_number), 'w') as file:
    row = 'sht num, '
    for j in range(len(Pk_Pk_all_noise)):
        row += 'fib_%d, ' % (j + 1)
    file.write(row + '\n')
    for i in range(len(Pk_Pk_all_noise[0])):
        row = '%d, ' % i
        for j in range(len(Pk_Pk_all_noise)):
            row += '%f, ' % Pk_Pk_all_noise[j][i]
        file.write(row + '\n')
    file.close()

print('Code OK')
