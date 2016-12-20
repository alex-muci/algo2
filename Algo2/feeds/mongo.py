#!/usr/local/bin/python2.7
# encoding: utf-8
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import quandl , os, logging, datetime, sys #, itertools
from pymongo import MongoClient
import pandas as pd 
import collections  # specialized container datatypes in alternative to built-in ones (e.g. dict, list, set, and tuple). 
                    # e.g. OrderedDict: dict subclass that remembers the order entries were added

quandl_dir = "C:/Users/Alessandro/Documents/Python-finance" # write your directory
my_api_key = open('%s/quandlapikey.txt' % quandl_dir,'r').read()
quandl.ApiConfig.api_key = my_api_key
 
contract_month_codes = ['F', 'G', 'H', 'J', 'K', 'M','N', 'Q', 'U', 'V', 'X', 'Z']
contract_month_dict = dict(zip(contract_month_codes,range(1,len(contract_month_codes)+1)))

############ CHECK mongo server is open  ############
MONGO_STAT =  "C:\\Progra~1\\MongoDB\\Server\\3.2\\bin\\mongostat.exe /rowcount:1" 
def check_mongo():
    pipe = os.popen(MONGO_STAT + ' 2>&1', 'r')
    text = pipe.read()
    if 'no reachable servers' in text:
        print("\n\n**** Mongo is NOT running, we stop here... ****\n\n") 
        exit()  # terminate here, don't execute following calls/fnctns
    else:
        print("\n\n**** Mongo is running! ****\n\n")
############ ############

# wrapper for quandl.get, or any other future one...
def web_download(contract,start,end):
    df = quandl.get(contract,trim_start=start,trim_end=end, returns="pandas" ) # ,authtoken=my_api_key)
    return df

def systemtoday():
    return datetime.datetime.today()   # yesterday = datetime.datetime.today() - datetime.timedelta(days=1)

##############################################    
############ using the database   ############
#
def get(market, sym, month, year, dt, MyDbCollection):
    """
    Returns one day data for a contract  
    """
#    connection = MongoClient(); db = connection[mydb]
    yearmonth = "%d%s" % (year,month)
    q = {"$query" :{"_id": {"sym": sym, "market": market, "month": month,"year": year, "yearmonth": yearmonth, "dt": dt } 
                    } 
         }
    res = list(MyDbCollection.find(q))
    return res  #

def get_one(market, sym, month, year, dt, MyDbCollection):
    """
    Returns one day data for a contract
    ...workaround...  
    """
#    connection = MongoClient(); db = connection[mydb]
    res = get_contract(market, sym, month, year, MyDbCollection)
    return res[dt:dt]


def get_contract(market, sym, month, year, MyDbCollection):
    """
    Returns all time series data for a futures contract [market, symbol+month+year] 
    in a pandas dataframe
    """
#    connection = MongoClient()
#    db = connection[mydb]
    yearmonth = "%d%s" % (year,month)
    q = {"$query" : {"_id.sym": sym, "_id.market": market, "_id.yearmonth": yearmonth },
         "$orderby":{"_id.dt" : 1} 
    }
    res = list(MyDbCollection.find(q))
    if len(res) == 0: return None
    res = pd.DataFrame(res)
    res['Date'] = res['_id'].map( lambda x: datetime.datetime.strptime( str(x["dt"]), '%Y%m%d' ) )  # .strptime returns a [datetime] corresponding to [date]_string, parsed according to format
    res = res.drop('_id',axis=1); res = res.set_index('Date')
    return res

def last_contract(sym, market, MyDbCollection):
    q = { "$query" : {"_id.sym": sym, "_id.market": market}, "$orderby":{"_id.yearmonth" : -1} }
    res = MyDbCollection.find(q).limit(1)    
    return list(res) 

def last_date_in_contract(sym, market, month, year, MyDbCollection):
    q = { "$query" : {"_id.sym": sym, "_id.market": market,
                      "_id.month": month, "_id.year": year},
          "$orderby":{"_id.dt" : -1}          
    }
    res = list(MyDbCollection.find(q).limit(1))
    if len(res) > 0: # return res[0]['_id']['dt'], or in pandas format as per below
        last_date = int(res[0]['_id']['dt'])
        return pd.to_datetime(str(last_date), format='%Y%m%d') 

