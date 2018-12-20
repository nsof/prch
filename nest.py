import json
import csv
import datetime
import re
import math
import urllib
from urllib.parse import urlencode
from urllib.request import urlopen


############################################################################################################
# ===========================================================================================================
class Filter:
   def __init__(self, location, size_min=None, size_max=None, price_min=None, price_max=None, lng=None, lat=None, radius=None, days_ago=None):
      self.location = location
      self.size_min = size_min
      self.size_max = size_max
      self.price_min = price_min
      self.price_max = price_max
      self.lat = lat
      self.lng = lng
      self.radius = radius if radius != None else 1
      self.days_ago = days_ago if days_ago != None else 183


class GeocodeResponse:
   def __init__(self):
      self.lat = None
      self.lng = None
      self.accuracy = None
      self.postal_code = "Not found"

# ===========================================================================================================
def get_file_writer():
   file_name = "listings." + datetime.datetime.now().strftime("%Y-%m-%dT%H%M%S") + ".csv"
   output_file = open(file_name, "w", newline="", encoding="utf-8")
   field_names = ["location", "postal_code", "accuracy", "price", "size", "updated_in_days", "lister_url", "lister_name"
                  "bathroom_number", "bedroom_number", "car_spaces", "commission",
                  "construction_year", "datasource_name", "floor", "keywords", "latitude",
                  "listing_type", "location_accuracy", "longitude",
                  "price_currency", "price_formatted", "price_high",
                  "price_low", "property_type", "room_number", "size_type",
                  "size_unit", "summary", "title", "updated_in_days_formatted"]
   file_writer = csv.DictWriter(output_file, field_names, restval="",
                                extrasaction="ignore", quoting=csv.QUOTE_MINIMAL, dialect="excel")
   file_writer.writeheader()
   return output_file, file_writer

# ===========================================================================================================


def get_queries(file_name):
   # filed_names = ["location", "size_min", "size_max", "price_min", "price_max", "radius"]
   queries = []
   with open(file_name, "r", newline="", encoding="utf-8") as input_file:
      file_reader = csv.DictReader(input_file)
      queries = [query for query in file_reader]

   return queries

# ===========================================================================================================

def geocode(filter):
   url = 'https://maps.googleapis.com/maps/api/geocode/json?'
   parameters = {"address": f"{filter.location}", "key": "AIzaSyDto4pHmSEjqEzBZZZXBI7GjJnsBqedGPo"}
   parameters = urllib.parse.urlencode(parameters)
   req_url = url + parameters
   response = urllib.request.urlopen(req_url)
   response_string = response.read()
   json_results = json.loads(response_string)

   if json_results['status'] != 'OK':
      print(f"geocoding location '{filter.location}' failed with status: {json_results['status']}")
      return None
   
   geometry = json_results["results"][0]["geometry"]

   geocode_response = GeocodeResponse()
   geocode_response.lat = geometry["location"]["lat"]
   geocode_response.lng = geometry["location"]["lng"]
   geocode_response.accuracy = geometry["location_type"]
   for address_component in json_results["results"][0]["address_components"]:
      if address_component["types"][0] == "postal_code":
         geocode_response.postal_code = address_component["long_name"]

   return geocode_response

