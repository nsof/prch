import json
import csv
import re
import requests
import pickle
import SedecatastroWrapper as sw
from NestoriaWrapper import NestoriaWrapper as nw
from IdealistaWrapper import IdealistaWrapper as iw
from PropertyFilter import PropertyFilter
from Property import Property
from Listing import Listing
from ListingWriter import ListingWriter

############################################################################################################
# ===========================================================================================================
def load_queries(file_name):
    expected_field_names = ["location", "catastro", "size_min", "size_max", "price_min", "price_max", "radius"]
    queries = []
    with open(file_name, "r", newline="", encoding="utf-8") as input_file:
        file_reader = csv.DictReader(input_file)
        file_reader_field_names = [fr_fieldname.lower() for fr_fieldname in file_reader.fieldnames]

        for expected_field_name in expected_field_names:
            if expected_field_name not in file_reader_field_names:
                print(f"Expected '{expected_field_name}' to be a header in the queries file but it is not")
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
        
        # update location or catastro and geo location
        success = property.update_property_from_data_sources()
        if success == False:
            print (f"Failed to update property from data sources. Skipping query")
            return None

        filter = PropertyFilter.from_query(property, query)
        listings = get_listings_from_data_sources(filter)
        if listings == None or len(listings) == 0:
            return None
    
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

    count = 0

    for query in queries:
        try:
            listings = get_listings_for_query(query)
            if not listings:
                continue
            ListingWriter.write_listings(listings)
            count += len(listings)

        except Exception as e:
            print(f"Something threw an exception. Error message: {str(e)}")
    
    ListingWriter.close_writer()

    print(f"Got a total of {count} listings for all locations")

    print("=== DONE! ===")
    return


# ===========================================================================================================
def main():
    get_listings("queries.csv")


def test_get_listings_from_data_sources():
    # filter = PropertyFilter(location="Ciutat vella, Valencia, Spain", price_max=100000, radius=50)
    property = Property(location = "la rambla, barcelona, Spain")
    filter = PropertyFilter(property = property)
    filter.radius = 300
    filter.price_max = 200000
    listings = get_listings_from_data_sources(filter)
    ListingWriter.write_listings(listings)
    print (listings)


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
    listings = get_listings_for_query(query)
    print (f"Got {len(listings)} results")
    ListingWriter.write_listings(listings)

    query = {
        "location": "",
        "catastro": "8931108DF2883B0001SO",
        "size_min": "",
        "size_max": "",
        "price_min": "",
        "price_max": "",
        "radius": "200"
    }
    listings = get_listings_for_query(query)
    print (f"Got {len(listings)} results")
    ListingWriter.write_listings(listings)

def tests():
    #test_get_listings_from_data_sources()
    test_get_listings_for_query()


if __name__ == "__main__":
    #tests()
    main()
