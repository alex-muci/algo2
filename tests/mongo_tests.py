from nose.tools import *
from Algo2.feeds.mongo import *


"""	UN-COMMENT THE WHOLE THING
def test_download():
	# logging.basicConfig(filename='%s/futures.log' % os.environ['TEMP'],level=logging.DEBUG, format='%(asctime)-15s: %(message)s')
	check_mongo()
	market_test = "CME"; cnt = "CLX2004"; temp_start = "2004-10-01"
	year=int(cnt[-4:]); mon=cnt[-5]; code=cnt[:-5]  # e.g. for CLX2004 --> year = 2004 ; mon = X ; code = CL
	dt = datetime.date(2004, 10, 19) #last-but-one date in the contract
	# get connection or client
	conn = MongoClient(); mytestdb = conn["testdb"]; testcollectdb = mytestdb.fake_test
	# download the whole contract
	download_and_save(work_items=[(market_test,code,mon,int(year),temp_start)], db=testcollectdb) 
	# check a couple of known values
	s = get_one(market_test, code, mon, year, dt, testcollectdb)
	assert_equal(s.iloc[0]['s'],53.29);assert_equal(s.iloc[0]['v'],76473.0)  
	# remove collections, so not duplicate
	testcollectdb.remove({}) 


def test_basic():
	print "I RAN!"

"""
