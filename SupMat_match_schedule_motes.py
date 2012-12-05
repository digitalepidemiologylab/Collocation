import csv
from scipy import stats

####
# Parameter

PERIODS = {}

PERIODS[0] = range(680,781)
PERIODS[1] = range(775,1026)
PERIODS[2] = range(1020,1266)
PERIODS[5] = range(1375,1621)
PERIODS[6] = range(1250,1496)
PERIODS[7] = range(1620,1861)
PERIODS[8] = range(1860,2031)

DURATIONS = {}

DURATIONS[0] = 30
DURATIONS[1] = 75
DURATIONS[2] = 75
DURATIONS[5] = 75
DURATIONS[6] = 75
DURATIONS[7] = 75
DURATIONS[8] = 50

####
# Global variables

schedules = {}
roles = {}
locations = {}
occ_teachers = {}
occ_students = {}
individuals = {}
individuals_final = {}
duration = {}
pers_duration = {}
perc_duration = {}
perc_pers_duration = {}

def read_schedule(filename,
                  pos_mote,
                  pos_period,
                  pos_occupancy,
                  pos_teacher_mote,
                  title_line):
    
    global schedules
    global duration
    global pers_duration
    
    i_file = csv.reader(open(filename, 'rb'))
    
    for line in i_file:
        
        if title_line == True:
            title_line = False
            continue
        
        if line[pos_mote]=='': continue
        mote = int(line[pos_mote])
        period = int(line[pos_period])
        occupancy = int(line[pos_occupancy])
        teacher_mote = int(line[pos_teacher_mote])
        
        if not period in schedules:
            schedules[period] = {}
            occ_teachers[period] = {}
            occ_students[period] = {}
        
        if not mote in schedules[period]:
            schedules[period][mote] = occupancy
            occ_teachers[period][mote] = {}
            occ_students[period][mote] = {}
        else:
            schedules[period][mote] += occupancy
        
        if not teacher_mote in duration:
            duration[teacher_mote] = DURATIONS[period]
            pers_duration[teacher_mote] = DURATIONS[period] * occupancy
        else:
            duration[teacher_mote] += DURATIONS[period]
            pers_duration[teacher_mote] += DURATIONS[period] * occupancy

def read_roles(filename,
               pos_id,
               pos_role,
               title_line):
    
    global roles
    
    i_file = csv.reader(open(filename, 'rb'))
    
    for line in i_file:
        
        if title_line == True:
            title_line = False
            continue
        
        id = int(line[pos_id])
        role = line[pos_role]
        
        roles[id] = role

def read_locations(filename,
                   id,
                   pos_time,
                   pos_mote,
                   title_line):
    
    global locations
    
    locations[id] = {}
    
    i_file = open(filename, 'rb')
    
    for line in i_file:
        
        if title_line == True:
            title_line = False
            continue
        
        time = int(line[pos_time[0]:pos_time[1]])
        mote = int(line[pos_mote[0]:pos_mote[1]])
        
        locations[id][time] = mote

def match_motes_to_schedule_students():
    
    global roles
    global locations
    global occ_students
    
    for i in locations:
        
        # Only students are of interest
        if roles[i] != 'student': continue
        individuals[i] = {}
        for p in range(0,9):
            individuals[i][p] = []
        
        # Loop over all timestamps of i
        for t in locations[i]:
            
            # Store all periods to which t potentially belongs to
            p_list = []
            for p in PERIODS:
                if t in PERIODS[p]:
                    p_list.append(p)
            mote = locations[i][t]
            
            # Loop over all potential periods; store presence time at location
            for p in p_list:
                if mote in occ_students[p]:
                    if i in occ_students[p][mote]:
                        occ_students[p][mote][i] += 1
                    else:
                        occ_students[p][mote][i] = 1

