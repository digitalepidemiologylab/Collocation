import csv

class Individual(object):
    
    def __init__(self,
                 id,
                 kind):
        
        self.id = id
        self.kind = kind
        self.data = {}
    
    def add_percentile(self,
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
        
        self.population[id].add_percentile(label, value)
        self.labels.add(label)
    
    def report_congruence(self,
                          cutoff,
                          label1,
                          label2):
        
        if (not label1 in self.labels) or (not label2 in self.labels):
            print "Error, one of the labels does not exist"
            return None
        
        pos = {}
        total = {}
        values = []
        
        for id in self.population:
            value1, value2 = self.population[id].report_pair_of_values(label1,
                                                                       label2)
            values.append(value1)
            if not value1 in pos:
                pos[value1] = 0
                total[value1] = 0
            if value2 >= cutoff:
                pos[value1] += 1
            total[value1] += 1
        
        values.sort(reverse=True)
        
        vacc_size = int((float(100-cutoff)/100.0)*789.0)
        
        pos_pos = 0.0
        
        for i in range(0,vacc_size):
            cur_val = values[i]
            pos_pos += (float(pos[cur_val])/float(total[cur_val]))
        
        if vacc_size == 0:
            result = 0.0
        else:
            result = pos_pos/float(vacc_size)
        
        return result, float(vacc_size)/(789.0)
    
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
                  label):
        
        POS_ID = 0
        POS_KIND = 1
        POS_PERC = 4
        
        i_file = csv.reader(open(filename, 'rb'))
        
        dataline=False
        
        for line in i_file:
            if dataline:
                self.add_data(int(line[POS_ID]),
                              line[POS_KIND],
                              label,
                              float(line[POS_PERC]))
            dataline = True

########
# Main #
########

pop = Population()
pop.read_data("./analyses/infection_risk_contacts.csv",
              "contacts")
pop.read_data("./analyses/degree10min_perc.csv",
              "time")

for i in range(100,-1,-1):
    result, p = pop.report_congruence(float(i),
                                      "time",
                                      "contacts")
    q = 1.0 - p
    
    rpp = p*p*789.0
    rpn = p*q*789.0
    rnp = rpn
    if rnp == 0: rnp = 0.00001
    rnn = q*q*789.0
    
    print (100-i), result, float(rpp)/float(rpp+rnp)