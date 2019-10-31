import Geo
import SedecatastroWrapper as sw

class Property:
    def __init__(self, location=None, catastro=None):
        self.location = location
        self.catastro = catastro

         # from google geocoding service
        self.postal_code = None
        self.geocode_accuracy = None
        self.longitude = None
        self.latitude = None
         
         # from sedecatastro.gob.es
        self.construction_year = None
        self.stairs = None
        self.floor = None
        self.door = None
        self.private_area = None
        self.common_area = None

    def __repr__(self):
        return f"location: {self.location}, catastro: {self.catastro}, postal code: {self.postal_code}, lng: {self.longitude}, lat: {self.latitude}, " \
            f"constuction year: {self.construction_year}, stairs: {self.stairs}, floor: {self.floor}, door: {self.door}, " \
            f"private area: {self.private_area}, common area: {self.common_area}"

    def _merge_from_cadastro_property(self, cadastro_property):
        if self.location == None and cadastro_property.location != None:
            self.location = cadastro_property.location
        self.construction_year = cadastro_property.construction_year
        self.stairs = cadastro_property.stairs
        self.floor = cadastro_property.floor
        self.door = cadastro_property.door
        self.private_area = cadastro_property.private_area
        self.common_area = cadastro_property.common_area

    @staticmethod
    def from_query(query):
        location = (None if query["location"] == "" else query["location"])
        catastro = (None if query["catastro"] == "" else query["catastro"])
        if location == None and catastro == None:
            #one or the other has to be specified
            return None

        property = Property(location=location, catastro=catastro)
        return property


    def _geocode_location(self):
        if self.location == None: 
            print (f"cannot geocode location since there is no location for property", end="")
            return False

        print(f"geocoding location using Google's geocoding service...", end="")
        geocode_response = Geo.geocode(self.location)
        if geocode_response == None:  # geocoding failed
            print("could not geocode location")
            return False
        else:
            print(f"got the following coordinates ({geocode_response.lat},{geocode_response.lng})")

        self.latitude = geocode_response.lat
        self.longitude = geocode_response.lng
        self.postal_code = geocode_response.postal_code
        self.geocode_accuracy = geocode_response.accuracy
        return True


    def update_property_from_data_sources(self):
        updated_from_catastro = False

        if self.location == None: # then there must be a catastro
            print("location was not specified. getting from catastro...", end="")
            cadastro_property = sw.get_property_from_catastro(self.catastro)
            updated_from_catastro = True
            self._merge_from_cadastro_property(cadastro_property)
            if self.location == None:
                print("could not find location from catastro. skipping query")
                return False
            else:
                print(f"got location {self.location}")
        
        if self._geocode_location() == False:
            return False

        if self.catastro == None and self.latitude != None and self.longitude != None:
            print(f"Searching for catastral reference... ",end="")
            self.catastro = sw.get_catastral_reference(self.latitude, self.longitude)
            if self.catastro != None:
                print(f"catastral reference for {(self.latitude, self.longitude)} is {self.catastro}")
            else:
                print(f"could not find catastral reference for {(self.latitude, self.longitude)}")

        if self.catastro != None and updated_from_catastro == False:
            cadastro_property = sw.get_property_from_catastro(self.catastro)
            self._merge_from_cadastro_property(cadastro_property)
        
        return True



def test_update_property_from_data_sources():

    print(f"Testing update_property_from_data_sources")

    catastral_reference = "0038130YJ2794B0017UH"
    location = "CL ANTONIO PONZ 120, VALENCIA, VALENCIA"
    property = Property(catastro = catastral_reference)

    success = property.update_property_from_data_sources()
    if not success:
        print(f"update_property_from_data_sources failed")
        return

    if property.location != location:
        print(f"failed to get location reference")
        return

    if property.construction_year != "1966":
        print(f"failed to get construction year correctly")
        return

    if property.private_area != "65":
        print(f"failed to get private correctly")
        return

    property = Property(location = location)
    success = property.update_property_from_data_sources()
    if not success:
        print(f"update_property_from_data_sources failed")
        return

    if property.catastro != catastral_reference:
        print(f"failed to get catastral reference")
        return



def tests():
    test_update_property_from_data_sources()


if __name__ == "__main__":
    tests()
