from Property import Property

class PropertyFilter:
   def __init__(self, property, size_min=None, size_max=None, price_min=None, price_max=None, longitude=None, latitude=None, radius=None, days_ago=None):
      self.property = property
      self.size_min = size_min
      self.size_max = size_max
      self.price_min = price_min
      self.price_max = price_max
      self.radius = radius if radius != None else 250
      self.days_ago = days_ago if days_ago != None else 183

# no operator overlpading and hence need for some static methods to create objects
   @staticmethod
   def from_query(property, query):
      size_min = (None if query["size_min"] == "" else int(float(query["size_min"])))
      size_max = (None if query["size_max"] == "" else int(float(query["size_max"])))
      price_min = (None if query["price_min"] == "" else int(float(query["price_min"])))
      price_max = (None if query["price_max"] == "" else int(float(query["price_max"])))
      radius = (None if query["radius"] == "" else float(query["radius"]))

      filter = PropertyFilter(property, 
                     size_min=size_min, 
                     size_max=size_max, 
                     price_min=price_min, 
                     price_max=price_max, 
                     radius=radius)
      return filter
