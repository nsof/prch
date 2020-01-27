from Property import Property


class PropertyFilter:
    def __init__(
        self,
        property,
        type=None,
        size_min=None,
        size_max=None,
        price_min=None,
        price_max=None,
        radius=None,
        days_ago=None,
    ):
        self.property = property
        self.type = type
        self.size_min = size_min
        self.size_max = size_max
        self.price_min = price_min
        self.price_max = price_max
        self.radius = radius if radius != None else 250
        self.days_ago = days_ago if days_ago != None else 183

    def __repr__(self):
        return f"property: {self.property}, type: {self.type}, size_min: {self.size_min}, size_max: {self.size_max}, price_min: {self.price_min}, price_max: {self.price_max}, radius: {self.radius}, days_ago: {self.days_ago}"

    # no operator overlpading and hence need for some static methods to create objects
    @staticmethod
    def from_query(property, query):

        type = "buy"
        if "type" in query and query["type"] != "":
            type = query["type"]

        size_min = None if query["size_min"] == "" else int(float(query["size_min"]))
        size_max = None if query["size_max"] == "" else int(float(query["size_max"]))
        price_min = None if query["price_min"] == "" else int(float(query["price_min"]))
        price_max = None if query["price_max"] == "" else int(float(query["price_max"]))
        radius = None if query["radius"] == "" else float(query["radius"])

        filter = PropertyFilter(
            property,
            type=type,
            size_min=size_min,
            size_max=size_max,
            price_min=price_min,
            price_max=price_max,
            radius=radius,
        )
        return filter

