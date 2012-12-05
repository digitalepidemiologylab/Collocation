import csv

o1_file = csv.writer(open("outbreak_sizes.csv",'wb'))
o2_file = csv.writer(open("ill_per_indexcase.csv",'wb'))

no_outbreak = 0
tot_data = 0
total_ill_per_i = 0

for i in range(1,790):
    print i
    filename = 'res_sgncont_ind%0i_epi2.csv' %(i)
    i_file = csv.reader(open(filename,'rb'))
    total_ill_per_i = 0
    for line in i_file:
        tot_data += 1
        try:
            outbreak_size = int(line[1])
        except:
            print line
        if outbreak_size == 1:
            no_outbreak += 1
        else:
            outbreak_size -= 1
            total_ill_per_i += outbreak_size
            o1_file.writerow([outbreak_size])
    o2_file.writerow([i, total_ill_per_i])

print no_outbreak
print tot_data
print float(no_outbreak)/float(tot_data)