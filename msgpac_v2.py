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
        for artist in self.legend.texts + self.legend.legendHandles:
            artist.set_picker(10)  # 10 points tolerance

        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

    def _build_lookups(self, legend):
        labels = [t.get_text() for t in legend.texts]
        handles = legend.legendHandles
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
    print('iteration %d, '%iteration,'fiber number %s, ' %fib_num, 'caen num %s, ' %msg_num,'fiber ch in caen %s' %fibers_1_ch[iteration])

    path = Path('D:\Ioffe\TS\divertor_thomson\laser(100Hz)\\alignment\\10.02.2023\caen_files\\%s\\%s.msgpk'% (caen_file_number, msg_num))
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

        for shot in range(len(laser_data)):
            laser_ground = 0
            for i in range(noise_road_len):
                laser_ground = laser_ground + float(laser_data[shot][i])
            laser_data[shot][:] = [float(x) - laser_ground / noise_road_len for x in laser_data[shot]]

        laser_max = []

        for shot in range(len(data)):
            signal_data.append(data[shot]['ch'][ch_num])

        for shot in range(len(signal_data)):
            ground = 0
            for count in range(noise_road_len):
                ground = ground + float(signal_data[shot][count])
            signal_data[shot][:] = [float(x) - ground / noise_road_len for x in signal_data[shot]]
            Pk_Pk_noise_data.append(max(signal_data[shot][:noise_road_len]) + abs(min(signal_data[shot][:noise_road_len])))

        fig, ax = plt.subplots()
        for shot in range(20):
            #ax.plot(max(laser_data[shot]), max(signal_data[shot]), 'o')
            #plt.xlim(0,1000)
            #plt.ylim(0,1000)
            #signal_data[shot][:] = [x * 3000/max(laser_data[shot]) for x in signal_data[shot]]
            time = [100 - laser_max_time[shot] * 0.3125 + 0.3125 * t for t in range(1024)]
            ax.plot(time, laser_data[shot], label=r"laser %i".format(shot) % shot, linewidth=0.9)
            ax.plot(time, signal_data[shot], label=r"signal %i" % shot, linewidth=0.9)

        ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1),
                  ncol=2, borderaxespad=0)
        fig.subplots_adjust(right=0.8)

        leg = interactive_legend()
        ax.grid()
        plt.show()