def match_motes_to_schedule_teacher():
    
    global roles
    global locations
    global occ_teachers
    
    for i in locations:
        
        # Only students are of interest
        if roles[i] != 'teacher': continue
        individuals[i] = {}
        for p in range(0,9):
            individuals[i][p] = []
        
        # Loop over all timestamps of i
        for t in locations[i]:
            
            # Store all periods to which t potentially belongs to
            p_list = []
            for p in PERIODS:
                if t in PERIODS[p]:
                    p_list.append(p)
            mote = locations[i][t]
            
            # Loop over all potential periods; store presence time at location
            for p in p_list:
                if mote in occ_teachers[p]:
                    if i in occ_teachers[p][mote]:
                        occ_teachers[p][mote][i] += 1
                    else:
                        occ_teachers[p][mote][i] = 1

def individuals_to_classes():
    
    global roles
    global locationsu
    global schedules
    global occ_teachers
    global occ_students
    global individuals
    global individuals_final
    
    occ_tracker = {}
    to_check = []
    
    # Allocate STUDENTS to scheduled classes
    
    for p in occ_students:
        for m in occ_students[p]:
            for i in occ_students[p][m]:
                if not i in individuals:
                    individuals[i] = {}
                    individuals[i][p] = []
                if not p in individuals[i]:
                    individuals[i][p] = []
                individuals[i][p].append((m, occ_students[p][m][i]))
    
    
    individuals_final = {}
    for i in individuals:
        individuals_final[i] = {}
        for p in individuals[i]:
            individuals_final[i][p] = None
    
    
    for p in schedules:
        
        occ_tracker[p] = {}
        
        for m in schedules[p]:
            
            occupancy = schedules[p][m]
            orig_occupancy = occupancy
            
            # Sorted list of presence time
            list_of_values = occ_students[p][m].values()
            list_of_values.sort(reverse=True)
            set_of_tuples=set()
            for id in occ_students[p][m]:
                set_of_tuples.add((id, occ_students[p][m][id]))
            
            # Identify x individuals with longest presence time (x=occupancy)
            for i in range(0, len(list_of_values)-1):
                if occupancy == 0: break
                for tuple in set_of_tuples:
                    if tuple[1] == list_of_values[i]:
                        if len(individuals[tuple[0]][p]) == 1:
                            set_of_tuples.remove(tuple)
                            individuals_final[tuple[0]][p] = m
                            occupancy -= 1
                            break
                        else:
                            flag = False # Flag will be true if another mote has higher value
                            for tuple2 in individuals[tuple[0]][p]:
                                if tuple2[1] > tuple[1]: flag = True
                            if flag == False:
                                set_of_tuples.remove(tuple)
                                occupancy -= 1
                                print tuple[0], p
                                individuals_final[tuple[0]][p] = m
                                break
                            elif flag == True:
                                to_check.append((tuple[0],p))
            occ_tracker[p][m] = occupancy
            print p, m, occupancy, orig_occupancy
            if occupancy == 0:
                for tuple in set_of_tuples:
                    temp_list = []
                    for tuple2 in individuals[tuple[0]][p]:
                        if tuple2[0] == m: continue
                        temp_list.append(tuple2)
                    individuals[tuple[0]][p] = temp_list
    
    print "2nd round"
    
    for tuple in to_check:
        check_list = []
        if individuals_final[tuple[0]][tuple[1]] != None: continue
        for loc_info in individuals[tuple[0]][tuple[1]]:
            if occ_tracker[tuple[1]][loc_info[0]] <= 0: continue
            check_list.append(loc_info)
        if len(check_list) == 0: continue
        max_val = 0
        for loc_info in check_list:
            if loc_info[1] > max_val:
                max_val = loc_info[1]
                max_mote = loc_info[0]
        individuals_final[tuple[0]][tuple[1]] = max_mote
        occ_tracker[tuple[1]][max_mote] -= 1
    
    for p in occ_tracker:
        for m in occ_tracker[p]:
            
            occupancy = occ_tracker[p][m]
            if occupancy <= 0:
                if occupancy < 0: print "ERROR"
                continue
            orig_occupancy = occupancy
            
            for i in individuals:
                if occupancy == 0: break
                if (len(individuals[i][p]) > 1):
                    # print i, p, len(individuals[i][p])
                    flag = False
                    for tuple in individuals[i][p]:
                        if (tuple[0] == m) and (tuple[1] > 15):   # if more than 5 min present at room m
                            occupancy -= 1
                            flag = True
                            break
                    if flag == True:
                        individuals[i][p] = [tuple]
            print p, m, occupancy, orig_occupancy

