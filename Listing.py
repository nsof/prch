
class Listing:

    def __init__(self, filter):
        self.filter = filter
        self.source = None # data source: nestoria / idealista
        self.type = None
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
        self.source_id = None # id in source

    def __repr__(self):
        return str(self.__dict__)
