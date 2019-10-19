import Geo
import SedecatastroWrapper as sw

class Property:
    @staticmethod
    def from_query(query):
        location = (None if query["location"] == "" else query["location"])
        catastro = (None if query["catastro"] == "" else query["catastro"])
        if location == None and catastro == None:
            #one or the other has to be specified
            return None

        property = Property(location=location, catastro=catastro)
        return property

    def __init__(self, location=None, catastro=None):
        self.location = location
        self.catastro = catastro
        self.postal_code = None
        self.geocode_accuracy = None
        self.longitude = None
        self.latitude = None

    def __repr__(self):
        return str(self.__dict__)


    def update_property_from_data_sources(self):
        if self.location == None: # then there must be a catastro
            print("location was not specified. getting from catastro...", end="")
            self.location = sw.get_address(self.catastro)
            if self.location == None:
                print("could not find location from catastro. skipping query")
                return None
            else:
                print(f"got location {self.location}")
        
        print(f"geocoding location...", end="")
        geocode_response = Geo.geocode(self.location)
        if geocode_response == None:  # geocoding failed
            print("could not geocode location. Skipping query")
            return None
        else:
            print(f"got the following coordinates ({geocode_response.lat}','{geocode_response.lng})")

        self.latitude = geocode_response.lat
        self.longitude = geocode_response.lng
        self.postal_code = geocode_response.postal_code
        self.geocode_accuracy = geocode_response.accuracy

        if self.catastro == None:
            print(f"Searching for catastral reference... ",end="")
            self.catastro = sw.get_catastral_reference(self.latitude, self.latitude)
            if self.catastro != None:
                print(f"catastral reference for {(self.latitude, self.latitude)} is {self.catastro}")
            else:
                print(f"could not find catastral reference for {(self.latitude, self.latitude)}")
        
        return self