# ===========================================================================================================
def search_listings_page(filter, page_size, page_number):
   NESTORIA_API_URL = "https://api.nestoria.es/api"
   listings = []
   number_of_listings = 0
   
   parameters = {}
   parameters['action'] = 'search_listings'
   parameters['encoding'] = 'json'
   parameters['listing_type'] = 'buy'
   parameters['sort'] = 'newest'
   parameters['country'] = 'es'
   parameters['pretty'] = 1
   parameters['number_of_results'] = page_size
   parameters['page'] = page_number
   if filter.lat != None and filter.lng != None and filter.radius != None:
      parameters['radius'] = f"{filter.lat},{filter.lng},{filter.radius}km"
   else:
      parameters['place_name'] = filter.location

   if filter.price_max:
      parameters['price_max'] = filter.price_max
   if filter.price_min:
      parameters['price_min'] = filter.price_min
   if filter.size_max:
      parameters['size_max'] = filter.size_max
   if filter.size_min:
      parameters['size_min'] = filter.size_min

   # parameters['south_west'] = south_west
   # parameters['north_east'] = north_east
   # parameters['property_type'] = property_type
   # parameters['bedroom_max'] = bedroom_max
   # parameters['bedroom_min'] = bedroom_min
   # parameters['keywords'] = keywords
   # parameters['keywords_exclude'] = keywords_exclude

   req_url = NESTORIA_API_URL + "?" + urllib.parse.urlencode(parameters)
   response = None
   try:
      response = urllib.request.urlopen(req_url)

      # Check API has worked
      if response.getcode() != 200:
         if response.getcode() == 400:
            print("    - Bad request for " + area_name + ". Check that this area is searchable on Nestoria website")
         elif response.getcode() == 403:
            print("    - API call was forbidden. Reached maximum calls")
         else:
            print("    - Something else went wrong. HTTP response code is ", response.status_code)
         
         print(f"    - Url was: {req_url}")
         return listings, number_of_listings

      response_string = response.read()
      json_results = json.loads(response_string)

      if int(json_results['response']['application_response_code']) >= 200:
         print(f"")
         print(f"    - Error getting data")
         print(f"    - Application Response code: {json_results['response']['application_response_code']}")
         print(f"    - Response message: {json_results['response']['application_response_text']}")
         print(f"    - Url was: {req_url}")
         return listings, number_of_listings

      listings = json_results['response']['listings']
      #filter listings based on date
      listings = [listing for listing in listings if int(listing['updated_in_days']) <= filter.days_ago]

      number_of_listings = json_results['response']['total_results']

      return listings, number_of_listings
   except:
      print(f"\n- Exception trying to get data from:\n{req_url}")
   
   return listings, number_of_listings


def search_all_listings(filter):

   page_number = 1
   page_size = 50
   listings = []
   number_of_listings = 0

   print("-------------------------------------------------------------------------------------")
   print("")
   print(f"Searching for listings centered on '{filter.location}' with radius of {filter.radius}km, price in [{filter.price_min if filter.price_min else ' '},{filter.price_max if filter.price_max else ' '}] and size in [{filter.size_min if filter.size_min else ' '},{filter.size_max if filter.size_max else ' '}]")

   while True:
      if page_number==1:
         print(f"    Getting first {page_size} listings...", end="")
      else:
         print(f"    Getting listings {(page_number-1)*page_size+1}-{min((page_number)*page_size, number_of_listings)}...", end="")

      page_listings, number_of_listings = search_listings_page(filter, page_size, page_number)
      listings.extend(page_listings)

      number_of_pages = int (math.floor((number_of_listings-1)/page_size+1))
      expected_number_of_page_listings = page_size
      if (page_number == number_of_pages):
         expected_number_of_page_listings = number_of_listings - (number_of_pages-1)*page_size

      if number_of_listings > 0:
         print(f" Got {len(page_listings)}/{expected_number_of_page_listings} listings", end="")
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
      print(f"    Total {len(listings)} listing for {filter.location}")
   
   return listings


# ===========================================================================================================
def get_listings():
   input_file_name = "queries.csv"
   queries = get_queries(input_file_name)
   print(f"Loaded {len(queries)} queries")

   output_file, file_writer = get_file_writer()
   count = 0

   for query in queries:
      try:
         location = query["location"]
         size_min = None if query["size_min"] == "" else int(float(query["size_min"]))
         size_max = None if query["size_max"] == "" else int(float(query["size_max"]))
         price_min = None if query["price_min"] == "" else int(float(query["price_min"]))
         price_max = None if query["price_max"] == "" else int(float(query["price_max"]))
         radius = None if query["radius"] == "" else float(query["radius"])
         filter = Filter(location, size_min, size_max, price_min, price_max, radius=radius)

         geocode_response = geocode(filter)
         if geocode_response == None:  # geocoding failed
            continue

         filter.lat = geocode_response.lat
         filter.lng = geocode_response.lng
         listings = search_all_listings(filter)

         if len(listings) != 0:
            for listing in listings:
               listing["location"] = location
               listing["postal_code"] = geocode_response.postal_code
               listing["accuracy"] = geocode_response.accuracy

            file_writer.writerows(listings)
            output_file.flush()
            print("    Saved to file")
            count += len(listings)

         
      except Exception as e:
         print ("something threw an exception" + str(e))
         pass

   output_file.close()
   print(f"Total {count} listings for all locations")
   print("--- DONE! ---")

   return

# ===========================================================================================================
def main():
   get_listings()
   return ""

if __name__ == "__main__":
   print(main())
