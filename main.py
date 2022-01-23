from datetime import datetime, timedelta
import sched, time
from bulb import Bulb
from db import Db
import os
from dotenv import load_dotenv

load_dotenv()

s = sched.scheduler(time.time, time.sleep)
rt = int(os.environ['REFRESH_TIME'])

bulb = Bulb(os.environ['BULB_USERNAME'], os.environ['BULB_PASSWORD'], int(os.environ['BULB_ACCOUNT']))
db = Db(os.environ['INFLUXDB_HOST'], os.environ['INFLUXDB_PORT'], os.environ['INFLUXDB_USERNAME'], os.environ['INFLUXDB_PASSWORD'], os.environ['INFLUXDB_DATABASE'])

print ("Bulb data gathering started, refreshing every {} seconds".format(rt))

def loop(sc):
    data = bulb.retrieveBulbData((datetime.today() - timedelta(days=6)).strftime('%Y-%m-%dT00:00:00.000Z'), (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%dT00:00:00.000Z'))
    
    db.insert(data, os.environ['INFLUXDB_DATABASE'], os.environ['INFLUXDB_MEASUREMENT'])

    s.enter(rt, 1, loop, (sc,))

s.enter(rt, 1, loop, (s,))

s.run()