class Place:

    def __init__(self,
                 name: str = "Anytown USA",
                 description: str = "middle of nowhere",
                 airport_code: str = "PANC",
                 price: int = 0,
                 row: list = None) -> None:

        """Well, I kind of fucked up when designing this, I didn't include an ID like in the item database
        so, anyway, I needed to make a local id to prevent collisions.  Instead of using the name of the location
        this makes sense, right, because "Anchorage" has several airports in it, Anchorage, Lakehood, Merril, etc.
        so this makes a local id that gets assigned to each place.  This gets used as the key in the database"""
        self.local_id = 0  # make sure to assign this, or no bueno, you'll have db collisions

        if row is not None:
            self.name = row[0]
            self.description = row[1]
            self.airport_code = row[2]
            self.price = row[3]
        else:
            self.name = name
            self.description = description
            self.airport_code = airport_code
            self.price = price  # again make sure this is an integer to eliminate rounding errors
