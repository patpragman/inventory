# This script runs

from admin import *

print("hello world...")
# test change git!

db = Database()


for name in db.people:
    print(db.people[name].username)