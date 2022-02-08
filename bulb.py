from asyncio.windows_events import NULL
from python_graphql_client import GraphqlClient

class Bulb:

  def __init__(self, username, password, account) -> None:
    self.username = username
    self.password = password
    self.account = account
    self.token = ""
    self.errorCount = 0

  def setToken(self):
    query = """
      mutation login($username: String!, $password: String!, $accountId: Int) {
        login(
          username: $username
          password: $password
          loginOptions: { useBulbAuth: true }
        ) {
          errorMessage
          errorType
          details {
            accessToken
            expiresIn
            scope
            idToken
            tokenType
            __typename
          }
          config {
            ...configFragment
            __typename
          }
          __typename
        }
      }
      fragment configFragment on Config {
        ...featureTogglesFragment
        __typename
      }
      fragment featureTogglesFragment on Config {
        featureToggles(
          names: [
          ]
          accountId: $accountId
        ) {
          __typename
        }
        __typename
      }
      """

    variables = {
      "username" : self.username,
      "password":self.password,
    }

    try:
      client = GraphqlClient(endpoint="https://account.bulddddddddddddddddddddddb.co.uk/graphql")
      bulbdata = client.execute(query=query, variables=variables)

      self.token = bulbdata["data"]["login"]["details"]["idToken"]
    except:
      print("Unable to connect to Bulb to retrieve token")



  def retrieveBulbData(self, fromDate, toDate):

    if self.token == "":
      self.setToken()
      
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
    variables = {
      "username" : self.account,
      "password":fromDate,
      "toDttm":toDate
    }

    client = GraphqlClient(endpoint="https://gr.bulddddddddddddddddddb.co.uk/graphql")

    headers = {
      "authorization" : "Bearer " + self.token
    }

    variables = {
      "accountId" : self.account,
      "fromDttm":fromDate,
      "toDttm":toDate
    }

    bulbdata = NULL
    try:
      bulbdata = client.execute(query=query, variables=variables, headers=headers)
    except:
      print("Unable to connect to Bulb to retrieve data")
      
    if bulbdata:
      if "errors" in bulbdata:
        print("Error - retrieving Bulb data: {}".format(bulbdata["errors"][0]["message"]))
        self.setToken()
        self.errorCount += 1
        self.retrieveBulbData(fromDate, toDate)
        if self.errorCount >= 3:
          print("Error - retrieving Bulb data: Failed to retrieve data from Bulb after 3 attempts in a row")
          return False
      else:
        self.errorCount = 0
        print("Found {} records".format(len(bulbdata["data"]["data"])))
        return bulbdata["data"]["data"]