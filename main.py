from datetime import datetime, timedelta
import bulb

##offset = 96
##maxdays = 500

##for x in range(offset, maxdays, 6):
##    bulb.retrieveBulbData((datetime.today() - timedelta(days=x)).strftime('%Y-%m-%dT00:00:00.000Z'), (datetime.today() - timedelta(days=x - 6)).strftime('%Y-%m-%dT00:00:00.000Z'))

bulb.retrieveBulbData((datetime.today() - timedelta(days=6)).strftime('%Y-%m-%dT00:00:00.000Z'), datetime.today().strftime('%Y-%m-%dT00:00:00.000Z'))

