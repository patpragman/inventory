class DucplicateUserError(Exception):

    def __init__(self, duplicate_username: str, attempting_user: str):

        self.duplicate_username = duplicate_username
        self.attempting_user = attempting_user

    def __str__(self):
        return "User " + self.duplicate_username + " already exists in the database."

class UnknownUserError(Exception):

    def __init__(self, username):

        self.username_guess = username

    def __str__(self) -> str:

        return "User " + self.username_guess + " is not found."

class BlankValueError(Exception):

    def __init__(self, note):

        self.note = note

    def __str__(self) -> str:

        return "The server didn't recieve the required data.  " + self.note

class InvalidPassword(Exception):

    def __init__(self, attempted_user: str) -> None:

        self.attempted_user = attempted_user

    def __str__(self) -> str:

        return "Invalid password attempt for logon: " + self.attempted_user


class NotLoggedInError(Exception):

    def __init__(self, note) -> None:

        self.note = note

    def __str__(self) -> str:

        return "Trying to access a page while not logged in. " + self.note

class InvalidRequest(Exception):

    def __init__(self, note):
        self.note = note

    def __str__(self):
        return self.note