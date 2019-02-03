import json
import csv
import datetime
import re
import requests
import os
import pickle
import SedecatastroWrapper as sw
import NestoriaWrapper as nw
import Geocode
from Filter import Filter

############################################################################################################
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
def get_listings():
   input_file_name = "queries.csv"
   queries = get_queries(input_file_name)
   print(f"Loaded {len(queries)} queries")

   output_file = None
   if queries != None and len(queries) > 0:
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

         geocode_response = Geocode.geocode(filter)
         if geocode_response == None:  # geocoding failed
            print (f"    could not geocode location. Continuing to next location")
            continue

         filter.lat = geocode_response.lat
         filter.lng = geocode_response.lng
         listings = nw.search_all_listings(filter)

         if len(listings) != 0:
            cadastral_reference = sw.get_cadastral_reference(geocode_response.lat, geocode_response.lng)
            if cadastral_reference != None:
               print (f"    cadastral reference for {(geocode_response.lat, geocode_response.lng)} is {cadastral_reference}")
            else:
               print (f"    could not find cadastral reference for {(geocode_response.lat, geocode_response.lng)}")

            for listing in listings:
               listing["location"] = location
               listing["postal_code"] = geocode_response.postal_code
               listing["accuracy"] = geocode_response.accuracy
               listing["catastro"] = cadastral_reference

            file_writer.writerows(listings)
            output_file.flush()
            os.fsync(output_file.fileno())
            print("    Saved to file")
            count += len(listings)
         
      except Exception as e:
         print (f"    something threw an exception {str(e)}. Continuing to next query")

   if output_file != None:
      output_file.close()
      print(f"Total {count} listings for all locations")
   
   print("--- DONE! ---")

   return

# ===========================================================================================================
def main():
   # sw.Sedecatastro_test()
   get_listings()
   return ""

if __name__ == "__main__":
   print(main())
