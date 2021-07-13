import atexit
from flask import Flask, render_template, request, redirect
from admin import *

app = Flask(__name__)

# load the database into memory
db = Database()
# when the process dies, save everything for next time
atexit.register(db.save_people)  # save people
atexit.register(db.save_items)  # save items
atexit.register(db.save_places)  # save people
# backups should be handled by a shell script


@app.route("/")
def main() -> str:

    return "Main page. Goes here."


@app.route("/login")
def login() -> str:

    return "Login goes here."


@app.route("/user_list")
def user_list() -> str:
    # this is the start of
    output = str([person for person in db.people])
    return output


@app.route("/new_user")
def new_user() -> str:

    return "New user."


# we'll use SSL to hide submitted passwords
if __name__ == '__main__':
    app.run(ssl_context="adhoc")
