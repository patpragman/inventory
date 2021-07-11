# This script runs
# barely - right now it's the test script for
# admin.py, eventually this will be the ui

from admin import *

print("hello world...")
# test change git!

db = Database()


for name in db.people:
    print(db.people[name].username)