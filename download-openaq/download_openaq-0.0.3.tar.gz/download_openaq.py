import os
import boto3
from multiprocessing import Pool, cpu_count
import pandas as pd

s3 = boto3.resource('s3')
errors_log = {}

# Input Params
wd = "./aws-landing/"
start = "2016-01-01"
end = "2016-12-31"

if not os.path.exists(wd): os.makedirs(wd)

# Gen Date Range
timeWindow = pd.date_range(start, end, freq=pd.tseries.offsets.DateOffset(days=1))

def download_s3(date):
    snap_date = str(date)[:10]
    try:
        s3.Object('openaq-data', '{0}.csv'.format(snap_date)).download_file('{0}{1}.csv'.format(wd,snap_date))
    except Exception as e:
        errors_log[snap_date] = e
        pass

def download():
    max_processes = cpu_count()
    current_idx = 0
    batch_size = max_processes
    end_idx = len(timeWindow)    
    while current_idx <= end_idx:
        p = Pool(max_processes)
        next_batch_idx = current_idx + batch_size
        p.map(download_s3, timeWindow[current_idx:next_batch_idx])
        p.close()
        current_idx = next_batch_idx
