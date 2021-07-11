import sqlite3
import passlib


class Person:
    # Person class, contains everything you need to know
    # Default Values to give an idea of the db structure
    def __init__(self,
                 first_name: str = "Guy",
                 last_name: str = "Manderson",
                 address: str = "123 E Fuckwit",
                 phone: str = "555-555-5555",
                 email: str = "gmanderson@gmail.com",
                 username: str = "gman",
                 password: str = "unhashed_mess",
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
        self.password = password
        self.is_employee = is_employee
        self.is_admin = is_admin
        self.last_logon = None
        self.notes = notes
        self.is_active = is_active


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

                self.people[person.username] = person

            conn.close()  # close the database

        except sqlite3.Error as e:
            print("Error loading people.  See following error:")
            print(e)

        # now let's connect to the database again and snag the items
        # we use a try/except here as shitty error handling
        # we need a new SQL Query - let's make another one
        sql_query = 'select * from items'
        try:
            # connect to the database...again
            conn = sqlite3.connect(Database.location)
            cur = conn.cursor()

            # let's execute the query listed outside of the try
            cur.execute(sql_query)
            rows = cur.fetchall()  # get all the rows

            for row in rows:
                # Iterate through all the rodes, make a new node with the lat_lons
                item = Item()
                item.name = row[0]
                item.checked_in_by = row[1]
                item.customer = row[2]
                item.weight = row[3]
                item.volume = row[4]
                item.price = row[5]
                item.paid = bool(row[6])
                item.description = row[7]
                item.origin = row[8]
                item.destination = row[9]

                self.items[item.name] = item

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
        # first let's put all the people into the database
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
            is_active)
        values (?,?,?,?,?,?,?,?,?,?,?);
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
                        int(person.is_active)
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
        # now we'll put all the items bak into the db
        # first let's write the SQL to update the db
        sql_query = """
        insert or replace into items (
            name,
            checked_in_by,
            customer,
            weight,
            volume,
            price,
            paid,
            description,
            origin,
            destination)
        values (?,?,?,?,?,?,?,?,?,?);
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
                        item.paid,
                        item.destination,
                        item.origin,
                        item.destination
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