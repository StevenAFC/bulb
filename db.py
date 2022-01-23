from influxdb import InfluxDBClient
import time

class Db:

  def __init__(self, host, port, username, password, database) -> None:
    self.db = InfluxDBClient(
      host=host,
      port=port,
      username=username,
      password=password,
      database=database
    )

  def insert(self, data, database, measurement):

    data = []

    for reading in data:

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
        measurement=measurement,
        electricCost=electricCost, 
        electricStandingCharge=electricStandingCharge,
        gasCost=gasCost,
        gasStandingCharge=gasStandingCharge,
        timestamp=int(time.mktime(time.strptime(reading['date'], '%Y-%m-%dT%H:%M:%S.000Z')))
        ))

    self.db.write_points(data, database=database, time_precision='s', protocol='line')