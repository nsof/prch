import math
import urllib
import json

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