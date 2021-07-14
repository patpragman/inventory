import atexit
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from admin import *
import os

app = Flask(__name__)
app.secret_key = os.urandom(50)  # set the secret key on startup

# load the database into memory
db = Database()
# when the process dies, save everything for next time
atexit.register(db.save_people)  # save people
atexit.register(db.save_items)  # save items
atexit.register(db.save_places)  # save people
# backups should be handled by a shell script

# alright - let's try setting up sessions
SESSION_COOKIE_NAME = "login_info"  # I'm spit balling here - but this is the name of the session cookie
SESSION_TYPE = "filesystem"
app.config.from_object(__name__)  # I also have no idea what this is doing
Session(app)  # this starts the session manager

@app.route("/")
def main() -> str:

    try:
        username = session["username"]
        password = session["password"]
        if username in db.people:
            if db.people[username].verify_password(password):
                print("Authentication success")
                return "Logged in as " + username
            else:
                print("Authentication Failed")
                return redirect("/login")
        else:
            print("user not found")
            return redirect("/login")
    except Exception as e:
        print("There was an error:")
        print(e)

    return "Main page. Goes here."


@app.route("/validate", methods=["post"])
def validate():
    global db

    try:
        # print("Attempting validation")  # debug
        username = request.form["username"]
        password = request.form["password"]
        # print(username, password)  # debug
        session["username"] = username
        session["password"] = password
        # print(session["username"], session["password"])  # debug

        return redirect("/")
    except Exception as e:
        print(e)
        return redirect("/login")


@app.route("/login")
def login() -> str:

    return render_template("login.html")


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
