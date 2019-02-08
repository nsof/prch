"""Idealista Explorer
Use the idealista.com API to run queries
(c) 2017 Marcelo Novaes
"""

import json
import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "https://api.idealista.com/"


def get_oauth_token():
    """Gets oauth2 token from the API Key and Secret provided by idealista
    """
    path = "oauth/token"
    url = BASE_URL + path
    apikey = "8u9a3d13oyitttsiuvyapg8ntyfzat9x"
    secret = "ILh4o6SVz7SQ"
    payload = {"grant_type": "client_credentials"}
    token = None
    try:
        response = requests.post(url, auth=HTTPBasicAuth(apikey, secret), data=payload)
        if response.status_code == 200:
            response_json = json.loads(response.text)
            token = response_json["access_token"]
        else:
            print (f"error acquiring idealista access token. response is {str(response)}")

    except Exception as e:
        print (f"error acquiring idealista access token. exception {str(e)}")

    return token

def search_api(url):
    """Runs a search using the API and a token
    """
    try:
        t = search_api.token
    except AttributeError:
        search_api.depth = 0
        search_api.token = get_oauth_token()
        if search_api.token == None:
            return None
    try:
        headers = {"Authorization": "Bearer " + search_api.token}
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            pass
        elif response.status_code == 401 and search_api.depth == 0:
            # invalid/expired token
            search_api.token = get_oauth_token()
            if search_api.token == None:
                return None
            search_api.depth+=1
            result = search_api(url)
            search_api.depth-=1
            return result
        else:
            print (f"error searching idealista. response is {str(response)}")
    except Exception as e:
        print (f"error searching idealista. response is {str(e)}")

    return response.text


def test_idealista_warapper():

    url = "http://api.idealista.com/3.5/es/search?center=40.42938099999995,-3.7097526269835726&country=es&maxItems=500&numPage=1&distance=452&propertyType=bedrooms&operation=rent"
    results = search_api(url)
    print(results)

if __name__ == "__main__":
    test_idealista_warapper()
