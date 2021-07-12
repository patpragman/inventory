# This script runs
# barely - right now it's the test script for
# admin.py, eventually this will be the controller for the UI - however that's built

from admin import *

db = Database()

"""bob_s = Person(username="bob_s", password="1")
randy_q = Person(username="randy_q", password="2")

db.people[bob_s.username] = bob_s
db.people[randy_q.username] = randy_q""

db.save_people()
"""

randy_q = db.people["randy_q"]
bob_s = db.people["randy_q"]

"""print(randy_q.change_password("2", "hello_world"))
print(randy_q.change_password("2", "wtf"))
print(randy_q.verify_password("2"))
print(randy_q.verify_password("hello_world"))
print(randy_q.verify_password("wtf"))

db.save_people()
randy_q.log_dump()"""

print(randy_q.password)
print(randy_q.verify_password("1"))
print(randy_q.verify_password("hello_world"))
print(randy_q.verify_password("wtf"))