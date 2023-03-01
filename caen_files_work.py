

def caen_files_work(file_name:str) -> list:
    with open('D:\Ioffe\TS\divertor_thomson\laser(100Hz)\laser_energy\\31.01.2023\caen_files\\%s.csv' % file_name, 'r') as file:
        launch = file.readlines()
        file.close()


    all_shots = []
    for j in range(len(launch)):
    #for j in range(1):
        shot = launch[j].split(', ')
        ans = 0
        for i in range(100):
            ans = ans + float(shot[i])
        shot[:] = [float(x) - ans/100 for x in shot]
        all_shots.append(shot)

    every_sht_max = []
    for i in range(len(all_shots)):
        every_sht_max.append(max(all_shots[i]))

    rel_2_max = every_sht_max
    rel_2_max[:] = [x / max(rel_2_max) for x in rel_2_max]
    print('caen done')

    return(rel_2_max)



#for i in ans:
    #print(i)
#with open('D:\Ioffe\TS\divertor_thomson\laser(100Hz)\laser_energy\\31.01.2023\caen_files\\00780_my.csv', 'w') as w_file:
#    string = 'time, '
#    for i in range(len(all_shots)):
#        string += str(i) + ', '
#    w_file.write(string)