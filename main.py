from main import caen_files_work
import ophir_files_work

dict = {
    '534475_16': '00782',
    '534475_17': '00784',
    '534475_18': '00785',
    '534475_19': '00786',
    '534475_20': '00787',
    '534475_21': '00788',
    '534475_22': '00789',
    '534475_23': '00790',
    '534475_24': '00791',
    '534475_25': '00792',
    '534475_26': '00793',
    '534475_27': '00794',
}

ophir_all_data = []
caen_all_data = []

for i, (k, v) in enumerate(dict.items()):
    print(i, k, v)
    ophir_all_data.append(ophir_files_work.ophir_rel2max(k))
    caen_all_data.append(caen_files_work.caen_files_work(v))

#print(len(ophir_all_data[3]), len(caen_all_data[3]))

for i in range(len(caen_all_data[2])):
    print(caen_all_data[9][i], ophir_all_data[9][i])

#print(dict[list[0]])