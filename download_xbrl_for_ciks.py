# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 17:19:53 2018

@author: bhavy

@README: Download cik files for particular year, from the list of CIKS given in an Excel file. This program basically downloads zipfile for given cik and year.
This program must be executed before you try to run "download_xbrl_tag_data" program.
"""

import urllib
import sys
import os
import pandas as pd
import feedparser

'''
@downloadfile takes 2 inputs. 1) sourceurl which is url to be downloaded. and 2) targetfname which is the name by which we will save our downloaded url.
We have exception handling for three different types of exceptions: HTTP, URL, Timeout.
'''
def downloadfile(sourceurl,targetfname):
    mem_file=''
    good_read=False
    xbrlfile=None
    #check if file already exists, return true if it does.
    if os.path.isfile(targetfname):
        print("local copy already exists.")
        return True
    else:
        print("downloading source url", sourceurl)
        try:
            xbrlfile=urllib.request.urlopen(sourceurl)
            try:
                mem_file=xbrlfile.read()
                good_read=True
            finally:
                xbrlfile.close()
        except urllib.error.HTTPError as e:
            print("http error", e.code)
        except urllib.error.URLError as e:
            print("url error", e.reason)
        except TimeoutError as e:
            print("timeout error", e.reason)
        #If we are successfully able to read the URL, write it to our file. 
        if good_read:
            output=open(targetfname,'wb')
            output.write(mem_file)
            output.close()
        return good_read

'''
@get_list_of_ciks function takes input a filename, which contains all the CIKS that we want to download zip files for. We use pandas library to perform this
extraction.
'''
def get_list_of_ciks(filename):
    #Read excel file, it is important to mention Sheet1 or whichever Sheet we are dealing with.
    ExcelRead = pd.read_excel(filename,sheetname="Sheet1")
    #give the column name where we have stored ciks. Here, its 'a_cikn'.
    List_CIK = ExcelRead['a_cikn']
    String_of_ciks = []
    for i in List_CIK:
        String_of_ciks.append(str(i).zfill(10))
    return String_of_ciks
  
'''
@SECDownload takes input the year for which we want to download files.
'''
def SECDownload(year):
    
    for i in range(1,13):
        
        feedFile=None
        feedData=None
        good_read=False
        month = i
        edgarFeed='http://www.sec.gov/Archives/edgar/monthly/xbrlrss-' + str(year) + '-' + str(month).zfill(2) + '.xml'
#create directory if it doesnt exist.
        if not os.path.exists("sec/" + str(year)):
        		os.makedirs("sec/" + str(year))    
#target_dir is directory where you want the files to go.
        target_dir="sec/" + str(year) + "/"
        try:
            feedFile=urllib.request.urlopen(edgarFeed)
            try:
                feedData=feedFile.read()
                good_read=True
            finally:
                feedFile.close()
        except:
            print("HTTPError: ")
        feed=feedparser.parse(edgarFeed)
#get list of ciks that we want.
        listofciks = get_list_of_ciks("diss_samplecik20190321.xlsx")
        for item in feed.entries:
          #Proceed only if filing type is 10-K. Change for different filing types.
            if item['summary']=='10-K':
                try:
           #identify zip file enclosure, if available, used to check if we can download zip folders for given cik or not.
                  enclosures = [ l for l in item['links'] if l['rel']== 'enclosure']
                  if (len(enclosures)>0):
                           enclosure=enclosures[0]
                           sourceurl=enclosure['href']
                           cik=item['edgar_ciknumber']
                           #check if cik is in the list of ciks we have. proceed if it is.
                           if(cik in listofciks):
                               targetfname=target_dir+cik+'-'+sourceurl.split('/')[-1]
                               retry=3
                               while retry>0:
                                   good_read = downloadfile(sourceurl,targetfname)
                                   if good_read:
                                       break
                                       exit()
                                   else:
                                       print("retrying", retry)
                                       retry -= 1
                  else:                       
                           print("no url found")
                           sys.exit()
                except:
                   continue
            else:
                continue

#Enter year value for which you want to run this program.
print("Enter year for which you want the data: ")
year=input()
#call our main function
SECDownload(year)