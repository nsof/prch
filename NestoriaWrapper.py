import math
import urllib
import json
import requests
from Listing import Listing
from Property import Property
from Filter import PropertyFilter


class NestoriaWrapper:

    @staticmethod
    def _convert(nestoria_listing, filter):
        listing = Listing(filter)
        listing.source = "nestoria"
        listing.price = nestoria_listing["price"] if "price" in nestoria_listing else None
        listing.size = nestoria_listing["size"] if "size" in nestoria_listing else None
        listing.rooms = nestoria_listing["bedroom_number"] if "bedroom_number" in nestoria_listing else None
        listing.floor = nestoria_listing["floor"] if "floor" in nestoria_listing else None
        listing.hasLift = None
        listing.bathrooms = nestoria_listing["bathroom_number"] if "bathroom_number" in nestoria_listing else None
        listing.property_type = nestoria_listing["property_type"] if "property_type" in nestoria_listing else None 
        listing.updated_in_days = nestoria_listing["updated_in_days"] if "updated_in_days" in nestoria_listing else None
        listing.url = nestoria_listing["lister_url"] if "lister_url" in nestoria_listing else None 
        listing.parking_spaces = nestoria_listing["car_spaces"] if "car_spaces" in nestoria_listing else None
        listing.address = None
        listing.neighborhood = None
        listing.district = None
        listing.province = None
        listing.country = None
        listing.latitude = nestoria_listing["latitude"] if "latitude" in nestoria_listing else None 
        listing.longitude = nestoria_listing["longitude"] if "longitude" in nestoria_listing else None 
        listing.source_id = None
        return listing


    @staticmethod
    def _prepare_parameters(filter, page_size, page_number):
        parameters = {}
        parameters["action"] = "search_listings"
        parameters["encoding"] = "json"
        parameters["listing_type"] = "buy"
        parameters["sort"] = "newest"
        parameters["country"] = "es"
        parameters["pretty"] = 1
        parameters["number_of_results"] = page_size
        parameters["page"] = page_number
        if filter.property.lattitude != None and filter.property.longitude != None and filter.radius != None:
            parameters["radius"] = f"{filter.property.lattitude},{filter.property.longitude},{filter.radius/1000.0}km"
        else:
            parameters["place_name"] = filter.property.location

        if filter.price_max:
            parameters["price_max"] = filter.price_max
        if filter.price_min:
            parameters["price_min"] = filter.price_min
        if filter.size_max:
            parameters["size_max"] = filter.size_max
        if filter.size_min:
            parameters["size_min"] = filter.size_min

        # parameters['south_west'] = south_west
        # parameters['north_east'] = north_east
        # parameters['property_type'] = property_type
        # parameters['bedroom_max'] = bedroom_max
        # parameters['bedroom_min'] = bedroom_min
        # parameters['keywords'] = keywords
        # parameters['keywords_exclude'] = keywords_exclude
        return parameters


    @staticmethod
    def search_listings_page(filter, page_size, page_number):
        NESTORIA_API_URL = "https://api.nestoria.es/api"
        
        try:
            parameters = NestoriaWrapper._prepare_parameters(filter, page_size, page_number)
            response = requests.get(NESTORIA_API_URL, params=parameters, verify=False)

            # Check if API call worked
            if response.status_code != 200:
                if response.status_code == 400:
                    print(f"    - Bad request for {filter.property.location}. Check that this area is searchable on Nestoria website")
                elif response.status_code == 403:
                    print(f"    - API call was forbidden. Reached maximum calls")
                else:
                    print(f"    - Something else went wrong. HTTP response code is {response.status_code}")
                print(f"    - Url was: {response.url}")
                return [], 0

            json_results = json.loads(response.text)

            if int(json_results["response"]["application_response_code"]) >= 200:
                print(f"\n    - Error getting data")
                print(f"    - Application Response code: {json_results['response']['application_response_code']}")
                print(f"    - Response message: {json_results['response']['application_response_text']}")
                print(f"    - Url was: {response.url}")
                return [], 0

            listings = json_results["response"]["listings"]

            # filter listings based on date
            listings = [listing for listing in listings if int(listing["updated_in_days"]) <= filter.days_ago ]

            number_of_listings = json_results["response"]["total_results"]

            return listings, number_of_listings

        except Exception as e:
            print(f"    Something threw an exception. Error message: {str(e)}")

        return [], 0


    @staticmethod
    def search_all_listings(filter):
        print(f"--- Searching Nestoria ---")

        if filter.property.location == None and (filter.property.latitude == None or filter.property.longitude == None):
            print(f"    location or (lat,lng) must be set to search nestoria")
            return []

        page_number = 1
        page_size = 50
        listings = []
        number_of_listings = 0

        while True:
            if page_number == 1:
                print(f"    Getting first {page_size} listings...", end="")
            else:
                print(f"    Getting listings {(page_number-1)*page_size+1}-{min((page_number)*page_size, number_of_listings)}...", end="")

            page_listings, number_of_listings = NestoriaWrapper.search_listings_page(filter, page_size, page_number)
            listings.extend(page_listings)

            number_of_pages = int(math.floor((number_of_listings - 1) / page_size + 1))
            expected_number_of_page_listings = page_size
            if page_number == number_of_pages:
                expected_number_of_page_listings = (number_of_listings - (number_of_pages - 1) * page_size)

            if number_of_listings > 0:
                print(f"  Got {len(page_listings)}/{expected_number_of_page_listings} listings", end="")
                if page_number == 1:
                    print(f" of total >>> {number_of_listings} <<< listings ", end="")

                if len(page_listings) < page_size:
                    if len(page_listings) < expected_number_of_page_listings:
                        print(f" the rest were not in the last {filter.days_ago} days", end="")

                    print(f"")
                    break
            else:
                print(f"")
                break

            print(f"")
            page_number += 1

        if len(listings) > 0:
            print(f"    Total {len(listings)} listing for {filter.property.location}")

        listings = [NestoriaWrapper._convert(nestoria_listing=listing, filter=filter) for listing in listings]
        return listings


import pprint
def test_search_all_listings():
    property = Property(location="Ciutat vella, Valencia, Spain")
    filter = PropertyFilter(property=property, price_max=100000)
    results = NestoriaWrapper.search_all_listings(filter)
    pprint.pprint(results, width=1)

if __name__ == "__main__":
    test_search_all_listings()
