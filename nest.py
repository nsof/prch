import json
import csv
import re
import requests
import os
import pickle
import SedecatastroWrapper as sw
from NestoriaWrapper import NestoriaWrapper as nw
from IdealistaWrapper import IdealistaWrapper as iw
from Filter import PropertyFilter
from Property import Property
from Listing import Listing

############################################################################################################
# ===========================================================================================================
def load_queries(file_name):
    expected_field_names = ["location", "catastro", "size_min", "size_max", "price_min", "price_max", "radius"]
    queries = []
    with open(file_name, "r", newline="", encoding="utf-8") as input_file:
        file_reader = csv.DictReader(input_file)

        for expected_field_name in expected_field_names:
            if expected_field_name not in file_reader.fieldnames:
                print("Expected '{expected_field_name}' to be a header in the queries file but it is not")
                return None

        queries = [query for query in file_reader]

    return queries


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
        property = Property.from_query(query)
        if property == None:
            print (f"skippping query {query} because the input data (in file) has a problem")
            return None
        
        property.update_property_from_data_sources()

        filter = PropertyFilter.from_query(property, query)
        listings = get_listings_from_data_sources(filter)
        if listings == None or len(listings) == 0:
            return None

        for listing in listings:
            listing.location = property.location
            listing.postal_code = property.postal_code
            listing.geocode_accuracy = property.geocode_accuracy
            listing.catastro = property.catastro
    
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
    property = Property(location = "Avinguda Diagonal 20, Barcelona")
    filter = PropertyFilter(property)
    listing = Listing(filter)
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
    listing.source_id = "testtest"

    output_file, file_writer = Listing.get_file_writer()
    file_writer.writerow(vars(listing))
    output_file.flush()
    os.fsync(output_file.fileno())
    output_file.close()


def test_get_listings_from_data_sources():
    # filter = Filter(location="Ciutat vella, Valencia, Spain", price_max=100000, radius=50)
    property = Property(location = "la rambla, barcelona, Spain")
    property.latitude = "41.381472"
    property.latitude = "2.172750"
    filter = PropertyFilter(property = property)
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
