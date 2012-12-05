import csv
import numpy as np
from scipy import stats

class Individual(object):
    
    def __init__(self,
                 id):
        
        self.id = id
        self.inf_times = []
    
    def add_inf_time(self,
                     inf_time):
        
        self.inf_times.append(inf_time)
    
    def return_stats(self):
        
        infections = len(self.inf_times)
        mean = np.mean(self.inf_times)
        median = np.median(self.inf_times)
        
        return (infections, mean, median)

class Population(object):
    
    def __init__(self):
        
        self.individuals = {}
    
    def add_inf_time(self,
                     id,
                     inf_time):
        
        if not id in self.individuals:
            self.individuals[id] = Individual(id)
        self.individuals[id].add_inf_time(inf_time)
    
    def read_csv_file(self,
                      filename,
                      pos_id,
                      pos_inf_time,
                      title_line=False):
        
        i_file = csv.reader(open(filename, 'rb'))
        
        for line in i_file:
            
            if title_line == True:
                title_line = False
                continue
            
            id = int(line[pos_id])
            inf_time = int(line[pos_inf_time])
            
            self.add_inf_time(id,
                              inf_time)
    
    def report_stats(self,
                     id):
        
        if id in self.individuals:
            (n, mean, median) = self.individuals[id].return_stats()
        else:
            return (None, None, None, None, None)
        
        return (n,
                mean,
                median,
                float(mean)/float(n),
                float(median)/float(n))
        
    def report_stats2(self,
                      id):
        
        if id in self.individuals:
            (n, mean, median) = self.individuals[id].return_stats()
        else:
            return (None, None, None, None, None)
        
        return (n,
                mean,
                median,
                float(mean),
                float(median))

def write_to_file(p,
                  filename_av,
                  filename_md,
                  ids):
    
    av_list = []
    md_list = []
    
    for i in ids:
        (n, av, md, av_n, md_n) = p.report_stats(i)
        if n == None: continue
        av_list.append(av_n)
        md_list.append(md_n)
    
    av_list.sort()
    md_list.sort()
    print av_list
    print md_list
    
    o_file_av = csv.writer(open(filename_av, 'wb'))
    o_file_av.writerow(['person_id', '', '', 'value', 'percentile'])
    o_file_md = csv.writer(open(filename_md, 'wb'))
    o_file_md.writerow(['person_id', '', '', 'value', 'percentile'])
    
    for i in ids:
        print i
        (n, av, md, av_n, md_n) = p.report_stats(i)
        if n == None: continue
        print av_n
        av_perc = stats.percentileofscore(av_list, av_n)
        md_perc = stats.percentileofscore(md_list, md_n)
        o_file_av.writerow([i,'','',av_n,av_perc])
        o_file_md.writerow([i,'','',md_n,md_perc])

def write_to_file_time_only(p,
                            filename_av,
                            filename_md,
                            ids):
    
    av_list = []
    md_list = []
    
    for i in ids:
        (n, av, md, av_n, md_n) = p.report_stats2(i)
        av_list.append(av_n)
        md_list.append(md_n)
    
    av_list.sort()
    md_list.sort()
    print av_list
    print md_list
    
    o_file_av = csv.writer(open(filename_av, 'wb'))
    o_file_av.writerow(['person_id', '', '', 'value', 'percentile'])
    o_file_md = csv.writer(open(filename_md, 'wb'))
    o_file_md.writerow(['person_id', '', '', 'value', 'percentile'])
    
    for i in ids:
        # print i
        (n, av, md, av_n, md_n) = p.report_stats2(i)
        # print av_n
        av_perc = stats.percentileofscore(av_list, av_n)
        md_perc = stats.percentileofscore(md_list, md_n)
        o_file_av.writerow([i,'','',av_n,av_perc])
        o_file_md.writerow([i,'','',md_n,md_perc])

########
# Main #
########

p = Population()

for i in range(1,790):
    filename = 'res_sgncont_ind%0i_inf_t.csv' %(i)
    print "reading", filename
    p.read_csv_file(filename,
                    pos_id=1,
                    pos_inf_time=2)

for i in range(1,790):
    (a,b,c,d,e) = p.report_stats2(i)
    if a == None: continue
    print i, a, b, c, d, e

write_to_file_time_only(p,
                        "average_time_perc.csv",
                        "median_time_perc.csv",
                        range(1,790))

sys.exit()

write_to_file(p,
              "average_time_by_infections_perc.csv",
              "median_time_by_infections_perc.csv",
              range(1,790))