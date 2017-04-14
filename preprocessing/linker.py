#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 15:43:41 2017

@author: Riaan
"""

import csv
import os
import sys 


def link_year(year, statement  = '10-K' ):
    linker = DataLinker(year)
    linker.verify_exists()
    


class DataLinker(object):
    
    def __repr__(self):
        return 'This is the linker object for year: %i' % self.year
    
    
    def __init__(self, year, statement = '10-K', restart = True, thresholds = None):
        
        self.year = year
        
        
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
            
    
            
        
        
    

