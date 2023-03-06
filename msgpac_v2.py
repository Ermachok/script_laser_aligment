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

def plot_fiber_laser(fiber_num):
    fig, ax = plt.subplots(figsize=(9, 6))

    for shot in range(10):
        # signal_data[shot][:] = [x * 3000/max(laser_data[shot]) for x in signal_data[shot]]
        ax.plot(all_times[fiber_num-1][shot*10], all_laser[fiber_num-1][shot*10], label=r"laser %i".format(shot) % shot, linewidth=0.9)
        ax.plot(all_times[fiber_num-1][shot*10], all_signals[fiber_num-1][shot*10], label=r"signal %i" % shot, linewidth=0.9)
        plt.vlines(60 , 0, 800)
        plt.vlines(20, 0, 800)

    plt.xlim(0, 150)
    ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1),
              ncol=1, borderaxespad=0)

    fig.subplots_adjust(right=0.8)

    ax.grid()
    leg = interactive_legend()
    plt.show()


caen_file_number = '00825'
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
t_step = 0.3125

all_noise = []
all_signals = []
all_times = []
all_laser = []

for iteration, (fib_num, msg_num) in enumerate(config_fiber_poly.items()):
   # print('iteration %d, ' % iteration, 'fiber number %s, ' % fib_num, 'caen num %s, ' % msg_num,
          #'fiber ch in caen %s' % fibers_1_ch[iteration])

    path = Path('C:\TS_data\\10.02.2023\caen_files\%s\%s.msgpk' % (caen_file_number, msg_num))
    with path.open(mode='rb') as file:
        data = msgpack.unpackb(file.read())
        file.close()

    ch_num = fibers_1_ch[iteration]

    signal_data = []
    Pk_Pk_noise_data = []
    laser_max_time = []
    shot_times = []
    laser_data = []
    times = []

    noise_road_len = 480

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

    for shot in range(len(laser_data)):
        time = [100 - laser_max_time[shot] * t_step + t_step * t for t in range(1024)]
        times.append(time)

    all_noise.append(Pk_Pk_noise_data)
    all_signals.append(signal_data)
    all_times.append(times)
    all_laser.append(laser_data)

data.clear()

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

fiber_num = 6
#plot_fiber_laser(fiber_num)

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

for n in n_phe:
    print(n)