import sqlite3
import config
from sql import query_database, clear_rows_of
from person import Person




class Item:

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
                 destination: str = "destination") -> None:
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


class Place:

    def __init__(self,
                 name: str = "Anytown USA",
                 description: str = "middle of nowhere",
                 airport_code: str = "PANC",
                 price: int = 0) -> None:
        self.name = name
        self.description = description
        self.airport_code = airport_code
        self.price = price  # again make sure this is an integer to eliminate rounding errors


class Cart:

    def __init__(self):
        """the cart class is a little data let's you stage items for checkout, nothing crazy
        here but I don't think we should store each potential stack of items you wish
        to check out in the database persistently.  Having this be persistent between sessions is not
        to crazy.  We can revisit this later if it becomes an issue - but typically in my
        experience typically carts are formed on adhoc basis and are quick to be filled.  Rarely
        are they kept for multiple days.  This may require change but shouldn't be too crazy because
        the stuff going into the "cart" are members of the item
        class"""

        self.description = "Generic Cart"  # this should be editable by the user
        self.items = [Item]  # this should be a list of items


class Database:
    location = "inventory.db"

    def __init__(self):
        # these dictionaries will hold data we need
        self.people = {}
        self.items = {}
        self.places = {}

        # here are the SQL queries we'll use to access the db and query it
        person_query = 'select * from person'
        item_query = 'select * from item'
        place_query = 'select * from place'

        # try to connect, then build persons, items, and places objects
        try:
            # let's connect to the database and get the person objects out of it
            person_query_rows = query_database(person_query, Database.location)
            for row in person_query_rows:
                # Iterate through all the rows creating a new person with every row
                # the mapping from the database to the
                person = Person(row=row)
                self.people[person.username] = person

            # now let's get all the items
            item_query_rows = query_database(item_query, Database.location)
            for row in item_query_rows:
                # Iterate through all the rows, build a new item for each one
                item = Item()
                item.name = row[0]
                item.checked_in_by = row[1]
                item.customer = row[2]
                item.weight = row[3]
                item.volume = row[4]
                item.price = row[5]
                item.paid = row[7]
                item.description = row[6]
                item.origin = row[8]
                item.destination = row[9]
                item.id = row[10] 
                """after much gnashing of teeth this ended up the last entry of the SQL db so that
                it was easier to work with and I'd have to modify less code.  Sorry if this is confusing
                when I refactor things a bit later this will move up in both the DB and in the mapping code
                but for now this is fine."""

                # also, we need to generate the appropriate URLs
                item.cart_load_url = item.make_cart_load_url()
                item.cart_unload_url = item.make_cart_remove_url()
                item.qr_code_url = config.Config.local_url + item.make_qr_redirect_url()

                self.items[item.id] = item

            # finally the places
            place_query_rows = query_database(place_query, Database.location)
            for row in place_query_rows:
                # Iterate through all the rodes, make a new node with the lat_lons
                place = Place()
                place.name = row[0]
                place.description = row[1]
                place.airport_code = row[2]
                place.price = row[3]

                self.places[place.name] = place

        except Exception as err:
            if isinstance(err, sqlite3.Error):
                # we can eventually put logs here
                print("There was a database error.")
                print(err)
            else:
                print("An unknown error occurred.")
                print(err)

    def save_people(self) -> bool:
        # first we'll delete all the people out of the db so we don't end up with copies
        clear_rows_of("person", Database.location)
        # next let's put all the people into the database
        # first let's write the SQL to update the db
        sql_query = """
        insert or replace into person (
            first_name,
            last_name,
            address,
            phone,
            email,
            notes,
            username,
            password,
            is_employee,
            last_logon,
            is_active,
            log)
        values (?,?,?,?,?,?,?,?,?,?,?, ?);
        """

        try:
            # connect to the database
            conn = sqlite3.connect(Database.location)
            cur = conn.cursor()

            # let's iterate through the people in the program
            # and send them to the db

            for entry in self.people:
                person = self.people[entry]  # the key is the var entry
                data = (person.first_name,
                        person.last_name,
                        person.address,
                        person.phone,
                        person.email,
                        person.notes,
                        person.username,
                        person.password,
                        person.is_employee,
                        person.is_admin,
                        int(person.is_active),
                        person.log
                        )
                cur.execute(sql_query, data)

            conn.commit()
            conn.close()

            result = True

        except sqlite3.Error as e:
            print("Error updating people database.  See following error:")
            print(e)
            result = False

        return result

    def save_items(self) -> bool:
        # first let's clear out all the items that were previously in the SQL db
        clear_rows_of("item", Database.location)
        # now we'll put all the items bak into the db
        # first let's write the SQL to update the db
        sql_query = """
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

        try:
            # connect to the database
            conn = sqlite3.connect(Database.location)
            cur = conn.cursor()

            # let's iterate through the people in the program
            # and send them to the db

            for entry in self.items:
                item = self.items[entry]  # the key is the var entry
                data = (item.name,
                        item.checked_in_by,
                        item.customer,
                        item.weight,
                        item.volume,
                        item.price,
                        item.description,
                        item.paid,
                        item.origin,
                        item.destination,
                        item.id
                        )
                cur.execute(sql_query, data)

            conn.commit()
            conn.close()

            result = True

        except sqlite3.Error as e:
            print("Error updating items database.  See following error:")
            print(e)
            result = False

        return result

    def save_places(self) -> bool:
        # first part is to clear the database of all the old places
        clear_rows_of("place", Database.location)
        # now we'll save the places
        # first let's write the SQL to update the db
        sql_query = """
        insert or replace into place (
            name,
            description,
            airport_code,
            price)
        values (?,?,?,?);
        """

        try:
            # connect to the database
            conn = sqlite3.connect(Database.location)
            cur = conn.cursor()

            # let's iterate through the people in the program
            # and send them to the db

            for entry in self.places:
                place = self.places[entry]  # the key is the var entry
                data = (place.name,
                        place.description,
                        place.airport_code,
                        place.price,
                        )
                cur.execute(sql_query, data)

            conn.commit()
            conn.close()

            result = True

        except sqlite3.Error as e:
            print("Error updating plaes database.  See following error:")
            print(e)
            result = False

        return result

    def is_in_db(self, username) -> bool:
        # takes a username and looks to see if it's in the db
        return username in self.people

    def max_item_id(self) -> int:

        if len(self.items) == 0:
            return 0
        else:
            return max([self.items[i].id for i in self.items])

    def return_item_by_id(self, id_reference) -> Item:
        # take an id number and return an item from it
        return self.items[id_reference]

