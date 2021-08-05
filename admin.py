import sqlite3
import config
from sql import query_database, clear_rows_of, insert_or_update_database
from person import Person
from item import Item
from place import Place


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
                item = Item(row=row)
                self.items[item.id] = item

            # finally the places
            place_query_rows = query_database(place_query, Database.location)
            for row in place_query_rows:
                # Iterate through all the rodes, make a new node with the lat_lons
                place = Place(row=row)
                self.places[place.name] = place

        except Exception as err:
            if isinstance(err, sqlite3.Error):
                # we can eventually put logs here
                print("There was a database error.")
                print(err)
            else:
                print("An unknown error occurred.")
                print(err)

    def save_people(self) -> None:
        # first we'll delete all the people out of the db so we don't end up with copies
        clear_rows_of("person", Database.location)
        # next let's put all the people into the database
        # first let's write the SQL to update the db

        try:

            # iterate each person and mash them into the database
            for entry in self.people:
                person = self.people[entry]  # the key is the var entry
                insert_or_update_database(Person.update_sql, person.generate_payload(), Database.location)

        except sqlite3.Error as e:
            print("Error updating people database.  See following error:")
            print(e)

    def save_items(self) -> None:
        # first let's clear out all the items that were previously in the SQL db
        clear_rows_of("item", Database.location)
        # now we'll put all the items bak into the db
        # first let's write the SQL to update the db

        try:
            # iterate through the items in the database
            # then insert or update each one into the actual SQL database
            # then
            for entry in self.items:
                item = self.items[entry]  # the key is the var entry
                insert_or_update_database(item.update_sql, item.generate_payload(), Database.location)

        except sqlite3.Error as e:
            print("Error updating items database.  See following error:")
            print(e)
            result = False

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

