#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
main loop
"""
from options import load_arguments
from utilities import say
from parser import parse_year
from linker import link_year
import time

def main():
    
    ########### Parse Mode ###########
    if args.mode == 'parse':
        # command : python main.py --mode=parse --years 1994
        print 'Starting Parsing'
        
        # if list empty set all years
        if not args.years:
            args.years = [1994 + i for i in range(23)]
            
        print '\nParsing the years:\n '
        for value in args.years:
            print '\t {}\n '.format(value)
            
        start = time.time()


                
        for year in args.years:
            say('\ncurrently parsing year: {}\n'.format(year))
            parse_year(year)
            
        end = time.time()
        print 'Time elapsed: {}'.format(end -start)
        say('\nFinished! \n')

    ########### Link Mode ###########
    elif args.mode == 'link':
        
        # command : python main.py --mode=link --years 1994
        print 'Starting Linking'
        
        if not args.years:
            args.years = [1994 + i for i in range(23)]
            
        print '\nLinking CIK to CUSIP codes to the years:'
        for value in args.years:
            print '\t {}\n'.format(value)
            
        start = time.time()
        
        for year in args.years:
            say('\ncurrently parsing year: {}\n'.format(year))
            link_year(year)
            
        end = time.time()
        print 'Time elapsed: {}'.format(end -start)
        
        say('\nFinished! \n')
        

        
        
    ########### Label Mode ###########
    elif args.mode == 'label':
        raise NotImplementedError
        
        
        
    ########### Train Mode ###########
    elif args.mode == 'train':
        raise NotImplementedError
        
        
        
        
    ########### Extract Mode ###########
    elif args.mode == 'extract':
        raise NotImplementedError
        
        
    else:
        print 'You have specified an unknown mode'
        return 
    
    return 
                
            
            
            
            
            
            
            
        
    return None
if __name__=='__main__':
    
    args = load_arguments()
    
    main()