def check_occupancy():
    
    global schedules
    global individuals_final
    
    occ_tracker = {}
    
    
    for i in individuals_final:
        for p in individuals_final[i]:
            if individuals_final[i][p] == None: continue
            mote = individuals_final[i][p]
            if p not in occ_tracker:
                occ_tracker[p] = {}
            if mote not in occ_tracker[p]:
                occ_tracker[p][mote] = 1
            else:
                occ_tracker[p][mote] += 1
    
    print "Check"
    
    for p in schedules:
        for m in schedules[p]:
            if m not in occ_tracker[p]:
                value = 0
            else:
                value = occ_tracker[p][m]
            print p, m, value, schedules[p][m]

def values_for_students():
    
    global individuals_final
    global schedules
    global roles
    global duration
    global pers_duration
    
    for i in individuals_final:
        if i in duration:
            print "Error! %0i already exists" %(i)
            continue
        duration[i] = 0
        pers_duration[i] = 0
        # If not allocated to an advisory class
        if not 0 in individuals_final[i]:
            duration[i] += DURATIONS[0] 
            pers_duration[i] += (DURATIONS[0] * 8.20)
        for p in individuals_final[i]:
            if individuals_final[i][p] == None: continue
            duration[i] += DURATIONS[p] 
            if individuals_final[i][p] != 10028:
                pers_duration[i] += (DURATIONS[p] *
                                          schedules[p][individuals_final[i][p]])
            else:
                # Here, classes could not be distinguished because mote on floor
                pers_duration[i] += (DURATIONS[p] * 8.33)

def calculate_percentiles(ids):
    
    global duration
    global pers_duration
    global perc_duration
    global perc_pers_duration
    
    list_durations = []
    list_pers_durations = []
    for i in ids:
        if not i in duration:
            list_durations.append(0)
            list_pers_durations.append(0)
            duration[i] = 0
            pers_duration[i] = 0
        else:
            list_durations.append(duration[i])
            list_pers_durations.append(pers_duration[i])
    list_durations.sort()
    list_pers_durations.sort()
    
    print list_durations
    print list_pers_durations
    
    for i in ids:
        perc_duration[i] = stats.percentileofscore(list_durations,
                                                   duration[i])
        perc_pers_duration[i] = stats.percentileofscore(list_pers_durations,
                                                        pers_duration[i])

####
# Main


print "Reading schedule data"
filename = "../School_Mote_Analysis_2012/School_Schedules/2010_Schedule_Conv_Motes.csv"
read_schedule(filename,
              pos_mote=4,
              pos_period=0,
              pos_occupancy=3,
              pos_teacher_mote=5,
              title_line=True)

print "Reading role data"
filename = "./data_files/roles.csv"
read_roles(filename,
           pos_id=0,
           pos_role=1,
           title_line=False)

print "Reading location data"
for i in range(1, 790):
    filename = "../locations4/location_node-%0i" %(i)
    read_locations(filename,
                   id=i,
                   pos_time=[0,6],
                   pos_mote=[6,12],
                   title_line=False)

print "Matching motes to students' schedules"
match_motes_to_schedule_students()
print "Individuals to teachers' schedules"
individuals_to_classes()
check_occupancy()

sys.exit()
print "Calculate schedule based values for students"
values_for_students()
print "calculate percentiles"
calculate_percentiles(range(1,790))



sys.exit()

o_file = csv.writer(open('./analyses/schedule_time.csv', 'wb'))
o_file.writerow(['person_id', '', '', 'value', 'percentile'])
for i in range(1,790):
    o_file.writerow([i,'','',duration[i],perc_duration[i]])

o_file = csv.writer(open('./analyses/schedule_collocation_time.csv', 'wb'))
o_file.writerow(['person_id', '', '', 'value', 'percentile'])
for i in range(1,790):
    o_file.writerow([i,'','',pers_duration[i],perc_pers_duration[i]])

#for id in roles:
#    if id in duration:
#        print id, duration[id], pers_duration[id], roles[id]
#    else:
#        print id, 0, 0, roles[id]