def existing_nonexpired_contracts(sym, market, today, MyDbCollection):
    yearmonth = "%d%s" % (today.year,contract_month_codes[today.month-1])
    q = { "$query" : {"_id.sym": sym, "_id.market": market,
                      "_id.yearmonth": {"$gte": yearmonth } }
    }  
    res = {} # dictionary
    for x in MyDbCollection.find(q): res[(x['_id']['year'],x['_id']['month'])]=1
    return res.keys() # = yearmonth

def get_more_contracts(market, sym, from_year, to_year, db="findb"):
    """
    Get all contracts for a futures, jan to dec, 
    between (and including) given years,
    
    Returns: An ordered dictionary whose key is YYYYMM year-month code,
    and value is the contract in a dataframe.
    """
    res = collections.OrderedDict()
    for year in range(from_year,to_year+1):
        for month in contract_month_codes:
            c = get_contract(market=market, sym=sym, month=month, year=year, db=db)
            key = "%d%02d" % (year,contract_month_dict[month])
            if 'DataFrame' in str(type(c)): res[key] = c
    return res        


############ SINGLE contract load and save  ############
def download_and_save(work_items, db, downloader=web_download, today=systemtoday):
    for market, sym, month, year, work_start in work_items:      #work_items=[(market,code,month,int(year),'1900-01-01')]
        contract = "%s/%s%s%d" % (market,sym,month,year)  # e.g. CME/CLX2004
        try:
            logging.debug(contract)
            df = downloader(contract,work_start,today().strftime('%Y-%m-%d')) # get the data
            oicol = [x for x in df.columns if 'Open Interest' in x][0]  # sometimes oi is in 'Prev. Days Open Interest' sometimes just 'Open Interest', use whichever
            yearmonth = "%d%s" % (year,month)         
            logging.debug("%d records" % len(df))
            for i, srow in df.iterrows(): # format and save in the database
                dt = str(i)[0:10] #str(srow[0])[0:10]
                dt = int(dt.replace("-",""))
                new_row = {"_id": {"sym": sym, "market": market, "month": month,
                                   "year": year, "yearmonth": yearmonth, "dt": dt },
                           "o": srow.Open, #srow[1].Open,
                           "h": srow.High, #srow[1].High,
                           "l": srow.Low, # srow[1].Low,
                           "s": srow.Settle, # srow[1].Settle,
                           "v": srow.Volume, # srow[1].Volume,
                          "oi": srow[oicol] # #srow[1][oicol]
                }
                db.insert_one(new_row)# save(new_row)

        except quandl.QuandlError:
            logging.error("No dataset")
    
############ all futures in a filename.cvs  ############
def download_data(downloader=web_download,today=systemtoday,db="findb",years=(1984,2022),fin="futures.csv"):

    """
    Futures Contracts downloader - symbols are in argument fin (a csv
    file location), each symbol in this file is retrieved from Quandl
    and inserted into a Mongo database. At each new invocation, only
    new data for non-expired contracts are downloaded.
    """
    
    # a tuple of contract years, defining the beginning
    # of time and end of time
    start_year,end_year=years
    futcsv = pd.read_csv(fin,comment='#')
    instruments = zip(futcsv.symbol,futcsv.market)

    str_start = datetime.datetime(start_year-2, 1, 1).strftime('%Y-%m-%d')
#    str_end = today().strftime('%Y-%m-%d'); today_month,today_year = today().month, today().year
    
    connection = MongoClient()  #1. get connection
    futures = connection[db].futures # 2. database = connection.db_name or  = connection['db-name']   3. collection = database.collecton_name 

    work_items = []
        
    # download non-existing / missing contracts 
    # this is the case of running for the first time, or a new contract became available
    for (sym,market) in instruments:
        last = last_contract(sym, market, futures)   # last_contract(sym, market, db="findb"): return list(db.futures.find(q).limit(1))
        for year in range(start_year,end_year):
            for month in contract_month_codes:
                if len(last)==0 or (len(last) > 0 and last[0]['_id']['yearmonth'] < "%d%s" % (year,month)):
                    # for non-existing contracts, get as much as possible
                    # from str_start (two years from the beginning of time)
                    # until the end of time
                    work_items.append([market, sym, month, year, str_start])

        # for existing contracts, 
        # add to the work queue the download of additional days that are not there. 
        # if today is a new day, and for existing non-expired contracts, we would have new price data
        for (nonexp_year,nonexp_month) in existing_nonexpired_contracts(sym, market, today(), connection[db]):
            last_con = last_date_in_contract(sym,market,nonexp_month,nonexp_year,futures)
            last_con = pd.to_datetime(str(last_con), format='%Y%m%d')
            logging.debug("last date contract %s" % last_con)
            if today() > last_con: work_items.append([market, sym, nonexp_month, nonexp_year, last_con.strftime('%Y-%m-%d')])

    download_and_save(work_items, futures, downloader, today)

