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
        # change when able
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

            conn.close() # close the database

        except sqlite3.Error as e:
            print("Error loading people.  See following error:")
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
            result =  False

        return result