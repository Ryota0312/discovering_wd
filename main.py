import sys
import yaml
import os
import csv
import re
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
worklist = []

with open('wd_answer.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        dirlist.append(row[0])
        worklist.append(row[1])

wdlist_in_logs = []
print("----------wdlist_in_log----------")
for d in dirlist:
    if len(logs.log.path_filter(d + "/*")) > 0:
        wdlist_in_logs.append(d)
        print(d)

estimated_wd = []
print("----------estimated_wd----------")
wd = WDEstimator(logs.log, [5, 3, 1], 18)
for d in wd.workingdir:
    estimated_wd.append(d)
    print(d)

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
print("正解ワーキングディレクトリ:", str(len(wdlist_in_logs)))
print("推定ワーキングディレクトリ:", str(len(estimated_wd)))
print("正解かつ推定　　　　　　　:", str(len(match_wd)))
