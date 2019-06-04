import sys
import yaml
import os
import csv
from AccessLogAnalyzer import *
from WDEstimator import *
import numpy as np

try:
    logfile = yaml.load(open('settings.yml','r'))['ACCESS_LOG_FILE_PATH']
except:
    print("Error: Cannnot open log file. Check your settings.")
    sys.exit()
    
try:
    print("Loading", flush=True)
    logs = LogParser()
    if os.path.exists("log.pickle"):
        logs.load()
        logs.update(logfile)
        logs.dump()
    else:
        logs.parse(logfile)
        logs.dump()
    print("Loaded",len(logs.log),"logs")
except:
    print("Error: Failed to load log dump data. ")
    sys.exit()

dirlist = []
filelist = []

#records = logs.log.op_filter("\AMODIFY\Z")
records = logs.log.op_filter("\ACREATE\Z|\AMODIFY\Z")
for rec in records:
    sepdir = "/".join(rec.file_path.split("/")[0:-1])
    sepfile = "/".join(rec.file_path.split("/"))
    dirlist.append(sepdir)
    filelist.append(sepfile)

dirlist = np.unique(np.array(dirlist))
filelist = np.unique(np.array(filelist))
dirc = len(dirlist)
filec = len(filelist)

#deltas = []

#for i, d in enumerate(dirlist):
#    try:
#        modify = records.path_filter(d + "/.*")
#    except:
#        print(d)
#    es = [e.timestamp for e in modify]
#    d = [es[i]-es[i-1] for i,x in enumerate(es) if i!=0]
#    deltas.append(np.array(d))

#deltas = np.array(deltas)
#print(deltas)

dirlist = []
worklist = []

with open('wd_answer.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        dirlist.append(row[0])
        worklist.append(row[1])

wdlist_in_logs = []
print("----------wdlist_in_log----------")
for d in dirlist:
    if len(records.path_filter(d + "/*")) > 0:
        wdlist_in_logs.append(d)
        print(d)

estimated_wd = []
print("----------estimated_wd----------")
wd = WDEstimator(records, [7, 5, 3, 1], 19)
for d in wd.workingdir:
    estimated_wd.append(d)
    print(d)

# 残ったファイルアクセス履歴数をカウントする
h_total = 0
for tl in wd.timelines.values():
    for h in tl:
       h_total += h[1] - h[0] + 1

# 残存履歴中のフォルダ数をカウント
dirlist_r = []
filelist_r = []
for tl in wd.timelines.values():
    for h in tl:
        for i in range(h[0], h[1]):
            sepdir_r = "/".join(records[i].file_path.split("/")[0:-1])
            sepfile_r = "/".join(records[i].file_path.split("/"))
            dirlist_r.append(sepdir_r)
            filelist_r.append(sepfile_r)
dirlist_r = np.unique(np.array(dirlist_r))
filelist_r = np.unique(np.array(filelist_r))
dirc_r = len(dirlist_r)
filec_r = len(filelist_r)

match_wd = []
not_match_wd = []
print("----------match----------")
for wl in wdlist_in_logs:
    if wl in estimated_wd:
        match_wd.append(wl)
        print(wl)
    else:
        not_match_wd.append(wl)

print("----------not_match----------")
for nw in not_match_wd:
    print(nw)

print("----------statistic----------")
wd_c = len(wdlist_in_logs)
wd_d = len(estimated_wd)
c_and_d = len(match_wd)
print("                  Unique DIR : ", dirc)
print("                 Unique FILE : ", filec)
print("        Unique DIR (Managed) : ", dirc_r)
print("       Unique FILE (Managed) : ", filec_r)
print("                  WD_correct : ", str(wd_c))
print("               WD_discovered : ", str(wd_d))
print("WD_correct AND WD_discovered : ", str(c_and_d))
print("               Total records : ", str(h_total))
print("------------score------------")
print("                   Precision : ", str(c_and_d/wd_d))
print("                      Recall : ", str(c_and_d/wd_c))
