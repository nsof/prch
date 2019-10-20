import json
import requests
import time
from requests.auth import HTTPBasicAuth
from Filter import PropertyFilter
from Property import Property
from Listing import Listing


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
        parameters["center"] = f"{filter.property.latitude},{filter.property.longitude}"
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
    def _convert(idealista_listing, filter):
        listing = Listing(filter)
        listing.source = "idealista"
        listing.price = idealista_listing["price"] if "price" in idealista_listing else None
        listing.size = idealista_listing["size"] if "size" in idealista_listing else None
        listing.rooms = idealista_listing["rooms"] if "rooms" in idealista_listing else None
        listing.floor = idealista_listing["floor"] if "floor" in idealista_listing else None
        listing.hasLift = idealista_listing["hasLift"] if "hasLift" in idealista_listing else None
        listing.bathrooms = idealista_listing["bathrooms"] if "bathrooms" in idealista_listing else None
        listing.property_type = idealista_listing["propertyType"] if "propertyType" in idealista_listing else None
        listing.updated_in_days = None
        listing.url = idealista_listing["url"] if "url" in idealista_listing else None
        if "ParkingSpace" in idealista_listing:
            parking_space = idealista_listing["ParkingSpace"]
            if "hasParkingSpace" in parking_space:
                listing.parking_spaces = 1
                if "isParkingSpaceIncludedInPrice" in parking_space and parking_space["isParkingSpaceIncludedInPrice"] == False:
                    listing.price += parking_space["parkingSpacePrice"] if "parkingSpacePrice" in parking_space else 0
            else:
                listing.parking_spaces = 0
        listing.address = idealista_listing["address"] if "address" in idealista_listing else None
        listing.neighborhood = idealista_listing["neighborhood"] if "neighborhood" in idealista_listing else None
        listing.district = idealista_listing["district"] if "district" in idealista_listing else None
        listing.province = idealista_listing["province"] if "province" in idealista_listing else None
        listing.country = idealista_listing["country"] if "country" in idealista_listing else None
        listing.latitude = idealista_listing["latitude"] if "latitude" in idealista_listing else None
        listing.longitude = idealista_listing["longitude"] if "longitude" in idealista_listing else None
        listing.source_id = idealista_listing["propertyCode"] if "propertyCode" in idealista_listing else None
        return listing


    @staticmethod    
    def search_listings(filter):
        print(f"--- Searching Idealista ---")

        if filter.property.latitude == None or filter.property.longitude == None:
            print (f"    Cant search idealista without geocoded location")
            return []

        url = IdealistaWrapper._BASE_URL + "/3.5/es/search"
        parameters = IdealistaWrapper._get_query_parameters(filter)

        print (f"    Geting authorization token")
        token = IdealistaWrapper._get_auth_token()
        if token == None:
            return []

        listings = []
        current_page = 1
        retried = False
        try:
            while True:
                print(f"    Getting page number {current_page}", end="")

                headers = {"Authorization": "Bearer " + token}
                parameters["numPage"] = f"{current_page}"
                response = requests.post(url, headers=headers, params=parameters)

                if response.status_code > 200:
                    print (f"    error searching idealista. request was {response.url}. response is {str(response.text)}")
                    if (response.status_code >= 402 and response.status_code < 500) and retried == False:
                        # invalid/expired token try reaquiring a new token
                        print (f"    trying to reaquire a new token")
                        token = IdealistaWrapper._get_auth_token(True)
                        if token == None:
                            print (f"    Failed to reaquire new token")
                            break
                        retried = True
                        print (f"    acquired new token")
                    else:
                        break
                else:
                    json_response = json.loads(response.text)
                    total_items = json_response["total"]
                    if current_page == 1:
                        print (f"    Found {total_items} listings")
                    else:
                        print (f"")

                    total_pages = json_response["totalPages"]
                    paginable = json_response["paginable"]

                    page_listings = json_response["elementList"]
                    listings.extend(page_listings)
                    
                    if current_page >= total_pages or paginable == False:
                        break
                    
                    current_page += 1

                time.sleep(1)

        except Exception as e:
            print (f"    error searching idealista. response is {str(e)}")

        listings = [IdealistaWrapper._convert(listing, filter) for listing in listings]
        return listings


def test_idealista_warapper():
    # url = "http://api.idealista.com/3.5/es/search?center=40.42938099999995,-3.7097526269835726&country=es&maxItems=500&numPage=1&distance=452&propertyType=bedrooms&operation=rent"
    property = Property(location="Ciutat vella, Valencia, Spain")
    property.latitude = "41.3797412"
    property.latitude = "2.179483"
    filter = PropertyFilter(property)
    filter.radius = 50
    results = IdealistaWrapper.search_listings(filter)
    print(results)

if __name__ == "__main__":
    test_idealista_warapper()
