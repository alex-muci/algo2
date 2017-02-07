# encoding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import quandl, os#, itertools, sys

"""
name_file = 'quandlapikey.txt'  
directory =  os.path.dirname(os.path.abspath(sys.argv[0])) 
fname = os.path.join(directory , name_file)
"""
api_key = open('C:/Users/Alessandro/quandlapikey.txt','r').read()  # txt file saved in my usual directory
quandl.ApiConfig.api_key = api_key  # = "YOUR_KEY_HERE"

base_dir = "C:/Users/Alessandro/Downloads/futures"  # where to be saved


years = range(2016, 2017)    # range(1992,2022)
months = ['F', 'G', 'H', 'J', 'K', 'M','N', 'Q', 'U', 'V', 'W', 'Z']

#instruments = ['CME/CL'] # oil
#instruments = ['CME/KC'] # coffee
#instruments = ['CME/TY'] # US-10 treasury
instruments = ['CME/ED'] # eurodollar

for year in years:
    for month in months:
        for code in instruments:
            file_ = "%s%s%d" % (code,month,year)
            fout = base_dir + "/%s.csv" % file_.replace("/","-")
            print(file_)
            if os.path.isfile(fout):
                print("file exists, skipping...")
                continue
            try:
                df = quandl.get(file_, returns="pandas")    # ,authtoken=api_key)
            except quandl.NotFoundError:
                print("No dataset")
                continue
            print(fout)
            df.to_csv(fout)