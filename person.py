from passlib.context import CryptContext
import datetime


class Person:
    # Person class, contains everything you need to know
    # Default Values to give an idea of the db structure
    # password context is shared by all "person classes"
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"],
                               deprecated="auto")  # this is the password context for passlib

    update_sql = """
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
                 is_active: bool = True,
                 row: list = None) -> None:

        if row is not None:
            self.first_name = row[0]
            self.last_name = row[1]
            self.address = row[2]
            self.phone = row[3]
            self.email = row[4]
            self.notes = row[5]
            self.username = row[6]
            self.password = row[7]
            self.is_employee = bool(row[8])
            self.is_admin = bool(row[9])
            self.last_logon = row[10]
            self.is_active = row[11]
            self.log = row[12]
        else:
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

    def update_log(self, event: str = "default log event", by: str = "sofware") -> None:
        right_now = str(datetime.datetime.now())
        self.log = event + " " + right_now + " by " + by

    def log_dump(self) -> None:
        print(self.log)

    def log_purge(self, by="software") -> None:
        self.log = ""
        self.update_log("Logs purged", by=by)

    def generate_payload(self) -> tuple:

        data = (self.first_name,
                self.last_name,
                self.address,
                self.phone,
                self.email,
                self.notes,
                self.username,
                self.password,
                self.is_employee,
                self.is_admin,
                int(self.is_active),
                self.log
                )
        return data

