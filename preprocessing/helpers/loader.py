#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 14:01:53 2017

@author: Riaan
"""

import pandas as pd
import sys
import numpy as np
from datetime import datetime

def shares_outstanding(mindate = '19940101'):
    
    df = pd.DataFrame()
    reader = pd.read_stata('data/stock_data/Torstens data/msf_1926to2014.dta', iterator=True)
            
    try: 
        chunk = reader.get_chunk(10*1000)
        while len(chunk) > 0:
            df = df.append(chunk, ignore_index=True)
            chunk = reader.get_chunk(100*1000)
            print '.',
            sys.stdout.flush()
    except (StopIteration, KeyboardInterrupt):
        pass
    print '\nloaded {} rows'.format(len(df))
    
    # remove some of the columns
    df = df[['permno', 'date', 'shrout']]

    # minimum date to keep 
    date = datetime.strptime('19940101', '%Y%m%d') # remove everything before 
    df = df[df['date'].dt.year > date.year]
    
    # iterate over pandas dataframe and load into dict
    main_dict = {}
    for x, y, z in np.asarray(df):
        date = y
        date_str = str(date.year) + str(date.month)
        
        if x in main_dict:
            main_dict[x][date_str] = z
        else:
            main_dict[x] = {date_str: z}
        
    

    return  main_dict


def book_value(bv_loc = 'data/stock_data/book_value_annual.csv'):
    df = pd.read_csv(bv_loc)
    df = df[['datadate', 'bkvlps', 'cusip']]
    df['datadate'] = df['datadate'].apply(lambda x: pd.to_datetime(datetime.strptime(str(x),
                                                                                     '%Y%m%d'),
                                                                                       errors = 'coerce'))
    df['year'] = df['datadate'].apply(lambda x: x.year)
    df['year']= df['year'].astype(int)
    
    cols = df.columns.tolist()
    
    cols =  [cols[-2], cols[-1], cols[1]]
    df = df[cols]
    
    main_dict = {}
    for x, y, z in np.asarray(df):
        date = int(y)
        x = x
        if x in main_dict:
            main_dict[x][date] = z
        else:
            main_dict[x] = {date: z}
            
    return main_dict
