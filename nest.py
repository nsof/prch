import json
import csv
import re
import requests
import os
import pickle
import SedecatastroWrapper as sw
import NestoriaWrapper as nw
from IdealistaWrapper import IdealistaWrapper as iw
import Geocode
from Filter import Filter
from Listing import Listing

############################################################################################################
# ===========================================================================================================
def get_queries(file_name):
    # filed_names = ["location", "size_min", "size_max", "price_min", "price_max", "radius"]
    queries = []
    with open(file_name, "r", newline="", encoding="utf-8") as input_file:
        file_reader = csv.DictReader(input_file)
        queries = [query for query in file_reader]

    return queries


# ===========================================================================================================
def create_filter_from_query(query):
    location = (None if query["location"] == "" else query["location"])
    catastro = (None if query["catastro"] == "" else query["catastro"])
    if location == None and catastro == None:
        return None

    size_min = (None if query["size_min"] == "" else int(float(query["size_min"])))
    size_max = (None if query["size_max"] == "" else int(float(query["size_max"])))
    price_min = (None if query["price_min"] == "" else int(float(query["price_min"])))
    price_max = (None if query["price_max"] == "" else int(float(query["price_max"])))
    radius = None if query["radius"] == "" else float(query["radius"])
    filter = Filter(location, catastro, size_min, size_max, price_min, price_max, radius=radius)
    return filter


# ===========================================================================================================
def get_listings_from_data_sources(filter):
    nestoria_listings = nw.search_all_listings(filter)
    idealista_listings = iw.search_listings(filter)
    listings = []
    listings.extend(nestoria_listings)
    listings.extend(idealista_listings)

    return listings


# ===========================================================================================================
def get_listings():
    print("=========================================================================================")
    input_file_name = "queries.csv"
    queries = get_queries(input_file_name)

    if queries == None or len(queries) == 0:
        print(f"No queries were loaded")
        return []

    print(f"Loaded {len(queries)} queries")

    output_file, file_writer = Listing.get_file_writer()
    count = 0

    for query in queries:
        try:
            filter = create_filter_from_query(query)
            if filter == None:
                print (f"skippping query {query}")
                continue

            print("-------------------------------------------------------------------------------------")
            print(f"Searching for listings centered on '{filter.location}' with radius of {filter.radius}m, price in [{filter.price_min if filter.price_min else ' '},{filter.price_max if filter.price_max else ' '}] and size in [{filter.size_min if filter.size_min else ' '},{filter.size_max if filter.size_max else ' '}]")
            print("-------------------------------------------------------------------------------------")

            geocode_response = Geocode.geocode(filter)
            if geocode_response == None:  # geocoding failed
                print(f"could not geocode location. Continuing to next location")
                continue

            filter.lat = geocode_response.lat
            filter.lng = geocode_response.lng

            listings = get_listings_from_data_sources(filter)
            if listings == None or len(listings) == 0:
                continue

            catastral_reference = filter.catastro
            if catastral_reference == None:
                print(f"--- Searching for catastral reference ---")
                catastral_reference = sw.get_catastral_reference(filter.lat, filter.lng)
                if catastral_reference != None:
                    print(f"    catastral reference for {(geocode_response.lat, geocode_response.lng)} is {catastral_reference}")
                else:
                    print(f"    could not find catastral reference for {(geocode_response.lat, geocode_response.lng)}")

            for listing in listings:
                listing.location = filter.location
                listing.postal_code = geocode_response.postal_code
                listing.geocode_accuracy = geocode_response.accuracy
                listing.catastro = catastral_reference

            for listing in listings:
                file_writer.writerow(vars(listing))
            output_file.flush()
            os.fsync(output_file.fileno())
            print(f"--- Saved {len(listings)} listings for current location to file")
            count += len(listings)

        except Exception as e:
            print(f"    something threw an exception {str(e)}. Continuing to next query")

    if output_file != None:
        output_file.close()
        print(f"Total {count} listings for all locations")

    print("=== DONE! ===")

    return


# ===========================================================================================================
def main():
    get_listings()


def test_file_writer():
    listing = Listing()
    listing.location = "Avinguda Diagonal 20, Barcelona"
    listing.postal_code = "12345"
    listing.geocode_accuracy = "Rooftop"
    listing.catastro = "9722108YJ2792D0002SA"
    listing.source = "Test"
    listing.price = 654321
    listing.size = 105
    listing.rooms = 3
    listing.floor = 2
    listing.bathrooms = 2
    listing.property_type = "flat"
    listing.updated_in_days = 10
    listing.parking_spaces = 0
    listing.url = "https://www.example.com/"
    listing.address = "Carrer de les Corts, 25"
    listing.neighborhood = "El Gotico"
    listing.district = "barcelona"
    listing.province = None
    listing.country = "es"
    listing.latitude = 41.383864
    listing.longitude = 2.183984
    listing.source_id = "ididididid"

    output_file, file_writer = Listing.get_file_writer()
    file_writer.writerow(vars(listing))
    output_file.flush()
    os.fsync(output_file.fileno())
    output_file.close()


def test_get_listings_from_data_sources():
    filter = Filter("Carrer d'en Carabassa, 2, Barcelona, Spain")
    filter.radius = 50
    get_listings_from_data_sources(filter)


if __name__ == "__main__":
    # test_get_listings_from_data_sources()
    # test_file_writer()
    main()

