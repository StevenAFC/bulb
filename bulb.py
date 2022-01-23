from python_graphql_client import GraphqlClient

class Bulb:

  def __init__(self, username, password, account) -> None:
    self.username = username
    self.password = password
    self.account = account
    self.token = ""

  def getToken(self):
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

    client = GraphqlClient(endpoint="https://account.bulb.co.uk/graphql")

    bulbdata = client.execute(query=query, variables=variables)

    self.token = bulbdata["data"]["login"]["details"]["idToken"]

  def retrieveBulbData(self, fromDate, toDate):

    if self.token == "":
      self.getToken()

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

    client = GraphqlClient(endpoint="https://gr.bulb.co.uk/graphql")

    headers = {
      "authorization" : "Bearer " + self.token
    }

    variables = {
      "accountId" : self.account,
      "fromDttm":fromDate,
      "toDttm":toDate
    }

    bulbdata = client.execute(query=query, variables=variables, headers=headers)

    if "errors" in bulbdata:
      print("Error: {}".format(bulbdata["errors"][0]["message"]))
      self.getToken()
      bulbdata = client.execute(query=query, variables=variables, headers=headers)
    
    print("Found {} records".format(len(bulbdata["data"]["data"])))

    return bulbdata["data"]["data"]