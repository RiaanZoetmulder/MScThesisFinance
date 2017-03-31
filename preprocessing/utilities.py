#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 15:23:04 2017

@author: Riaan
"""
import sys

# usefull print function
def say(s, stream=sys.stdout):
    stream.write("{}".format(s))
    stream.flush()