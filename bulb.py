from python_graphql_client import GraphqlClient
from influxdb import InfluxDBClient
from configparser import ConfigParser
import time

config_object= ConfigParser()
config_object.read("config.ini")

client = GraphqlClient(endpoint="https://account.bulb.co.uk/graphql")

influxdbinfo = config_object["INFLUXDB"]

db = InfluxDBClient(
        host=influxdbinfo["host"],
        port=influxdbinfo["port"],
        username=influxdbinfo["username"],
        password=influxdbinfo["password"],
        database=influxdbinfo["database"]
    )

query = """
query usagePageData($accountId: Int!) {
  meterpoints(accountId: $accountId) {
    readings {
      ...meterReadingFragment
      __typename
    }
    __typename
  }
}

fragment meterReadingFragment on MeterReading {
  cumulative
  meter
  register
  quality
  readingDate
  source
  unit
  meterRegisterId
  sequenceType
  __typename
}
"""

bulbinfo = config_object["BULB"]

variables = {"accountId" : int(bulbinfo["accountId"])}

headers = {
"authorization" : bulbinfo['token']
}

bulbdata = client.execute(query=query, variables=variables, headers=headers)

def write_data(measurement, readings):
    data = []

    for reading in readings:
        
        data.append('{measurement} cumulative={cumulative},meter="{meter}",register="{register}",quality="{quality}",source="{source}",unit="{unit}",meterRegisterId={meterRegisterId},sequenceType="{sequenceType}" {timestamp}'.format(
            measurement=measurement,
            cumulative=reading['cumulative'], 
            meter=reading['meter'],
            register=reading['register'],
            quality=reading['quality'],
            source=reading['source'],
            unit=reading['unit'],
            meterRegisterId=reading['meterRegisterId'],
            sequenceType=reading['sequenceType'],
            timestamp=int(time.mktime(time.strptime(reading['readingDate'], '%Y-%m-%dT%H:%M:%S.000Z')))
            ))

    db.write_points(data, database="sensors", time_precision='s', protocol='line')

write_data(measurement=influxdbinfo["electricmeasurement"], readings=bulbdata['data']['meterpoints'][0]['readings'])
write_data(measurement=influxdbinfo["gasmeasurement"], readings=bulbdata['data']['meterpoints'][1]['readings'])