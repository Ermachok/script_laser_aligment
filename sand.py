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

#for i, (k, v) in enumerate(config_fiber_poly.items()):
    #print(i, k, v, fibers_1_ch[i])


x_ar = [ind*0.3125 for ind in range(1024)]
for x in x_ar:
    print(x,x_ar.index(x))