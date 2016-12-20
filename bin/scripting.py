#!/usr/local/bin/python2.7
# encoding: utf-8
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)



import quandl, os, sys , datetime #, logging, itertools
# from pymongo import MongoClient
import pandas as pd 

##############################
#    running from command line
##############################
if __name__ == "__main__":

#   check_mongo()   
#   logging.basicConfig(filename='%s/futures.log' % os.environ['TEMP'],level=logging.DEBUG, format='%(asctime)-15s: %(message)s')
#   findb = connection["findb"]
#   collectdb = findb.futures # connection.finddb.futures
       
    if len(sys.argv) == 3 and sys.argv[1] == "--load-cont":
        """
        main.py --load-cont futures.csv 
        - for each instrument in future.csv, call the carry, stitching method 
        [which will write the result in db].
        """
#       print(sys.argv[2])
        insts ={} # e.g. insts[(sym,market)] = {'currency': "USD", 'point_size': 1, 'carryoffset': -1}
        insts = pd.read_csv(sys.argv[2],index_col=[0,1],comment='#').to_dict('index')
        for (sym,market) in insts.keys(): 
            print(sym, market)
#           combine_contract_info_save(sym, market, insts, collectdb)
