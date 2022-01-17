from datetime import datetime, timedelta
import sched, time
import bulb
import os

s = sched.scheduler(time.time, time.sleep)

def loop(sc):
    bulb.retrieveBulbData((datetime.today() - timedelta(days=6)).strftime('%Y-%m-%dT00:00:00.000Z'), (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%dT00:00:00.000Z'))
    
    s.enter(900, 1, loop, (sc,))

s.enter(900, 1, loop, (s,))

s.run()