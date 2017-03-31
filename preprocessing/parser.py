#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Edgar Parser Class
Parses historical 10-K files and strips them of anything that is not text

Author: Riaan Zoetmulder
"""

import os 
import urllib
import csv
from utilities import say

def parse_year(year):
    parser = StatementsParser(year)
    parser.get_list_statements()

class StatementsParser(object):
    
    def __init__(self, year, statement = '10-K'):
        
        self.year = year
        self.statement_type = statement
        
        self.archive_link = 'https://www.sec.gov/Archives'
        self.total_tenks = 0
        
    def _obtain_correct_statements(self, link):
        with open(link + '/'+ 'master.txt', 'rb') as csvfile:
            
            reader = csv.reader(csvfile, delimiter='|')
            
            with open(link +'/'+ 'master_{}.txt'.format(self.statement_type), 'wb' ) as file_out:
                writer = csv.writer(file_out, delimiter = '|')
            
                # skip the docstring
                for x in range(9):
                    next(reader, None)
                    
                # get the header
                header = next(reader)
                
                # skip over line in between
                next(reader, None)
                
                writer.writerow(header)
                for x in reader:
                    if x[2] ==self.statement_type:
                        writer.writerow(x) 
                        self.total_tenks+=1
                
                file_out.close()
            csvfile.close()
            
        os.remove(link + '/'+ 'master.txt')
                    

        
    def get_list_statements(self):
        '''
        Get the list of all statements and filter out all of the files which are 
        not the financial statement.
        '''
        link = self.archive_link + '/edgar/full-index/'
            
        if not os.path.exists('data/indexes/'+str(self.year)):
            os.makedirs('data/indexes/'+str(self.year))
        
        fl = urllib.URLopener()
        
        # iterate over quarters in year and save filtered master file
        for quarter in ['QTR'+ str(i) for i in xrange(1,5)]:
            
            try:
                quarter_link = link + str(self.year) + '/'+ quarter + '/master.idx'
                
                directory= 'data/indexes/'+str(self.year) + '/' + quarter 
                
                if not os.path.exists(directory):
                    os.makedirs(directory)
                  
                # load file from the internet and filter
                fl.retrieve(quarter_link , directory + '/'+ 'master.txt')
                self._obtain_correct_statements(directory )
            except:
                
                print '\n Something went wrong in year %s,  quarter %s'  \
                                    % (str(self.year),quarter) 
            
        say('\n \tfound {} of  {} \'s'. format(self.total_tenks, \
                                    self.statement_type,))
            
            
            
        
        