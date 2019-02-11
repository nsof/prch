import csv
import datetime

class Listing:
    def __init__(self):
        self.location = None
        self.source = None
        self.postal_code = None
        self.geocode_accuracy = None
        self.catastro = None
        self.price = None
        self.size = None
        self.rooms = None
        self.floor = None
        self.hasLift = None
        self.bathrooms = None
        self.property_type = None
        self.updated_in_days = None
        self.url = None
        self.parking_spaces = None
        self.address = None
        self.neighborhood = None
        self.district = None
        self.province = None
        self.country = None
        self.latitude = None
        self.longitude = None
        self.source_id = None

    def __repr__(self):
        return str(self.__dict__)

    @staticmethod
    def get_file_writer():
        file_name = ("listings." + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv")
        output_file = open(file_name, "w", newline="", encoding="utf-8")
        field_names = [
            "location",
            "postal_code",
            "geocode_accuracy",
            "catastro",
            "source",
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
        file_writer = csv.DictWriter(output_file, field_names, restval="", 
            extrasaction="ignore",quoting=csv.QUOTE_MINIMAL,dialect="excel",
        )
        file_writer.writeheader()
        return output_file, file_writer