############ stitch all prices  ############
def shift(lst,empty):
    res = lst[:]
    temp = res[0]
    for index in range(len(lst) - 1): res[index] = res[index + 1]         
    res[index + 1] = temp
    res[-1] = empty
    return res
    
def stitch_prices(dfs, price_col, dates_arg, ctd):
    """Stitches together a list of contract prices. dfs should contain a
    list of dataframe objects, price_col is the column name to be
    combined, and dates is a list of stitch dates. The dataframes must
    be date indexed, and the order of dates must match the order of
    the dataframes. The stitching method is called the Panama method -
    more details can be found at
    http://qoppac.blogspot.de/2015/05/systems-building-futures-rolling.html
    """
    dates = dates_arg[:]
    
    res = []
    datesr = list(reversed(dates))
    dfsr = list(reversed(dfs))    
    dfsr_pair = shift(dfsr,pd.DataFrame())
        
    for i,v in enumerate(datesr):
        tmp1=float(dfsr[i].ix[v,price_col]) # 1990-09-26
        tmp2=float(dfsr_pair[i].ix[v,price_col])
        dfsr_pair[i].loc[:,price_col] = dfsr_pair[i][price_col] + tmp1-tmp2

    dates.insert(0,'1900-01-01')
    dates_end = shift(dates,'2200-01-01')
    
    for i,v in enumerate(dates):
        tmp = dfs[i][(dfs[i].index > dates[i]) & (dfs[i].index <= dates_end[i])]
        res.append(tmp[price_col])
    return pd.concat(res)
    
##############################
#    running from command line
##############################
if __name__ == "__main__":

    check_mongo()   
    logging.basicConfig(filename='%s/futures.log' % os.environ['TEMP'],level=logging.DEBUG, format='%(asctime)-15s: %(message)s')
    
    if  len(sys.argv) == 4 and sys.argv[1] == "--load-save-cnt":
        """
        Download from Quandl and load a single contract, example usage is:
        [THIS FILE].py --load-save-cnt CME CLX2004
            """
        x1,x1,market, cnt = sys.argv
        year=int(cnt[-4:]); mon=cnt[-5]; code=cnt[:-5]  # e.g. for CLX2004 --> year = 2004 ; mon = X ; code = CL
        connection = MongoClient()
        findb = connection["findb"]
        collectdb = findb.futures # connection["findb"].futures or connection.finddb.futures
        temp_start = '1900-01-01' 
        download_and_save(work_items=[(market,code,mon,int(year),temp_start)], db=collectdb)
        # write some checks...
        print("downloaded and saved: " + code+mon+year)
        
        
    elif len(sys.argv) == 3 and sys.argv[1] == "--load-cont":
        """
        futures.py --load-cont filename.csv - for each instrument in 
        filename.csv, call the carry, stitching method which will write
        the result in db.
        """
        print(sys.argv[2])
        insts = pd.read_csv(sys.argv[2],index_col=[0,1],comment='#').to_dict('index')
        for (sym,market) in insts.keys(): 
            print(sym, market)
#            combine_contract_info_save(sym, market, insts, db="findb")
                
    elif len(sys.argv) == 3 and sys.argv[1] == "--latest":
        """
        Simply get the latest for all items in a csv
        (by looping through the single instrument: download_and_save(...) )
        """
        print('Downloading the latest for %s...' % sys.argv[2])
#        download_data(fin=sys.argv[2])


#
# F - Jan, G - Feb, H - Mar, J - Apr, K - May, M - Jun
# N - Jul, Q - Aug, U - Sep, V - Oct, X - Nov, Z - Dec
#