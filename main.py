from datetime import datetime, timedelta
import sched, time
import bulb
import os

s = sched.scheduler(time.time, time.sleep)
rt = int(os.environ['REFRESH_TIME'])

print ("Bulb data gathering started, refreshing every {} seconds".format(rt))

def loop(sc):
    bulb.retrieveBulbData((datetime.today() - timedelta(days=6)).strftime('%Y-%m-%dT00:00:00.000Z'), (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%dT00:00:00.000Z'))
    
    s.enter(rt, 1, loop, (sc,))

s.enter(rt, 1, loop, (s,))

s.run()