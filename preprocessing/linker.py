#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 15:43:41 2017

@author: Riaan
"""
import csv
import os
import sys 
from datetime import datetime
import pandas as pd
import sys
from dateutil.relativedelta import relativedelta
import numpy as np
from progressbar import ProgressBar

def link_year(year, shares_dict, bv, statement  = '10-K' ):
    linker = DataLinker(year, shares_dict, bv)
    linker.verify_exists()
    #linker.link_codes(year)
    


class DataLinker(object):
    
    def __repr__(self):
        return 'This is the linker object for year: %i' % self.year
    
    
    def __init__(self, year, shares_dict, bv,  statement = '10-K', restart = True, thresholds = None,
                 headers = ['cshoc', 'cshtrd', 'prccd', 'exchg'], by = 'cusip'):
        '''
        headers:
            cshoc --> shares outstanding
            cshtrd --> daily trading volume 
            prccd --> price close daily
            exchg --> stock exchange code 
            
        header bookvalue annual:
            bkvlps --> book value per share
        '''
        
        self.year = year
        self.quarters = ['QTR'+ str(i) for i in xrange(1,5)]
        self.years_dir = 'data/indexes/{}'.format(year)
        self.statement_type = statement
        
        self.linking_dir = 'data/linking_table/'
        self.data_dir = 'data/stock_data/'
        
        # sorting titles 
        self.headers = headers
        self.by = by 
        
        self.shares_dict = shares_dict # Shares outstanding
        self.book_value = bv           # book value per share
        
        
    def _check_dates(self, date_str, date_obj, permno):
        
        dates = self.shares_dict[permno]
        
        
        date_m_1 = date_obj - relativedelta(months=1)
        date_m_1 = str(date_m_1.year) + str(date_m_1.month)
        
        if date_m_1 in dates:
            return date_m_1
        
        date_p_1 = date_obj + relativedelta(months=1)
        date_p_1 = str(date_p_1.year) + str(date_p_1.month)
        
        if date_p_1 in dates:
            return date_p_1
        
        return None
        
        
    def _setup(self):
        
        print 'Setting up correct data!'
        
        with open(self.linking_dir + 'linking_table.csv', 'rb') as file_in:
            
            reader = csv.reader(file_in, delimiter=',')
        
            raw_data = [x for x in reader]
            
        header = [x.lower() for x in raw_data[0]]
        
        # get indexes 
        cik_idx = header.index('cik')
        cusip_idx = header.index('cusip')
        sic_idx = header.index('sic')
        lpermno_idx = header.index('lpermno')

        # important lookup tables
        self.lookup_table = {x[cik_idx].lstrip('0'):[x[cusip_idx], x[sic_idx],x[lpermno_idx] ] for x in raw_data[1:]}
        self.lookup_table_cusip = {x[cusip_idx].lstrip('0'):[x[cik_idx], x[sic_idx],x[lpermno_idx] ] for x in raw_data[1:]}
        
        del self.lookup_table['']
        del self.lookup_table_cusip['']
        
        print '\tLoaded lookup table!'
        
        # load stock data, except for shares outstanding
        with open(self.data_dir + 'CRSP_stockdata.csv', 'rb') as file_in:
            reader = csv.reader(file_in, delimiter=',')
            raw_data = [x for x in reader]
            
        header = [x.lower() for x in raw_data[0]]
        
        idxs = [header.index(x) for x in self.headers]
        
        rel_headers = [header[x] for x in idxs]
        
        # get index of shares outstanding in new header file
        rep_cshoc = False
        if 'cshoc' in rel_headers:
            rep_cshoc = True
            idx_cshoc = rel_headers.index('cshoc')
        
        by_idx = header.index('cusip')
        date_idx = header.index('datadate')
        permno_idx = header.index('lpermno')
        
        
        # compile dictionary with data
        main_dict = {}
        pbar = ProgressBar()
        
        print '\tLinking to monthly outstanding shares data, progress:'
        for x in pbar(raw_data[1:]):
            
            data_field = [x[i] for i in idxs]
            date = datetime.strptime(str(x[date_idx]), '%Y%m%d')
            yr_str = str(date.year)
            date_str = yr_str + str(date.month)
            by = x[by_idx]
            
            if by in main_dict:
                
                if data_field[3] not in ['11', '12','14']:
                    continue 
                
                # replace cshoc with montly data
                if rep_cshoc: 
                    
                    # check if the permno exists
                    if by.lstrip('0') in  self.lookup_table_cusip:
                        permno = int(self.lookup_table_cusip[by.lstrip('0')][2])
                        
                    else:
                        continue
                    
                    # check if permno in dictionary 
                    if permno in self.shares_dict:
                        
                        # check if date in dictionary 
                        if date_str in self.shares_dict[permno]:
                            
                            data_field[idx_cshoc] = self.shares_dict[permno][date_str]
                            
                            # link book values per share
                            if by in self.book_value:
                                if int(yr_str) in self.book_value[by]:
                                    data_field.append(self.book_value[by][int(yr_str)])
                            else:
                                data_field.append('-1')
                            
                            main_dict[by][date] = data_field
                        
                        # check whether other dates exist
                        else:
                            date_str = self._check_dates(date_str, date, permno)
                            
                            if date_str:
                                data_field[idx_cshoc] = self.shares_dict[permno][date_str]
                                
                                # link book values per share
                                if by in self.book_value:
                                    if int(yr_str) in self.book_value[by]:
                                        data_field.append(self.book_value[by][int(yr_str)])
                                else:
                                    data_field.append('-1')
                                
                                main_dict[by][date] = data_field
                                
                            else:
                                continue
                                
                
            else:
                # if datafield doesn't exist yet. Create it!
                
                if data_field[3] not in ['11', '12','14']:
                    continue 
                
                # replace cshoc with montly data
                if rep_cshoc: 
                    
                    # check if the permno exists
                    if by.lstrip('0') in  self.lookup_table_cusip:
                        permno = int(self.lookup_table_cusip[by.lstrip('0')][2])
                        
                    else:
                        continue
                    
                    
                    if permno in self.shares_dict:
                        
                        if date_str in self.shares_dict[permno]:
                            
                            
                            data_field[idx_cshoc] = self.shares_dict[permno][date_str]
                            
                            # link book values per share
                            if by in self.book_value:
                                if int(yr_str) in self.book_value[by]:
                                    data_field.append(self.book_value[by][int(yr_str)])
                            else:
                                data_field.append('-1')
                            
                            main_dict[by] = {date: data_field}
                            
                        # check whether other dates exist
                        else:
                            date_str = self._check_dates(date_str, date, permno)
                            
                            if date_str:
                                data_field[idx_cshoc] = self.shares_dict[permno][date_str]
                                
                                # link book values per share
                                if by in self.book_value:
                                    if int(yr_str) in self.book_value[by]:
                                        data_field.append(self.book_value[by][int(yr_str)])
                                else:
                                    data_field.append('-1')
                                    
                                
                                main_dict[by] = {date: data_field}
                                
                            else:
                                continue
                
        
        
        total = 0
        complete = 0
        comp2 = 0
        for x, y in main_dict.iteritems():
            for i, j in y.iteritems():
                total +=1
                if j[0] != '':
                    complete+=1
                    
                if j[-1] > 0 :
                    comp2 +=1
                    
        
        
        print 'complete percent shrout: {} % '.format( (float(complete)/float(total))*100.0)
        print 'complete percent bvps: {} % '.format( (float(comp2)/float(total))*100.0)
        

        
    def verify_exists(self):
        
        if not os.path.isfile('data/linking_table/linking_table.csv'):
            sys.exit('Create folder named linking_table in data folder and put the linking_table.csv there.'
                     )
        else:
            print '\tLinking table found!'
        
        if not os.path.exists('data/indexes/' + str(self.year)):
            sys.exit('Please parse the data before calling linking table.')
        else:
            print '\tFound data.'
            
        self._setup()
        
            
    
    def link_codes(self, year, seperator = ','):
        
        for quarter in self.quarters:
            
            print '\t Linking data in Quarter {}.'.format(quarter[-1])
            
            with open(self.years_dir+'/' + quarter + '/'+ 'master_processed_{}.txt'.format(
                                        self.statement_type), 'rb' ) as file_in:
                
                reader = csv.reader(file_in, delimiter='|')
                raw_data = [x for x in reader]
            
            header = raw_data[0]
            cik_idx = header.index('CIK')
            
            header.extend(['cusip', 'sic'])
            
            deleted = 0
            updated = [header]
            for x in raw_data[1:]:
                
                if x[cik_idx] in self.lookup_table:
                    x.extend(self.lookup_table[x[cik_idx]])
                    updated.append(x)
                    
                else:
                    deleted +=1
                    
                    try:
                        os.remove(self.years_dir +'/' + quarter + '/'+ '{}.txt'.format(x[cik_idx]))
                    except:
                        pass
                    
            print  '-- no match for {} statements.'.format(deleted)
            
            os.remove(self.years_dir +'/' + quarter + '/'+ 'master_processed_{}.txt'.format(self.statement_type))
            
            with open(self.years_dir+'/' + quarter + '/'+ 'master_processed_{}.txt'.format(
                                        self.statement_type), 'wb' ) as file_in:
                
                reader = csv.writer(file_in, delimiter='|')
                
                for x in updated:
                    reader.writerow(x)
                    
    def link_data(self):
        
        return None
    





# TODO: setup so that the linked table with all data doesn't have to get linked every time
                    
        
            
            
                    
            
            
            
                
        

    
            
        
        
    

