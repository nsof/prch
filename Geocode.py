import requests

class GeocodeResponse:
   def __init__(self):
      self.lat = None
      self.lng = None
      self.accuracy = None
      self.postal_code = "Not found"


def geocode(filter):
   url = 'https://maps.googleapis.com/maps/api/geocode/json'
   parameters = {"address": f"{filter.location}", "key": "AIzaSyDto4pHmSEjqEzBZZZXBI7GjJnsBqedGPo"}
   geocode_response = None

   try:
      response = requests.get(url, params = parameters)
      json_results = response.json()

      if json_results['status'] != 'OK':
         print(f"geocoding location '{filter.location}' failed with status: {json_results['status']}")
         return None
      
      geometry = json_results["results"][0]["geometry"]

      geocode_response = GeocodeResponse()
      geocode_response.lat = geometry["location"]["lat"]
      geocode_response.lng = geometry["location"]["lng"]
      geocode_response.accuracy = geometry["location_type"]
      for address_component in json_results["results"][0]["address_components"]:
         if address_component["types"][0] == "postal_code":
            geocode_response.postal_code = address_component["long_name"]
   
   except Exception:
      return None
   
   return geocode_response
