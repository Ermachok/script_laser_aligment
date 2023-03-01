import statsmodels.api as sm
import matplotlib.pyplot as plt
import numpy as np

caen_file_number = '00828'

with open('D:\Ioffe\TS\divertor_thomson\laser(100Hz)\\alignment\\10.02.2023\caen_files\\%s\\scat_Nphe_%s.csv'
          % (caen_file_number,caen_file_number), 'r') as file:
    data = file.readlines()
    file.close()


for j in range(1,2):
    dist_data = []
    for i in range(1, len(data)):
        #print(float(data[i].split(', ')[j]))
        dist_data.append(float(data[i].split(', ')[j]))


    mean = sum(dist_data)/len(dist_data)

    std = 0
    for x in dist_data:
        std += (x - mean)**2
    std = (std / (len(dist_data)-1))**(1/2)

    dist_data[:] = [(x - mean)/std for x in dist_data]

    #print(dist_data)
    my_array = np.array(dist_data)

    fig = sm.qqplot(my_array, line='45')
    plt.show()

for x in dist_data:
    print(x)