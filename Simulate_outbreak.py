import networkx
import math
import random
import copy
import sys
import csv


####################
# Global variables #
####################

II_FILE = sys.argv[1]

INDEX_CASE = int(sys.argv[2])

RUNS = int(sys.argv[3])

OUTPUT_SIGN = str(sys.argv[4])

TIMESEQUENCE = [True,False,
                True,False,
                True,False,
                True,False,
                True,False,
                False,False,
                False,False]

TIME_TO_TIMESTEP = 2.0

CUR_STEP = 1

WEIGHT_FACTOR = 0.25

INFECTIOUS_NOTCONFINED = 1

ID1 = 0 # 1st column in csv-file is the infector ID
ID2 = 1 # 2nd column is the ID of the exposed individual
ID3 = 2 # 3rd column gives the weight

SEED_SIZE = 1

#############
# Functions #
#############

def read_ii_exposure_data(filename):
    # filename points to the file that contains the following data:
    #          Infector ID, Exposed ID, Exposure [quanta]
    
    global ID1, ID2, ID3
    global WEIGHT_FACTOR
    
    G = networkx.DiGraph()
    
    input_file = open(filename,'r')
    
    for line in input_file:
        
        infector = int(line.split()[ID1])
        exposed = int(line.split()[ID2])
        weight_val = int(line.split()[ID3])
        
        if not infector in G.nodes():
            G.add_node(infector)
            G.node[infector]['status_time'] = None
        
        if not exposed in G.nodes():
            G.add_node(exposed)
            G.node[exposed]['status_time'] = None
        
        if weight_val > 0:
            G.add_edge(infector, exposed, weight=(float(weight_val)*
                                                  WEIGHT_FACTOR))
    
    return G, set(G.nodes())

def infect_seed(seed_size,
                G_iie,
                index=False):
    
    sus = set()
    exp = set()
    inf = set()
    con = set()
    rec = set()
    
    individuals = set(G_iie.nodes())
    if index == False:
        infectors = set(random.sample(individuals,seed_size))
    else:
        infectors = set([index])
    
    for e in infectors:
        G_iie.node[e]['status_time'] = exposure_period()
        exp.add(e)
    
    sus = individuals - exp
    
    return sus, exp, inf, con, rec

def inf_prob(timestamps):
    return 1 - ((1 - 0.003)**timestamps)

def iteration(G_iie,
              sus,
              exp,
              inf,
              con,
              rec,
              schooltime=True):
    
    add = {'sus':set(),
           'exp':set(),
           'inf':set(),
           'con':set(),
           'rec':set()}
    
    remove = {'sus':set(),
              'exp':set(),
              'inf':set(),
              'con':set(),
              'rec':set()}
    
    add, remove = c_to_r(G_iie,
                         con,
                         add,
                         remove)
    
    add, remove = i_to_r(G_iie,
                         inf,
                         add,
                         remove)
    
    add, remove = i_to_c(G_iie,
                         inf,
                         add,
                         remove)
    
    add, remove = e_to_i(G_iie,
                         exp,
                         add,
                         remove)
    
    if schooltime==True:
        add, remove = s_to_e(G_iie,
                             sus,
                             inf,
                             add,
                             remove)
    
    sus, exp, inf, con, rec = update_healthlists(add,
                                                 remove,
                                                 sus,
                                                 exp,
                                                 inf,
                                                 con,
                                                 rec)
    
    return sus, exp, inf, con, rec

def update_healthlists(add,
                       remove,
                       sus,
                       exp,
                       inf,
                       con,
                       rec):
    
    sus = sus - remove['sus']
    exp = exp - remove['exp']
    inf = inf - remove['inf']
    con = con - remove['con']
    rec = rec - remove['rec']
    
    sus = sus | add['sus']
    exp = exp | add['exp']
    inf = inf | add['inf']
    con = con | add['con']
    rec = rec | add['rec']
    
    return sus, exp, inf, con, rec

def c_to_r(G_iie,
           con,
           add,
           remove):
    
    for c in con:
        if G_iie.node[c]['status_time'] == 1:
            add['rec'].add(c)
            remove['con'].add(c)
        elif G_iie.node[c]['status_time'] > 1:
            G_iie.node[c]['status_time'] -= 1
        else:
            print "Error"
    
    return add, remove

def i_to_r(G_iie,
           inf,
           add,
           remove):
    
    return add, remove

