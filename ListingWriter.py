import csv
import datetime
import os
from Listing import Listing
from Property import Property
from PropertyFilter import PropertyFilter

class ListingWriter:

    output_file = None
    file_writer = None
    output_field_names = [
        # property output field names
        "property_location",
        "property_catastro",
        "property_postal_code",
        "property_latitude",
        "property_longitude",
        "property_geocode_accuracy",
        "property_construction_year",
        "property_stairs",
        "property_floor",
        "property_door",
        "property_private_area",
        "property_common_area",
        # listing output field names
        "source",
        "type",
        "price",
        "size",
        "rooms",
        "floor",
        "hasLift",
        "bathrooms",
        "property_type",
        "updated_in_days",
        "parking_spaces",
        "url",
        "address",
        "neighborhood",
        "district",
        "province",
        "country",
        "latitude",
        "longitude",
        "source_id",
    ]

    @staticmethod
    def create_file_writer():
        file_name = ("listings." + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv")
        ListingWriter.output_file = open(file_name, "w", newline="", encoding="utf-8")
        ListingWriter.file_writer = csv.DictWriter(ListingWriter.output_file, ListingWriter.output_field_names, restval="", 
            extrasaction="ignore",quoting=csv.QUOTE_MINIMAL,dialect="excel",
        )
        ListingWriter.file_writer.writeheader()

    @staticmethod
    def close_writer():
        if ListingWriter.output_file != None:
            ListingWriter.output_file.close()


    @staticmethod
    def flatten_listing(listing):
        flat_listing = (vars(listing)).copy() #shallow copy is ok
        flat_listing.pop("filter")
        flat_listing["property_location"] = listing.filter.property.location
        flat_listing["property_catastro"] = listing.filter.property.catastro
        flat_listing["property_postal_code"] = listing.filter.property.postal_code
        flat_listing["property_geocode_accuracy"] = listing.filter.property.geocode_accuracy
        flat_listing["property_latitude"] = listing.filter.property.latitude
        flat_listing["property_longitude"] = listing.filter.property.longitude
        flat_listing["property_construction_year"] = listing.filter.property.construction_year
        flat_listing["property_stairs"] = listing.filter.property.stairs
        flat_listing["property_floor"] = listing.filter.property.floor
        flat_listing["property_door"] = listing.filter.property.door
        flat_listing["property_private_area"] = listing.filter.property.private_area
        flat_listing["property_common_area"] = listing.filter.property.common_area
        flat_listing["type"] = listing.filter.type
        return flat_listing

    @staticmethod
    def write_listings(listings):
        if ListingWriter.output_file == None:
            ListingWriter.create_file_writer()

        for listing in listings:
            row = ListingWriter.flatten_listing(listing)
            ListingWriter.file_writer.writerow(row)

        ListingWriter.output_file.flush()
        os.fsync(ListingWriter.output_file.fileno())



def test_file_writer():
    property = Property(location="Avinguda Diagonal 20, Barcelona", catastro="9722108YJ2792D0002SA")
    property.postal_code = "12345"
    property.geocode_accuracy = "Rooftop"
    property.latitude = 314
    property.longitude = 314

    filter = PropertyFilter(property, size_min=10, size_max=1000, price_min=100000, price_max=1000000000, radius=250)

    listing = Listing(filter)
    listing.source = "Test"
    listing.type = "rent"
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

    listings = [listing]
    ListingWriter.write_listings(listings)


if __name__ == "__main__":
    test_file_writer()

