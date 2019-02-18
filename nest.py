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
def load_queries(file_name):
    # fieled_names = ["location", "catastro", "size_min", "size_max", "price_min", "price_max", "radius"]
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
    radius = (None if query["radius"] == "" else float(query["radius"]))

    filter = Filter(location=location, 
                    catastro=catastro, 
                    size_min=size_min, 
                    size_max=size_max, 
                    price_min=price_min, 
                    price_max=price_max, 
                    radius=radius)
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
def get_listings_for_query(query):
    print("-------------------------------------------------------------------------------------")
    print(f"Searching listings for query {query}")
    print("-------------------------------------------------------------------------------------")

    try:
        filter = create_filter_from_query(query)
        if filter == None:
            print (f"skippping query {query}")
            return None

        if filter.location == None: # then there must be a catastro
            print("location was not specified. getting from catastro...", end="")
            filter.location = sw.get_address(filter.catastro)
            if filter.location == None:
                print("could not find location from catastro. skipping query")
                return None
            else:
                print(f"got location {filter.location}")
        
        print(f"geocoding location...", end="")
        geocode_response = Geocode.geocode(filter.location)
        if geocode_response == None:  # geocoding failed
            print("could not geocode location. Skipping query")
            return None
        else:
            print(f"got the following coordinates ({geocode_response.lat}','{geocode_response.lng})")

        filter.lat = geocode_response.lat
        filter.lng = geocode_response.lng

        listings = get_listings_from_data_sources(filter)
        if listings == None or len(listings) == 0:
            return None

        if filter.catastro == None:
            print(f"Searching for catastral reference... ",end="")
            filter.catastro = sw.get_catastral_reference(filter.lat, filter.lng)
            if filter.catastro != None:
                print(f"catastral reference for {(geocode_response.lat, geocode_response.lng)} is {filter.catastro}")
            else:
                print(f"could not find catastral reference for {(geocode_response.lat, geocode_response.lng)}")

        for listing in listings:
            listing.location = filter.location
            listing.postal_code = geocode_response.postal_code
            listing.geocode_accuracy = geocode_response.accuracy
            listing.catastro = filter.catastro
    
        return listings

    except Exception as e:
        print(f"Something threw an exception. Error message: {str(e)}")
    
    return None

# ===========================================================================================================
def get_listings(input_file_name):

    queries = load_queries(input_file_name)
    if not queries:
        print(f"No queries were loaded")
        return

    print(f"Loaded {len(queries)} queries")

    output_file, file_writer = Listing.get_file_writer()
    count = 0

    for query in queries:
        try:
            listings = get_listings_for_query(query)
            if not listings:
                continue

            for listing in listings:
                file_writer.writerow(vars(listing))

            output_file.flush()
            os.fsync(output_file.fileno())
            print(f"Saved {len(listings)} listings for current location to file")
            count += len(listings)

        except Exception as e:
            print(f"Something threw an exception. Error message: {str(e)}")

    if output_file != None:
        output_file.close()
        print(f"Total {count} listings for all locations")

    print("=== DONE! ===")
    return


# ===========================================================================================================
def main():
    get_listings("queries.csv")


def test_file_writer():
    listing = Listing()
    listing.location = "Avinguda Diagonal 20, Barcelona"
    listing.catastro = "9722108YJ2792D0002SA"
    listing.postal_code = "12345"
    listing.geocode_accuracy = "Rooftop"
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
    # filter = Filter(location="Ciutat vella, Valencia, Spain", price_max=100000, radius=50)
    filter = Filter(location = "la rambla, barcelona, Spain")
    filter.lat = "41.381472"
    filter.lng = "2.172750"
    filter.radius = 300
    filter.price_max = 200000
    results = get_listings_from_data_sources(filter)
    print (results)


def test_get_listings_for_query():
    query = {
        "location": "Carrer de berenguer mallol 40, Valencia",
        "catastro": "",
        "size_min": "",
        "size_max": "",
        "price_min": "",
        "price_max": "",
        "radius": "300"
    }
    results = get_listings_for_query(query)
    print (f"Got {len(results)} results")

    query = {
        "location": "",
        "catastro": "8931108DF2883B0001SO",
        "size_min": "",
        "size_max": "",
        "price_min": "",
        "price_max": "",
        "radius": "200"
    }
    results = get_listings_for_query(query)
    print (f"Got {len(results)} results")

def tests():
    test_get_listings_for_query()
    # test_get_listings_from_data_sources()
    # test_file_writer()


if __name__ == "__main__":
    # tests()
    main()
