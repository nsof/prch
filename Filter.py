
class Filter:
   def __init__(self, location=None, catastro=None, size_min=None, size_max=None, price_min=None, price_max=None, lng=None, lat=None, radius=None, days_ago=None):
      self.location = location
      self.catastro = catastro
      self.size_min = size_min
      self.size_max = size_max
      self.price_min = price_min
      self.price_max = price_max
      self.lat = lat
      self.lng = lng
      self.radius = radius if radius != None else 250
      self.days_ago = days_ago if days_ago != None else 183
