class Place:

    def __init__(self,
                 name: str = "Anytown USA",
                 description: str = "middle of nowhere",
                 airport_code: str = "PANC",
                 price: int = 0,
                 row: list = None) -> None:

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
