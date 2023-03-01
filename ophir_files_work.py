import matplotlib.pyplot as plt

def ophir_rel2max(file_name:str) -> list:
    #files_number = ['534475_16']

    with open('D:/Ioffe/TS/divertor_thomson/laser(100Hz)/laser_energy/31.01.2023/ophir_files/%s.txt' %file_name, 'r') as file:
        ophir_data = file.readlines()
        file.close()

    sht_energy = []

    for i in range(36, len(ophir_data)):
        #print(i, float(ophir_data[i].lstrip().split('  ')[1]))
        sht_energy.append(float(ophir_data[i].lstrip().split('  ')[1]))

    rel_2_max = sht_energy
    rel_2_max[:] = [x / max(rel_2_max) for x in rel_2_max]
    print('ophir done')

    return(rel_2_max)


def ophir_data(file_name:str) -> list:
    #files_number = ['534475_16']

    with open('D:\Ioffe\TS\divertor_thomson\laser(100Hz)\\alignment\\10.02.2023\ophir_files/%s.txt' %file_name, 'r') as file:
        ophir_data = file.readlines()
        file.close()

    sht_energy = []
    ophir_time = []
    for i in range(36, len(ophir_data)):
        #print(i, float(ophir_data[i].lstrip().split('  ')[1]))
        sht_energy.append(float(ophir_data[i].lstrip().split('  ')[1]))
        ophir_time.append(float(ophir_data[i].lstrip().split('  ')[0]))

    sht_energy = sht_energy[2:]
    ophir_time = ophir_time[2:]
    #rel_2_max = sht_energy
    #rel_2_max[:] = [x / max(rel_2_max) for x in rel_2_max]

    fig, ax = plt.subplots()
    x_ar = [i for i in range(len(sht_energy))]

    ax.plot(ophir_time, sht_energy, '.-', label=r"laser_energy")
    #ax.plot(x_ar,ophir_time, '.-', label=r"laser_energy")
    #ax.plot(x_ar, rel_2_max, '.', label=r"shot_en/max_shot_en")
    #plt.ylim([0.6,1.2])
    ax.legend()
    plt.show()

    ave = sum(sht_energy)/len(sht_energy)
    #print(ave)

    return(sht_energy)

data = []
data.append(ophir_data('534475_44'))

std = 0
mean = sum(data[0]) / len(data[0])

for x in data[0]:
    std += (x - mean) ** 2
std = (std / (len(data[0]) - 1)) ** (1 / 2)
print(std)
#data.append(ophir_data('534475_38'))
for i in range(len(data[0])):
    #print(data[0][i]/max(data[0]))
    print(data[0][i])


