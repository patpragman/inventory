import sqlite3
from passlib.context import  CryptContext
import datetime
import config


class Person:
    # Person class, contains everything you need to know
    # Default Values to give an idea of the db structure
    # password context is global to all "person classes"
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"],
                               deprecated="auto",
                               )  # this is the password context for passlib

    def __init__(self,
                 first_name: str = "Guy",
                 last_name: str = "Manderson",
                 address: str = "123 E Fuckwit",
                 phone: str = "555-555-5555",
                 email: str = "gmanderson@gmail.com",
                 username: str = "gman",
                 password: str = pwd_context.hash("default_garbage"),
                 is_employee: bool = False,
                 is_admin: bool = False,
                 notes: str = "Empty note.",
                 is_active: bool = True) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.phone = phone
        self.email = email
        self.username = username
        self.password = Person.pwd_context.hash(password)
        self.is_employee = is_employee
        self.is_admin = is_admin
        self.last_logon = None
        self.notes = notes
        self.is_active = is_active
        self.log = "Log: \n"

    def verify_password(self, password: str) -> bool:
        result = Person.pwd_context.verify(password, self.password)
        event_time = str(datetime.datetime.now())  # make a string object to record the time of the last attempt

        if result:
            self.last_logon = event_time  # password verified
            self.log = str(self.log) + "\nPassword Verified at:" + str(event_time)
        else:
            self.log = str(self.log) + "\nPassword verification failure at: " + str(event_time)
            print("Password verification failure at: " + str(event_time))

        return result

    def change_password(self, new_password: str) -> None:
            self.password = Person.pwd_context.hash(new_password)
            self.update_log("password updated")

    def update_log(self, event: str = "default log event", by: str="sofware") -> None:
        right_now = str(datetime.datetime.now())
        self.log = event + " " + right_now+ " by " + by

    def log_dump(self) -> None:
        print(self.log)
        return self.log

    def log_purge(self, by="software") -> None:
        self.log = ""
        self.update_log("Logs purged", by=by)


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
        base_url = config.Config.local_url

        return base_url + "cart/" "1" + "/" + str(self.id)

    def make_cart_remove_url(self) -> str:
        # takes a cart item and produces a cart load url
        # recall that a status of
        base_url = config.Config.local_url

        return base_url + "cart/" + "2" + "/" + str(self.id)

    def make_qr_redirect_url(self) -> str:
        # takes a cart item and produces a cart load url
        # recall that a status of
        base_url = config.Config.local_url

        return base_url + "cart/" + "3" + "/" + str(self.id)


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

        def __init(self) -> None:

            self.description = "Generic Cart"  # this should be editable by the user
            self.items = [Item]  # this should be a list of items
            self.creator: Person = None



class Database:
    location = "inventory.db"

    def __init__(self):
        # these dictionaries will hold data we need
        self.people = {}
        self.items = {}
        self.places = {}

        # first let's write the SQL to update the db
        sql_query = 'select * from person'

        # i repeat the following code multiple times for items and places
        # why?  because I haven't refactored it yet - also because I'm lazy
        # change when able, make this programmatic or whatever, for now, yeah
        # also I'm not sure if this would be come a mess of dependencies either
        # seems easier just to be explicit about what we're doing here.
        try:
            # connect to the database
            conn = sqlite3.connect(Database.location)
            cur = conn.cursor()

            # let's execute the query listed outside of the try
            cur.execute(sql_query)
            rows = cur.fetchall()  # get all the rows

            for row in rows:
                # Iterate through all the rodes, make a new node with the lat_lons
                person = Person()
                person.first_name = row[0]
                person.last_name = row[1]
                person.address = row[2]
                person.phone = row[3]
                person.email = row[4]
                person.notes = row[5]
                person.username = row[6]
                person.password = row[7]
                person.is_employee = bool(row[8])
                person.is_admin = bool(row[9])
                person.last_logon = row[10]
                person.is_active = row[11]
                person.log = row[12]

                self.people[person.username] = person

            conn.close()  # close the database

        except sqlite3.Error as e:
            print("Error loading people.  See following error:")
            print(e)

        # now let's connect to the database again and snag the items
        # we use a try/except here as shitty error handling
        # we need a new SQL Query - let's make another one
        sql_query = 'select * from item'
        try:
            # connect to the database...again
            conn = sqlite3.connect(Database.location)
            cur = conn.cursor()

            # let's execute the query listed outside of the try
            cur.execute(sql_query)
            rows = cur.fetchall()  # get all the rows

            for row in rows:
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
                item.qr_code_url = item.make_qr_redirect_url()

                self.items[item.id] = item

            conn.close()  # close the database

        except sqlite3.Error as e:
            print("Error loading items.  See following error:")
            print(e)

        # same thing as above but we're get the places
        sql_query = 'select * from place'
        try:
            # connect to the database...again
            conn = sqlite3.connect(Database.location)
            cur = conn.cursor()

            # let's execute the query listed outside of the try
            cur.execute(sql_query)
            rows = cur.fetchall()  # get all the rows

            for row in rows:
                # Iterate through all the rodes, make a new node with the lat_lons
                place = Place()
                place.name = row[0]
                place.description = row[1]
                place.airport_code = row[2]
                place.price = row[3]

                self.places[place.name] = place

            conn.close()  # close the database

        except sqlite3.Error as e:
            print("Error loading places.  See following error:")
            print(e)

    def save_people(self) -> bool:
        # first we'll delete all the people out of the db so we don't end up with copies
        self.clear_rows_of("person")
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
        self.clear_rows_of("item")
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
                item = self.items[entry] # the key is the var entry
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
        self.clear_rows_of("place")
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
                place = self.places[entry] # the key is the var entry
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

    def return_item_by_id(self, id) -> Item:
        # take an id number and return an item from it
        return self.items[id]

    def clear_rows_of(self,table) -> None:
        try:
            # this will clear all the stuff from whatever table you specify
            statement = """DELETE from """ + str(table) + ";"
            conn = sqlite3.connect(Database.location)
            cur = conn.cursor()
            cur.execute(statement)
            conn.commit()
        except Exception as err:
            print("Error processing SQL in clear_rows_of function")
            print(err)





