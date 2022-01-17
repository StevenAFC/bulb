from python_graphql_client import GraphqlClient
from influxdb import InfluxDBClient
import time
import os

def retrieveBulbData(fromDate, toDate):

  query = """
    query halfHourlyUsageData(
      $accountId: Int!
      $fromDttm: String!
      $toDttm: String!
    ) {
      data: halfHourlyUsageData(
        accountId: $accountId
        fromDttm: $fromDttm
        toDttm: $toDttm
      ) {
        date
        usage {
          electricity {
            cost
            rates {
              name
              cost
              __typename
            }
            __typename
          }
          gas {
            cost
            rates {
              name
              cost
              __typename
            }
            __typename
          }
          __typename
        }
        __typename
      }
    }
    """

  client = GraphqlClient(endpoint="https://gr.bulb.co.uk/graphql")

  db = InfluxDBClient(
    host=os.environ['INFLUXDB_HOST'],
    port=os.environ['INFLUXDB_PORT'],
    username=os.environ['INFLUXDB_USERNAME'],
    password=os.environ['INFLUXDB_PASSWORD'],
    database=os.environ['INFLUXDB_DATABASE']
  )

  headers = {
    "authorization" : os.environ['BULB_TOKEN']
  }

  variables = {
    "accountId" : int(os.environ['BULB_ACCOUNT']),
    "fromDttm":fromDate,
    "toDttm":toDate
  }

  bulbdata = client.execute(query=query, variables=variables, headers=headers)

  data = []

  print("Found {} records".format(len(bulbdata["data"]["data"])))

  for reading in bulbdata["data"]["data"]:

    if reading['usage']['electricity']['cost'] != None :
      electricCost = reading['usage']['electricity']['cost']
      electricStandingCharge=reading['usage']['electricity']['rates'][1]['cost']
    else :
      electricCost = 0
      electricStandingCharge=0

    if reading['usage']['gas']['cost'] != None :
      gasCost=reading['usage']['gas']['cost'] - reading['usage']['gas']['rates'][1]['cost']
      gasStandingCharge=reading['usage']['gas']['rates'][1]['cost']
    else:
      gasCost= 0
      gasStandingCharge= 0

    data.append('{measurement} electricCost={electricCost},electricStandingCharge={electricStandingCharge},gasCost={gasCost},gasStandingCharge={gasStandingCharge} {timestamp}'.format(
      measurement=os.environ['INFLUXDB_MEASUREMENT'],
      electricCost=electricCost, 
      electricStandingCharge=electricStandingCharge,
      gasCost=gasCost,
      gasStandingCharge=gasStandingCharge,
      timestamp=int(time.mktime(time.strptime(reading['date'], '%Y-%m-%dT%H:%M:%S.000Z')))
      ))
  
  db.write_points(data, database="sensors", time_precision='s', protocol='line')