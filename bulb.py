from asyncio.windows_events import NULL
from python_graphql_client import GraphqlClient
from influxdb import InfluxDBClient
from configparser import ConfigParser
import time

config_object= ConfigParser()
config_object.read("config.ini")

client = GraphqlClient(endpoint="https://gr.bulb.co.uk/graphql")

influxdbinfo = config_object["INFLUXDB"]

db = InfluxDBClient(
        host=influxdbinfo["host"],
        port=influxdbinfo["port"],
        username=influxdbinfo["username"],
        password=influxdbinfo["password"],
        database=influxdbinfo["database"]
    )

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

bulbinfo = config_object["BULB"]

headers = {
"authorization" : bulbinfo['token']
}

def retrieveBulbData(fromDate, toDate):

  variables = {
    "accountId" : int(bulbinfo["accountId"]),
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
      electricCost = NULL
      electricStandingCharge=NULL

    if reading['usage']['gas']['cost'] != None :
      gasCost=reading['usage']['gas']['cost'] - reading['usage']['gas']['rates'][1]['cost']
      gasStandingCharge=reading['usage']['gas']['rates'][1]['cost']
    else:
      gasCost=NULL
      gasStandingCharge=NULL

    data.append('{measurement} electricCost={electricCost},electricStandingCharge={electricStandingCharge},gasCost={gasCost},gasStandingCharge={gasStandingCharge} {timestamp}'.format(
      measurement=influxdbinfo["measurement"],
      electricCost=electricCost, 
      electricStandingCharge=electricStandingCharge,
      gasCost=gasCost,
      gasStandingCharge=gasStandingCharge,
      timestamp=int(time.mktime(time.strptime(reading['date'], '%Y-%m-%dT%H:%M:%S.000Z')))
      ))
  
  db.write_points(data, database="sensors", time_precision='s', protocol='line')