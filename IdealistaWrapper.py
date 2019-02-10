import json
import requests
import time
from requests.auth import HTTPBasicAuth
from Filter import Filter


class IdealistaWrapper:
    _BASE_URL = "https://api.idealista.com"
    _access_token = None
    _MAX_ITEMS_PER_PAGE = 50

    @staticmethod
    def _refresh_auth_token():
        url = IdealistaWrapper._BASE_URL + "/oauth/token"
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

    @staticmethod
    def _get_auth_token(refresh = False):
        if IdealistaWrapper._access_token == None or refresh == True:
            IdealistaWrapper._access_token = IdealistaWrapper._refresh_auth_token()
        
        return IdealistaWrapper._access_token

    @staticmethod
    def _get_query_parameters(filter):
        parameters = {}
        parameters["operation"] = "sale"
        parameters["propertyType"] = "homes"
        parameters["center"] = f"{filter.lat},{filter.lng}"
        parameters["distance"] = f"{filter.radius}"
        if filter.price_min:
            parameters["minPrice"] = f"{filter.price_min}"
        if filter.price_max:
            parameters["maxPrice"] = f"{filter.price_max}"
        if filter.size_min:
            parameters["minSize"] = f"{filter.size_min}"
        if filter.size_max:
            parameters["maxSize"] = f"{filter.size_max}"
        # parameters["sinceDate"] = f""
        parameters["order"] = "publicationDate"
        parameters["sort"] = "desc"
        parameters["maxItems"] = f"{IdealistaWrapper._MAX_ITEMS_PER_PAGE}"

        return parameters
    

    @staticmethod    
    def search_listings(filter):
        if filter.lat == None or filter.lng == None:
            print (f"Cant search idealista without geo coded location")
            return []

        url = IdealistaWrapper._BASE_URL + "/3.5/es/search"
        parameters = IdealistaWrapper._get_query_parameters(filter)

        token = IdealistaWrapper._get_auth_token()
        if token == None:
            return []

        listings = []
        current_page = 1
        retried = False
        try:
            while True:
                headers = {"Authorization": "Bearer " + token}
                parameters["numPage"] = f"{current_page}"
                response = requests.post(url, headers=headers, params=parameters)

                if response.status_code > 200:
                    print (f"error searching idealista. request was {response.url}. response is {str(response.text)}")
                    if (response.status_code >= 402 and response.status_code < 500) and retried == False:
                        # invalid/expired token try reaquiring a new token
                        print (f"trying to reaquire a new token")
                        token = IdealistaWrapper._get_auth_token(True)
                        if token == None:
                            print (f"Failed to reaquire new token")
                            break
                        retried = True
                        print (f"acquired new token")
                    else:
                        break
                else:
                    json_response = json.loads(response.text)
                    total_items = json_response["total"]
                    if current_page == 1:
                        print (f"Found {total_items} listings")

                    total_pages = json_response["totalPages"]
                    paginable = json_response["paginable"]
                    
                    if current_page >= total_pages or paginable == False:
                        break
                    
                    page_listings = json_response["elementList"]
                    listings.extend(page_listings)
                    current_page += 1

                time.sleep(1)

        except Exception as e:
            print (f"error searching idealista. response is {str(e)}")

        return listings


# def get_oauth_token():
#     url = "https://api.idealista.com/oauth/token"
#     apikey = "8u9a3d13oyitttsiuvyapg8ntyfzat9x"
#     secret = "ILh4o6SVz7SQ"
#     payload = {"grant_type": "client_credentials"}
#     token = None
#     try:
#         response = requests.post(url, auth=HTTPBasicAuth(apikey, secret), data=payload)
#         if response.status_code == 200:
#             response_json = json.loads(response.text)
#             token = response_json["access_token"]
#         else:
#             print (f"error acquiring idealista access token. response is {str(response)}")

#     except Exception as e:
#         print (f"error acquiring idealista access token. exception {str(e)}")

#     return token


# def search_api(url):
#     try:
#         t = search_api.token
#     except AttributeError:
#         search_api.depth = 0
#         search_api.token = get_oauth_token()
#         if search_api.token == None:
#             return None
    
#     response = None
#     try:
#         headers = {"Authorization": "Bearer " + search_api.token}
#         response = requests.post(url, headers=headers)
#         if response.status_code == 200:
#             pass
#         elif (response.status_code == 401 or response.status_code == 405) and search_api.depth == 0:
#             # invalid/expired token
#             search_api.token = get_oauth_token()
#             if search_api.token == None:
#                 return None
#             search_api.depth+=1
#             result = search_api(url)
#             search_api.depth-=1
#             return result
#         else:
#             print (f"error searching idealista. response is {str(response)}")
#     except Exception as e:
#         print (f"error searching idealista. response is {str(e)}")

#     return response.text

def test_idealista_warapper():
    # url = "http://api.idealista.com/3.5/es/search?center=40.42938099999995,-3.7097526269835726&country=es&maxItems=500&numPage=1&distance=452&propertyType=bedrooms&operation=rent"
    filter = Filter("Carrer d'en Carabassa, 2, Barcelona, Spain")
    filter.lat = "41.3797412"
    filter.lng = "2.179483"
    filter.radius = 500
    results = IdealistaWrapper.search_listings(filter)
    print(results)

if __name__ == "__main__":
    test_idealista_warapper()
