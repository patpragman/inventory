import config


class Item:

    update_sql = """
    insert or replace into item (
        name,
        checked_in_by,
        customer,
        weight,
        volume,
        price,
        description,
        paid,
        origin,
        destination,
        id)
    values (?,?,?,?,?,?,?,?,?,?,?);
    """

    def __init__(self,
                 name: str = "item",
                 checked_in_by: str = "default",
                 customer: str = "",
                 weight: float = 0.0,
                 volume: float = 0.0,
                 price: int = 100,
                 paid: bool = False,
                 description: str = "default item",
                 origin: str = "origin",
                 destination: str = "destination",
                 row: list = None) -> None:
        if row is not None:
            # if you pass a SQL row to it, this is how we parse it
            # Iterate through all the rows, build a new item for each one
            self.name = row[0]
            self.checked_in_by = row[1]
            self.customer = row[2]
            self.weight = row[3]
            self.volume = row[4]
            self.price = row[5]
            self.paid = row[7]
            self.description = row[6]
            self.origin = row[8]
            self.destination = row[9]
            self.id = row[10]
            """
            8/4/2021 -pat

            after much gnashing of teeth this ended up the last entry of the SQL db so that
            it was easier to work with and I'd have to modify less code.  Sorry if this is confusing
            when I refactor things a bit later this will move up in both the DB and in the mapping code
            but for now this is fine."""

            # also, we need to generate the appropriate URLs
            self.cart_load_url = self.make_cart_load_url()
            self.cart_unload_url = self.make_cart_remove_url()
            self.qr_code_url = config.Config.local_url + self.make_qr_redirect_url()

        else:
            # if you didn't pass anything into it, we still need to create an object and it needs
            # to have some values so the whole codebase doesn't implode
            self.id = None  # start with blank id reference until the DB fills this out
            self.name = name
            self.checked_in_by = checked_in_by
            self.customer = customer
            self.weight = weight
            self.volume = volume
            self.price = price  # make sure this is an integer for rounding errors with reals
            self.paid = paid
            self.description = description
            self.origin = origin
            self.destination = destination
            self.cart_load_url = ""
            self.cart_unload_url = ""
            self.qr_code_url = ""

    def make_cart_load_url(self) -> str:
        # takes a cart item and produces a cart load url
        # recall that a status of

        return "cart/" "1" + "/" + str(self.id)

    def make_cart_remove_url(self) -> str:
        # takes a cart item and produces a cart load url
        # recall that a status of
        base_url = config.Config.local_url

        return base_url + "cart/" + "2" + "/" + str(self.id)

    def make_qr_redirect_url(self) -> str:
        # takes a cart item and produces a cart load url
        # recall that a status of
        return "cart/" + "3" + "/" + str(self.id)

    def generate_payload(self) -> tuple:
        data = (self.name,
                self.checked_in_by,
                self.customer,
                self.weight,
                self.volume,
                self.price,
                self.description,
                self.paid,
                self.origin,
                self.destination,
                self.id
                )
        return data
