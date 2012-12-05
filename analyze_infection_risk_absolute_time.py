import csv
import random
import numpy
import sys
from scipy import stats

class Individual(object):
    
    def __init__(self,
                 id,
                 kind):
        
        self.id = id
        self.kind = kind
        self.data = {}
    
    def add_value(self,
                  label,
                  value):
        
        self.data[label] = value
    
    def report_pair_of_values(self,
                              label1,
                              label2):
        
        if (not label1 in self.data) or (not label2 in self.data):
            return None, None
        else:
            return self.data[label1], self.data[label2]

class Population(object):
    
    def __init__(self):
        
        self.population = {}
        self.labels = set()
        self.kinds = set()
    
    def add_data(self,
                 id,
                 kind,
                 label,
                 value):
        
        if not id in self.population:
            self.population[id] = Individual(id, kind)
            self.kinds.add(kind)
        
        self.population[id].add_value(label, value)
        self.labels.add(label)
    
    def report_average(self,
                       cutoff,
                       label1,
                       label2):
        
        if (not label1 in self.labels) or (not label2 in self.labels):
            print "Error, one of the labels does not exist"
            return None
        
        time_by_size = {}
        total = {}
        values = []
        
        for id in self.population:
            value1, value2 = self.population[id].report_pair_of_values(label1,
                                                                       label2)
            values.append(value1)
            if not value1 in time_by_size:
                time_by_size[value1] = 0.0
                total[value1] = 0
            time_by_size[value1] += float(value2)
            total[value1] += 1
        
        values.sort(reverse=True)
        
        vacc_size = int((float(100-cutoff)/100.0)*786.0)
        
        average = 0.0
        
        for i in range(0,vacc_size):
            cur_val = values[i]
            average += (time_by_size[cur_val]/float(total[cur_val]))
        
        if vacc_size == 0:
            result = 0.0
        else:
            result = average/float(vacc_size)
        
        return result, float(vacc_size)/(786.0)
    
    def report_model_diff_by_group(self,
                                   kind,
                                   label1,
                                   label2):
        
        if (not label1 in self.labels) or (not label2 in self.labels):
            print "Error, one of the labels does not exist"
            return None
        
        sum1 = 0
        sum2 = 0
        
        higher1 = 0
        equal = 0
        higher2 = 0
        
        for id in self.population:
            if self.population[id].kind != kind: continue
            value1, value2 = self.population[id].report_pair_of_values(label1,
                                                                       label2)
            sum1 += value1
            sum2 += value2
            
            if value1 > value2:
                higher1 += 1
            elif value1 == value2:
                equal += 1
            else:
                higher2 += 1
        
        return sum1, sum2, higher1, higher2
    
    def read_data(self,
                  filename,
                  label,
                  pos_data):
        
        POS_ID = 0
        POS_KIND = 1
        POS_DATA = pos_data
        
        i_file = csv.reader(open(filename, 'rb'))
        
        dataline=False
        
        for line in i_file:
            if dataline:
                self.add_data(int(line[POS_ID]),
                              line[POS_KIND],
                              label,
                              float(line[POS_DATA]))
            dataline = True
    
    def calculate_random_case (self,
                               repetitions,
                               cutoff,
                               label):
        
        if not label in self.labels:
            print "Error, one of the labels does not exist"
            return None
        
        time_by_size = {}
        total = {}
        values = []
        
        for id in self.population:
            values.append(self.population[id].data[label])
        
        vacc_size = int((float(100-cutoff)/100.0)*786.0)
        
        if vacc_size == 0:
            return 0, 0, 0, 0, 0
        
        list_of_outcomes = []
        
        for rep in range(0, repetitions):
            choice = random.sample(values,vacc_size)
            list_of_outcomes.append(numpy.mean(choice))
        
        perc10 = stats.scoreatpercentile(list_of_outcomes, 10)
        perc25 = stats.scoreatpercentile(list_of_outcomes, 25)
        perc50 = stats.scoreatpercentile(list_of_outcomes, 50)
        perc75 = stats.scoreatpercentile(list_of_outcomes, 75)
        perc90 = stats.scoreatpercentile(list_of_outcomes, 90)
        
        return perc10, perc25, perc50, perc75, perc90

########
# Main #
########

pop = Population()
pop.read_data("./analyses/average_time_by_infections_perc.csv",
              "contacts",3)
pop.read_data("./analyses/degree20min_perc_nozeros.csv",
              "time",4)

for i in range(100,-1,-1):
    result, p = pop.report_average(float(i),
                                   "time",
                                   "contacts")
    q = 1.0 - p
    
    rpp = p*p*786.0
    rpn = p*q*786.0
    rnp = rpn
    if rnp == 0: rnp = 0.00001
    rnn = q*q*786.0
    
    print (100-i), result, float(rpp)/float(rpp+rnp)

sys.exit()

for i in range(100,-1,-1):
    a, b, c, d, e = pop.calculate_random_case(100000,
                                              float(i),
                                              "contacts")
    print (100-i), a, b, c, d, e

sys.exit()