def i_to_c(G_iie,
           inf,
           add,
           remove):
    
    for i in inf:
        if G_iie.node[i]['status_time'] == 1:
            remove['inf'].add(i)
            con_period = confinement_period()
            if con_period == 0:
                add['rec'].add(i)
            else:
                add['con'].add(i)
                G_iie.node[i]['status_time'] = con_period
        elif G_iie.node[i]['status_time'] > 1:
            G_iie.node[i]['status_time'] -= 1
        else:
            print "Error"
    
    return add, remove

def confinement_period(): ### Correct?
    
    for t in range(0,12):
        p = 1.0 - (0.95 ** float(t+1))
        if random.random() <= p:
            break
    
    return t

def e_to_i(G_iie,
           exp,
           add,
           remove):
    
    global INFECTIOUS_NOTCONFINED
    
    for e in exp:
        if G_iie.node[e]['status_time'] == 1:
            add['inf'].add(e)
            remove['exp'].add(e)
            G_iie.node[e]['status_time'] = INFECTIOUS_NOTCONFINED
        elif G_iie.node[e]['status_time'] > 1:
            G_iie.node[e]['status_time'] -= 1
        else:
            print "Error"
    
    return add, remove

def s_to_e(G_iie,
           sus,
           inf,
           add,
           remove):
    
    for s in sus:
        
        timestamps = 0.0
        
        for i in inf:
            if s in G_iie.neighbors(i):
                timestamps += G_iie[i][s]['weight']
        
        infection_probability = inf_prob(timestamps)
        if random.random() < infection_probability:
            remove['sus'].add(s)
            add['exp'].add(s)
            G_iie.node[s]['status_time'] = exposure_period()
    
    return add, remove

def exposure_period():
    
    SCALE_PAR = 1.10
    SHAPE_PAR = 2.21
    OFFSET = 0.5
    
    t = int(round((random.weibullvariate(SCALE_PAR, SHAPE_PAR) + OFFSET)
                  * TIME_TO_TIMESTEP))
    
    return t

##############
# Initialize #
##############

G_iie, individuals = read_ii_exposure_data(II_FILE)
print "Data of",len(G_iie.nodes())," nodes read in."

i_tot = []
time_to_peak = []
max_time = []
indiv_ill = []

##############
# Simulation #
##############

time_of_infection = {}

for run in range(1,RUNS+1):
        
    print "---> RUN", run
    
    t_cnt = 0
    i_max = (0, 0)
    
    sus, exp, inf, con, rec = infect_seed(SEED_SIZE,
                                          G_iie,
                                          INDEX_CASE)
    
    for week in range(0,10):
        
        if len(exp)+len(inf) == 0:
            break
        
        if week == 0:
            seq1 = random.randint(0,13)
        else:
            seq1 = 0
        seq2 = 14
        
        for t in TIMESEQUENCE[seq1:seq2]:
            
            t_cnt += 1
            
            if len(inf) > i_max[0]:
                i_max = (len(inf), t_cnt)
            
            sus, exp, inf, con, rec = iteration(G_iie,
                                                sus,
                                                exp,
                                                inf,
                                                con,
                                                rec,
                                                t)
            
            for case in inf:
                if case == INDEX_CASE: continue
                if not case in time_of_infection:
                    time_of_infection[case] = [t_cnt]
                else:
                    time_of_infection[case].append(t_cnt)
            
            if len(exp)+len(inf) == 0:
                break
            
    time_to_peak.append(i_max[1])
    max_time.append(t_cnt)
    i_tot.append(len(con)+len(rec))
    indiv_ill.append(con | rec)

#################
# Store results #
#################

filename = './work/cont_results/res_sgn%0s_ind%0i_inf_t.csv' %(
                                                        OUTPUT_SIGN, INDEX_CASE)
print filename
o = csv.writer(open(filename, 'wb'))
for i in time_of_infection:
    for inf_time in time_of_infection[i]:
        o.writerow([INDEX_CASE, i, inf_time])

filename = './work/cont_results/res_sgn%0s_ind%0i_epi2.csv' %(
                                                        OUTPUT_SIGN, INDEX_CASE)
print filename
o = csv.writer(open(filename, 'wb'))
for i in range(0, len(i_tot)):
    o.writerow([INDEX_CASE,
                i_tot[i],
                time_to_peak[i],
                max_time[i]])

#filename = './work/cont_results/res_sgn%0s_ind%0i_indivs.csv' %(
#                                                        OUTPUT_SIGN, INDEX_CASE)
#o = csv.writer(open(filename, 'wb'))
#indiv_list = sorted(individuals)
#o.writerow(indiv_list)
#for line in indiv_ill:
#    output_line = []
#    for i in indiv_list:
#        if i in line:
#            output_line.append(1)
#        else:
#            output_line.append(0)
#    o.writerow(output_line)
