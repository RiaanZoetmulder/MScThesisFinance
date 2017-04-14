#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
Options for the parser

Author: Riaan
'''

import sys
import argparse

def load_arguments():
    argparser = argparse.ArgumentParser(sys.argv[0])
    argparser.add_argument("--mode",
            type = str,
            default = None,
            help = "Indicate which mode: parse, link, label, train or extract",
            required = True
        )
    argparser.add_argument("--years",
            nargs='*', type=int,
            help = "indicate which years will be parsed: pass a list of integers, empty list means all will be parsed"
        )
    
    # TODO: Add more options as parser grows
    
    args = argparser.parse_args()
    return args