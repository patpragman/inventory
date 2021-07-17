class DucplicateUserError(Exception):

    def __init__(self, duplicate_username: str, attempting_user: str):

        self.duplicate_username = duplicate_username
        self.attempting_user = attempting_user

    def __str__(self):
        return "User " + self.duplicate_username + " already exists in the database."