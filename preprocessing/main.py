#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
main loop
"""
from options import load_arguments
from utilities import say
from parser import parse_year

def main():
    
    ########### Parse Mode ###########
    
    if args.mode == 'parse':
        
        print 'Starting Parsing'
        
        # if list empty or not
        if not args.years:
            raise NotImplementedError
            
        else:
            print '\nParsing the years:'
            for value in args.years:
                print '\t {}'.format(value)
                
            for year in args.years:
                say('\ncurrently parsing year: {}'.format(year))
                parse_year(year)
            
            say('\n')
                
                
                
                
                
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