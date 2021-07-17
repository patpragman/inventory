import atexit
import datetime
from errors import *

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

# carts are stored in this variable this should be persistent betwen sessions but doesn't need to be stored in the db
carts = [Cart]


@app.route("/")
def main() -> str:

    # the main page simply redirects you to the login page and does a little bit of logic to this
    # end.  First, check if he user has a valid session cookie, then check if it authenticates
    # if that works, redirect the user to the control panel for the application.  If there is no
    # valid session cookie, tell the user to login.

    try:
        # this is basically checking if the username and password have a session cookie
        # the logic is handled with the try except - if the session cookie is there, proceed
        # otherwise, just render the login template with a message
        username = session["username"]
        password = session["password"]
        print(username, password) # debug
        if username in db.people:
            if db.people[username].verify_password(password):
                #  print("Authentication success", username, password)  # debug
                person = db.people[username]
                person.last_logon = str(datetime.datetime.now())
                person.log = person.update_log("Logged in at " + person.last_logon, "Login form")
                return redirect("/control_panel")
            else:
                return render_template("/login.html", message="Authentication Failed")
        else:
            raise UnknownUserError(username)
    except Exception as e:
        if isinstance(e, UnknownUserError):
            return render_template("/login.html", message="Username not found.  Please try again.")
        else:
            print("There was an unkown error:")
            print(e)
            return render_template("/login.html", message="Not logged in, please log in.")


@app.route("/validate", methods=["post"])
def validate():
    global db

    try:
        # print("Attempting validation")  # debug
        username = request.form["username"]
        password = request.form["password"]

        # if either of the values from the form are missing
        # then throw an error
        if username == "" or password == "":
            raise BlankValueError("Username or Password is blank.")

        # similarly, if the username isn't in the database throw an error
        if username not in db.people:
            raise UnknownUserError(username)

        # print(username, password)  # debug
        session["username"] = username
        session["password"] = password
        # print(session["username"], session["password"])  # debug
        person = db.people[username]

        if person.verify_password(password):
            return redirect("/control_panel")
        else:
            return redirect("/")
    except Exception as e:
        if isinstance(e, UnknownUserError):
            return render_template("/login.html", message="Username not found.  Please try again.")
        elif isinstance(e, BlankValueError):
            return render_template("/login.html", message = str(e))
        else:
            print(e)
            return redirect("/login")


@app.route("/login")
def login() -> str:

    return render_template("login.html", message="Please Log in.")


@app.route("/user_list")
def user_list() -> str:
    # this is the start of
    output = str([person for person in db.people])
    return output


@app.route("/control_panel")
def control_panel() -> str:
    global db
    # again check to see if the user is logged in, otherwise send them back to login
    try:
        #  print(session["username"])  # debug
        person = db.people[session["username"]]
        return render_template("/control_panel.html", person=person)

    except Exception as e:
        print(e)
        return redirect("/")


@app.route("/amend_personal_data", methods=["post"])
def amend_personal_data() -> str:
    global db
    # again check to see if the user is logged in, otherwise send them back to login
    try:
        person = db.people[session["username"]]

        # if that worked without throwing an exception - go through and update this data
        # now let's verify that username isn't already in the db
        """print("Trying to evaluate the form.")  # debug code
        for form_data in request.form:
            print(form_data, request.form[form_data])"""

        if request.form["username"] in db.people:
            # if the desired is not the user's name already
            if request.form["username"] != person.username:
                # if the username is already in use raise a specific error to take you
                # back to the appropriate page
                raise DucplicateUserError(request.form["username"], person.username)

        # take all the post data and jam it into the person object
        old_name = person.username
        person.username = request.form["username"]

        new_password = request.form["password"]
        verify_pass = request.form["verify_pass"]
        if new_password == verify_pass:
            print("Password changed!")  # debug
            person.change_password(new_password)
            person.update_log("Password changed", by=person.username)
        else:
            return render_template("edit_personal_user.html",
                                   person=person,
                                   message="Error updating passwords, please try again.")

        person.first_name = request.form["first_name"]
        person.last_name = request.form["last_name"]
        person.phone = request.form["phone"]
        person.address = request.form["address"]
        person.email = request.form["email"]
        person.notes = request.form["notes"]
        person.log = person.update_log("Updated personal details", by=person.username)
        # now we have to change the underlying object in the db
        db.people.pop(old_name)
        db.people[person.username] = person
        session["username"] = person.username
        session["password"] = person.password
        # now go back to the control panel
        return redirect("/control_panel")

    except Exception as err:
        print(err)
        if isinstance(err, DucplicateUserError):
            return render_template("edit_personal_user.html",
                                   message="Username already exists.",
                                   person=db.people[err.attempting_user])
        else:
            return redirect("/login")

@app.route("/new_user", methods=["post", "get"])
def new_user() -> str:
    global db
    # again check to see if the user is logged in, otherwise send them back to login
    if request.method == "POST":
        try:
            person = Person()
            # this code is very similar to the amend user code
            # however you aren't checking session data because you're a new user

            if request.form["username"] in db.people:
                # if the user is user is already in the db, raise a flag
                raise DucplicateUserError(request.form["username"], "new user")

            person.username = request.form["username"]
            new_password = request.form["password"]
            verify_pass = request.form["verify_pass"]
            person.first_name = request.form["first_name"]
            person.last_name = request.form["last_name"]
            person.phone = request.form["phone"]
            person.address = request.form["address"]
            person.email = request.form["email"]
            person.notes = request.form["notes"]
            person.log = person.update_log("Created new user", by=person.username)
            # now we have to change the underlying object in the db
            db.people[person.username] = person
            session["username"] = person.username
            session["password"] = person.password

            if new_password == verify_pass:
               # print("Password changed!")  # debug
                person.change_password(new_password)
                person.update_log("Password changed", by=person.username)
            else:
                return render_template("new_user.html",
                                       message="Error updating passwords, please try again.")
            # now go back to the control panel
            db.people[person.username] = person
            return redirect("/control_panel")


        except Exception as err:
            print(err)
            if isinstance(err, DucplicateUserError):
                return render_template("new_user.html",
                                       message="Username already exists.",
                                       person="new user")
    else:
        return render_template("new_user.html", message="Enter your information please!")

@app.route("/edit_personal_user")
def edit_personal_user() -> str:
    global db

    try:
        person = db.people[session["username"]]
        return render_template("edit_personal_user.html", person=person)
    except Exception as err:
        print(err)
        redirect("/")

@app.route("/logout")
def logout() -> None:

    session.clear()  # clear the session history then go back to the main page
    return redirect("/")


# we'll use SSL to hide submitted passwords
if __name__ == '__main__':
    app.run(ssl_context="adhoc")
