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
import bs4
from bs4 import BeautifulSoup
import shutil
import logging as logger
import traceback
import unicodedata


def parse_year(year, statement  = '10-K' ):
    parser = StatementsParser(year, statement  = '10-K' )
    parser.get_list_statements()
    parser.start_parsing(maxnumber = 1000, clean = True, add_cleaning = True)
    

    
    

class StatementsParser(object):
    
    def __repr__(self):
        return 'This is the statements parser object for year: %i' % self.year
    
    def __init__(self, year, statement = '10-K', restart = True, thresholds = None):
        
        self.year = year
        self.statement_type = statement
        self.types=['graphic', 'zip', 'excel', 'pdf', 'ex']
        self.removeable_tags = ['div', 'tr', 'td', 'font']
        
        
        self.archive_link = 'https://www.sec.gov/Archives'
        self.total_tenks = 0
        
        self.restart = restart        
        
        self.thresholds = thresholds
        self.margin = 5
        
        if not thresholds:
            self.thresholds = {'alphanum': 0.05,
                               'tab': 0.05,
                               'space': 0.2,
                               'dots': 0.05, 
                               'underscores': 0.15
                    }
            
   
    
    def checktype(self,tag):
        
        unwanted_types = lambda x: any(x.lower().startswith(word) for word in self.types)
        
        return unwanted_types(tag)

    def _clean_html(self, soup):
    
        # step 1 outlined in internet appendix: removing certain types
        try:
            for tag in soup.find_all('type'):
                string = tag.get_text()
                if self.checktype(string):
                    #print string
                    tag.replaceWith('')
        except:
            pass
        
        #  step 2 outlined in internet appendix: removing illegal tags
        try:
            for illegal_tag in self.removeable_tags:
                for tag in soup.find_all(illegal_tag):
                    tag.replaceWithChildren()
        except:
            pass
                
        
        #  step 3 outlined in internet appendix: removing xml
        try:
            for e in soup:
                if isinstance(e, bs4.element.ProcessingInstruction):
                    e.extract()
                    break
        except:
            pass
                
        
        #  step 4 outlined in internet appendix: remove   <XBRL …> … </XBRL> 
        try:
            for tag in soup.find_all('xbrl'):
                tag.replaceWith('')
        except:
            pass
            
        #  step 5a. outlined in internet appendix: remove sec header 
        # TODO: 
        try:
        
            for tag in soup.find_all('sec-header'):
                header = tag
                tag.replaceWith('')
            
            old_version = soup.find_all('ims-header')
            
            if old_version:
                for tag in old_version:
                    header = tag
                    
                    tag.replaceWith('')
        except:
            pass
        
        # step 9
        try:
            count_numbers  = lambda x: sum(i.isdigit() for i in x)/float(len(x))
            for tag in soup.find_all('table'):
                
                string = tag.get_text().lower()
                
                if count_numbers(string) > 0.1:
                    if not ('item 7' in string or 'item 8' in string):
                        tag.replaceWith('')
        except:
            pass
            
        # get data from sec-document tags and convert to text
        
        try:
            text = soup.find_all('sec-document')[0].get_text()
            
            text = self._clean_text(text)
        except:
            text = soup.get_text()
            
            text = self._clean_text(text)
        
        return soup, header, text
    
    
    
    def _additional_cleaning(self, text):
            
        
        non_alpha= lambda x : sum(not i.isalpha() for i in x)/float(len(x))
        
        # cleaning redundant \n's
        text = [x.lstrip(' \t')for x in text]
        text = [x for x in text if (not x.startswith('\n'))
                                    and (non_alpha(x) < 0.25 or x.lower().strip().startswith('item'))                    
                                    and not x.lower().startswith('table of contents') 
                                    ]
        
        # clean up table of contents
        container = []
        txt = []
        temp = 0
        bysegment = False
        
        for i,x in enumerate(text):
            
           if x.lower().startswith('item') and len(container)< self.margin:
               container = []
           elif x.lower().startswith('item') and len(container) >= self.margin:
               txt.extend(container)
               container = []
        
        
           # check if line starts with item 
           if x.lower().startswith('item') and not bysegment:
               bysegment = True
               
           elif bysegment:
               container.append(x)
          
           else:
               txt.append(x)
       

        return txt
    
    
    
    def _clean_text(self, text):
        
        # temporarily store text
        with open('data/storage.txt', 'wb') as fl_write:
            fl_write.write(text.encode('utf-8'))
            fl_write.close()
        
        # read into a list
        with open('data/storage.txt', 'rb') as fl_read:
            doc = fl_read.readlines()
            
            
        
        # remove non ascii characters 
        newdoc = []
        for line in doc:
            
            line = line.replace('\&NBSP', ' ')
            line = line.replace('\&NBSP'.lower(), ' ')
            
            line = line.replace('\&#160', ' ')
            line = line.replace('\&AMP', '&')
            line = line.replace('\&#38', '&')
            line = line.decode('utf-8','ignore').encode('ascii', 'ignore')
            
            newdoc.append(line)
        
        if self.add_cleaning:
            newdoc = self._additional_cleaning(newdoc)
            

        return newdoc
        
        
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
                    if x[2] == self.statement_type :
                        writer.writerow(x) 
                        self.total_tenks+=1
                        
                    if self.statement_type == '10-K':
                        if x[2] == self.statement_type + '405':
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
        
        # Get the link to the archive, the directory on the computer for the 
        # years and the names of the quarters
        link = self.archive_link + '/edgar/full-index/'
        years_dir = self.years_dir = 'data/indexes/'
        
        # restart!
        if os.path.exists('data/indexes/' + str(self.year)):
            
            var = 'incorr'
            while var != 'y' and var !='n':
                if var != 'y' and var !='n' and var != 'incorr':
                    print 'Incorrect input, try again.'
                
                var = raw_input("\n Indexes already exist, restart? (y/n): ")
                
                if var == 'y':
                    
                    shutil.rmtree('data/indexes/'+ str(self.year))
                    print '\t Restarting...'
                    self.restart = True
                    break
                
                elif var == 'no':
                    print '\t Not restarting'
                    
                    self.restart = False
                    break
                    
        
        
        quarters = self.quarters = ['QTR'+ str(i) for i in xrange(1,5)]
            
        if not os.path.exists('data/indexes/'+str(self.year)):
            os.makedirs('data/indexes/'+str(self.year))
        
        if self.restart:
            fl = urllib.URLopener()
            
            # iterate over quarters in year and save filtered master file
            
            for quarter in quarters:
                
                try:
                    quarter_link = link + str(self.year) + '/'+ quarter + '/master.idx'
                    
                    directory= years_dir +str(self.year) + '/' + quarter 
                    
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                      
                    # load file from the internet and filter
                    fl.retrieve(quarter_link , directory + '/'+ 'master.txt')
                    self._obtain_correct_statements(directory )
                except:
                    
                    print '\n Something went wrong in year %s,  quarter %s'  \
                                        % (str(self.year),quarter) 
                
            say('\n \tfound {} of  {} \'s \n'. format(self.total_tenks, \
                                        self.statement_type,))
        
    def _parse_one(self, row, fl, quarter, directory, failed= False):
        
        # construct link and save file name
        temp = row[4]
        link = self.archive_link + '/' + temp 
        
        if failed:
            os.remove(directory + '/' + quarter + '/' + '{}.txt'.format(row[0]))
            
        filename = '{}.txt'.format(row[0]) if not failed else 'failed_{}.txt'.format(row[0])
        save_loc = directory + '/' + quarter + '/' + filename
        
        # check if already exists
        if os.path.isfile(save_loc):
            return False
        
        fl.retrieve(link, save_loc )
        
        return save_loc
    
    
    def _clean_one(self, save_loc):
        
        fl = open(save_loc, 'rb')
        raw_html = fl.read()
        os.remove(save_loc)
        
        soup = BeautifulSoup(raw_html, 'lxml')
        
        try:
            # soup = self.type_1(soup) or self.type_2(soup) or self.type_3(soup)
            soup, header, cleantext = self._clean_html(soup)
            
            if not soup:
                return None
            
        except:
            print 'exception occurred'
            return None
            
        
        fl_write = open(save_loc, 'wb')
        fl_write.write(''.join(cleantext))
        
        
        return None
            
    
    def start_parsing(self, maxnumber = None, clean = True, add_cleaning = False):
        '''
        Will open the link file and start parsting the statements.
        Only run after running get list statements.
        
        Will additionally keep track of which statements have been and have been attempted to 
        be parsed, 
        args:
            maxnumber --> (optional) maximum number per year you want to parse
            
        '''
        self.add_cleaning = add_cleaning
        directory = self.years_dir + str(self.year)
        quarters = self.quarters
        
        fl = urllib.URLopener()
        
        
        if maxnumber:
            maxno = int(maxnumber/4)
            
        # iterate over the quarters
        for quarter in quarters:
            
            loc = directory +'/' + quarter + '/' 
            files = len([name for name in os.listdir(loc) if os.path.isfile(os.path.join(loc, name))])
            
            if files > maxno + 2:
                print 'Use the --restart=True option with desired maximum number.'
                print 'Terminating...'
                return None
            
            
            with open(directory +'/' + quarter + '/'+ 'master_{}.txt'.format(
                                    self.statement_type),'rb' ) as file_in:
                
                reader = csv.reader(file_in, delimiter='|')
                header = next(reader)
                
                # keep track of which files have been parsed
                with open(directory +'/' + quarter + '/'+ 'master_processed_{}.txt'.format(
                                    self.statement_type), 'wb' ) as file_out:
            
                    
                    writer = csv.writer(file_out, delimiter='|')
                    writer.writerow(header)
                    
                    fails = 0
                    cntr = 0
                    for row in reader:
                        
                        if maxnumber:
                            cntr+=1 
                            if cntr > maxno:
                                break

                        # get statement 
                        try:
                            save_loc = self._parse_one(row, fl, quarter,
                                                       directory)
                            
                            if not save_loc:
                                cntr -= 1
                                continue
                            
                            if save_loc and clean:
                                self._clean_one(save_loc)
                            
                            
                            writer.writerow(row)
                            
                        except Exception, e:
                            
                            tb = traceback.format_exc()
                            
                            fails+=1
                            writer.writerow(row)
                            save_loc = self._parse_one(row, fl, quarter,
                                                      directory, failed = True)
                            
                            if not save_loc:
                                cntr -= 1
                                continue
                            
                            print tb
                            
                            continue 
                            
                        
                            
                    print '\t %s has had %i unparsable links'%(quarter, fails)
                    
                    
        
    def restart_parsing(self, maxnumber = None, clean = True, add_cleaning = False):
        
        self.add_cleaning = add_cleaning
        directory = self.years_dir + str(self.year)
        quarters = self.quarters
        
        fl = urllib.URLopener()
        
        if maxnumber:
            maxno = int(maxnumber/4)
        
        for quarter in quarters:
            
            with open(directory +'/' + quarter + '/'+ 'master_processed_{}.txt'.format(
                                        self.statement_type), 'rb' ) as file_out:
                
                processed = file_out.readlines()
                processed = [x.rstrip('\n') for x in processed]
                
                
                if len(processed)-1 >= maxno: 
                    print 'Maximum number reached in year {}, quarter {},  {} docs parsed. Increase maxno if you wish to continue.'.format(
                            self.year, quarter[-1], len(processed)-1)
                    print ''
                    
                    
                    continue
                else:
                    print '\tParsing {} additional statements.'.format(maxno - (len(processed)-1))
                    
                with open(directory +'/' + quarter + '/'+ 'master_{}.txt'.format(
                        self.statement_type),'rb' ) as file_in:
                    reader = csv.reader(file_in, delimiter='|')
                    
                    unprocessed = [x for i, x in enumerate(reader) if i > len(processed)]
                    
                fails = 0
                cntr = 0
                for row in unprocessed:

                    # get statement 
                    try:
                        save_loc = self._parse_one(row, fl, quarter,
                                                   directory)
                        
                        if not save_loc:
                            cntr -= 1
                            continue
                        
                        if save_loc and clean:
                            self._clean_one(save_loc)
                        
                        
                        processed.append('|'.join(row))
                        
                    except Exception, e:
                        
                        tb = traceback.format_exc()
                        
                        fails+=1
                        processed.append('|'.join(row))
                        save_loc = self._parse_one(row, fl, quarter,
                                                  directory, failed = True)
                        
                        if not save_loc:
                            cntr -= 1
                            continue
                        
                        print tb
                        
                        continue 
                        
                    if maxnumber:
                        cntr+=1 
                        if cntr > maxno:
                            break
                        
                # replace old processed file
                os.remove(directory +'/' + quarter + '/'+ 'master_processed_{}.txt'.format(
                                        self.statement_type))
                
                with open(directory +'/' + quarter + '/'+ 'master_processed_{}.txt'.format(
                                        self.statement_type), 'wb' ) as file_out:
                    
                    # write to file
                    for item in processed:
                        print>>file_out, item
                
                        
                print '\t %s has had %i unparsable links'%(quarter, fails)
                
                    
                 
                    
        
                    
                    
                    
                
# TODO: if SIC number not in 10- k, get it from the general page at the SEC
        
        
            
            
            
        
        