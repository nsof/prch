import json
import csv
import datetime
import re
import math
import requests
import urllib
import os
import pickle

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
   field_names = ["location", "postal_code", "accuracy", "catastro", "price", "size", "updated_in_days", "lister_url", "lister_name"
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
   # url = 'https://maps.googleapis.com/maps/api/geocode/json?'
   # parameters = {"address": f"{filter.location}", "key": "AIzaSyDto4pHmSEjqEzBZZZXBI7GjJnsBqedGPo"}
   # parameters = urllib.parse.urlencode(parameters)
   # req_url = url + parameters
   # response = urllib.request.urlopen(req_url)
   # response_string = response.read()
   url = 'https://maps.googleapis.com/maps/api/geocode/json'
   parameters = {"address": f"{filter.location}", "key": "AIzaSyDto4pHmSEjqEzBZZZXBI7GjJnsBqedGPo"}
   response = requests.get(url, params = parameters)
   json_results = response.json()

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

   
def find_value(key, text):
   n = text.find(key)
   start = text.find('value="', n) + len('value="')
   end = text.find('"', start)
   value = text[start:end]
   return value

class GZ:
   __session = None
   __tried = False
   __cookies_file_name = "cookies.txt"

   @staticmethod
   def save_cookies():
      with open(GZ.__cookies_file_name, 'wb') as f:
         pickle.dump(GZ.__session.cookies, f)


   @staticmethod
   def load_cookies():
      if not os.path.isfile(GZ.__cookies_file_name):
        return

      with open(GZ.__cookies_file_name, 'rb') as f:
         GZ.__session.cookies.update(pickle.load(f))


   @staticmethod
   def get_session():
      if GZ.__session != None:
         return GZ.__session

      GZ.__session = requests.Session()
      GZ.__session.cookies.clear()
      GZ.load_cookies()
      GZ.__session.headers.clear()
      GZ.__session.headers.update({
         "Host": "es.goolzoom.com",
         "Connection": "keep-alive",
         "Upgrade-Insecure-Requests": "1",
         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
         "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
         "Accept-Encoding": "gzip, deflate, br",
         "Referer": "https://es.goolzoom.com/mapas/",
         "Accept-Language" : "en-GB,en;q=0.9,en-US;q=0.8,he;q=0.7"
      })

      return GZ.__session


   @staticmethod
   def try_to_login(prev_response = None):
      if GZ.__tried == True:
         return False

      GZ.__tried = True

      print ("Trying to sign into Goolzoom...")
      try:
         if prev_response == None:
            url = "https://es.goolzoom.com/mapas/"
            prev_response = GZ.get_session().get(url)

         vs_value = find_value('id="__VIEWSTATE"', prev_response.text)
         vsg_value = find_value('id="__VIEWSTATEGENERATOR"', prev_response.text)
         parameters = { }
         headers = { 
            "Origin": "https://es.goolzoom.com",
            "Referer": prev_response.url,
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "max-age=0"
         }
         data = {
            "__VIEWSTATE" : vs_value,
            "__VIEWSTATEGENERATOR" : vsg_value,
            "email" : "yoed.dotan@gmail.com",
            "password" : "shafan10"
         }
         response = GZ.get_session().post(prev_response.url, params = parameters, headers = headers, data=data)
         if "SignIn.aspx" in response.url:
            print ("Failed to sign in")
            return False

         GZ.save_cookies()
         return True

      except Exception as e:
         print ("Failed to sign in to Goolzoom")
         print ("Error message: ", e)

      return False


   @staticmethod
   def get_cadastral_data(lat, lng):
      cadastral_reference = None
      try:
         url = "https://es.goolzoom.com/el-propietario/GetGeo.aspx"
         headers = { "Referer": "https://es.goolzoom.com/el-propietario/",}
         parameters = { "lat" : lat,"lng" : lng,}

         response = GZ.get_session().get(url, params = parameters, headers=headers)

         if "SignIn.aspx" in response.url:
            if GZ.try_to_login(response):
               response = GZ.get_session().get(url, params = parameters, headers=headers)
            else:
               return None

         if response.text == '':
            print ("Failed to get catasral reference number. Probably failed to login")
            return cadastral_reference

         try:
            json_results = response.json()
            if len (json_results["features"]) > 0:
               cadastral_reference = json_results["features"][0]["properties"]["l"]
            else:
               print ("Failed to get catasral reference number. Perhaps location is not accurate")
               print (f"Url was {response.request.url}")
         except ValueError as e:
            print (f"Failed to get catasral reference number. Server's response was {'empty' if response.text=='' else response.text}")
            cadastral_reference = None

      except Exception as e:
         print ("Failed to get catasral reference number")
         print ("Error message: ", e)
         cadastral_reference = None

      return cadastral_reference


# class Sedecatastro:

#    @staticmethod
#    def find_cadastral_reference_in_text(text):
#       n = text.find("PARCELA CATASTRAL")
#       if n == -1:
#          return None

#       start = text.find('value="', n) + len('value="')
#       end = text.find('"', start)
#       value = text[start:end]
#       return value

#    @staticmethod
#    def cadastral_reference(lat, lng):
#       try:
#          url = "https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCListaBienes.aspx"
#          headers = { 
#             # "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
#             # "Accept-Encoding" : "gzip, deflate, br"
#             # Accept-Language: en-GB,en;q=0.9,en-US;q=0.8,he;q=0.7
#             # Connection: keep-alive
#             # Cookie: ASP.NET_SessionId=kirnbuffprhok1yfobovdpk5; Lenguaje=es
#             # Host: www1.sedecatastro.gob.es
#             # Upgrade-Insecure-Requests: 1
#             "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
#          }
#          parameters = { 
#                "latitud" : lat, "longitud" : lng, 
#                "pest" : "coordenadas", "huso" : "0", "tipoCoordenadas" : "2", "TipUR" : "Coor",
#          }
#          response = requests.get(url, params = parameters, headers=headers)

#          if response.status_code != 200:
#             print (f"Failed to get catasral reference number from {response.request.url}")
#             return None

#          if "SignIn.aspx" in response.url:
         

#       except Exception as e:
#          print ("Failed to get catasral reference number")
#          print ("Error message: ", e)
#          cadastral_reference = None

#       return cadastral_reference



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
            cadastral_reference = GZ.get_cadastral_data(geocode_response.lat, geocode_response.lng)

            for listing in listings:
               listing["location"] = location
               listing["postal_code"] = geocode_response.postal_code
               listing["accuracy"] = geocode_response.accuracy
               listing["catastro"] = cadastral_reference

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
   cadastral_reference = GZ.get_cadastral_data(41.39409684378864, 2.1487222098593293)
   print ("cadastral_reference =", cadastral_reference)

   cadastral_reference = GZ.get_cadastral_data(41.39409684378864, 2.1487222098593293)
   print ("cadastral_reference =", cadastral_reference)
   # get_listings()
   return ""

if __name__ == "__main__":
   print(main())
