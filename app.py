import atexit
from errors import *
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from admin import *
from person import Person
from item import Item
import datetime

app = Flask(__name__)
app.secret_key = config.Config.secret_key  # set the secret key on startup
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # this is so the browser doesn't cache the pages between loads

# load the database into memory
db = Database()
loading_cart = []

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


@app.route("/login", methods=["POST", "GET"])
@app.route("/", methods=["POST", "GET"])
def main() -> str:
    global db

    # the main page simply redirects you to the login page and does a little bit of logic to this
    # end.  First, check if he user has a valid session cookie, then check if it authenticates
    # if that works, redirect the user to the control panel for the application.  If there is no
    # valid session cookie, tell the user to login.

    if request.method == "GET":
        # first let's check to see if there's a session cookie
        try:
            # this is basically checking if the username and password have a session cookie
            # the logic is handled with the try except - if the session cookie is there, proceed
            # otherwise, just render the login template with a message
            username = session["username"]
            password = session["password"]
            # if there's no session cookie for "username and password" this will throw an error - cool
            # this takes us back to a blank login page.
            # however, if there is session cookie and we've made it this far, let's try to login
            # first check that the username from the session cookie is in the database
            if username in db.people:
                # first we should raise an error if the user isn't an employee
                if not db.people[username].is_employee:
                    raise UnknownUserError(username)
                # if it actually is in the database, check the password
                if db.people[username].verify_password(password):
                    # if the password works then go ahead and log in and redirect to the control panel
                    person = db.people[username]
                    person.last_logon = str(datetime.datetime.now())
                    person.log = person.update_log("Logged in at " + person.last_logon, "Login form")
                    return redirect("/control_panel")
                else:
                    # in this case the password didn't work - render the login page with a message
                    # stating that
                    raise InvalidPassword(username)  # throw this error if you put the wrong username in
            else:
                raise UnknownUserError(username)

        except Exception as login_error:
            if isinstance(login_error, UnknownUserError):
                return render_template("/login.html", message="Username not found.  Please try again.")
            elif isinstance(login_error, InvalidPassword):
                return render_template("/login.html", message="Authentication failed.  Check password.")
            elif isinstance(login_error, KeyError):
                #  if you're not logged in, a key_error gets thrown
                return render_template("/login.html", message="Not logged in.  Please log in.")
            else:
                print("There was some sort of error that we couldn't handle")
                print(login_error, type(login_error))
                return render_template("/login.html", message=str(login_error))

    elif request.method == "POST":
        # if you receive a post, make sure it's not blank, then reset then session variables
        # we'll hold all this inside a try except so that we can catch any errors
        try:
            username = request.form["username"]
            password = request.form["password"]
            if username == "" or password == "":
                raise BlankValueError("Username or Password is blank.")
            # if we made it this far without throwing an error let's reset the session cookies
            # and send the user back to the main page with a redirect
            session["username"] = username
            session["password"] = password
            return redirect("/")
        except Exception as posting_error:
            if isinstance(posting_error, BlankValueError):
                # if you didn't type anything in, render the login form again with a message
                return render_template("/login.html", message=posting_error.note)
            else:
                print("There was an error during the post operation.")
                print(posting_error)
                return render_template("/login.html", message=posting_error)
    else:
        return "POST or GET are the only supported methods."


@app.route("/control_panel")
def control_panel():
    global db
    # again check to see if the user is logged in, otherwise send them back to login
    try:
        try:
            person = db.people[session["username"]]
        except Exception as err:
            # print the exception in case it's something else then raise a NotLoggedInError
            # this could be bad if something else caused this to fail, but it starts the debug process at least
            print(err)
            raise NotLoggedInError("There was an error while trying to get to the control panel page.")

        return render_template("/control_panel.html", person=person)

    except Exception as err:
        # something happened when trying to load the session token
        # rather, regardless don't redirect to the control panel in
        # that case, send them somewhere else and try again
        print(err)
        return redirect("/")


@app.route('/remove_all', methods=["GET"])
def remove_all() -> str:
    global db
    global loading_cart

    loading_cart.clear()

    return redirect("/cart")


@app.route("/ship_all", methods=["GET"])
def ship_all() -> str:
    global db
    global loading_cart

    # iterate through the list and take everything out of the dictionary
    for item in loading_cart:
        # this shadows the name id here - and could be confusing
        # I should fix this at some time
        id = item.id
        db.items.pop(id)

    # now empty the whole db
    loading_cart.clear()

    return redirect("/control_panel")


# stolen and adapted from stack exchange
# https://stackoverflow.com/questions/14032066/can-flask-have-optional-url-parameters
# I think this is the most reasonable
@app.route('/cart')
@app.route('/cart/<status>/<item_id>', methods=["GET", "POST"])
def cart(status=0, item_id=None) -> str:
    # grab the db copy
    # also load up the cart
    global db
    global loading_cart

    """
    debug
    print("status:  ", status)  # debug
    print("item_id:  ", item_id)  # debug
    """
    try:
        # check to see if logged in - otherwise panic!
        try:
            person = session["username"]  # I wonder if there's a better way to do this
        except Exception as err:
            print(err)
            raise NotLoggedInError()

        # this method is "GET" only
        if request.method == "POST":
            raise InvalidRequest('Only "GET" is acceptable with this method.')
        elif request.method == "GET":
            # now that we've made it this far into the method, let's change the strings coming from
            # the browser into integers so they can interface comfortably with the database dictionary
            # you can do it by usings strings or some sort of id, but it's easier to just mash them into
            # integers
            status = int(status)

            if item_id is not None:
                # we get an error if the item_id is the default - this is fine but we want
                # just only want type-cast this to an int in the event that there's actually
                # an item_id attached to this
                item_id = int(item_id)

            # now we need to check to see if it is a load or not
            if status == 0:
                # if nothing was done return the cart page
                # print("made it to here - status 0")  # debug
                return render_template("carts.html",
                                       cart=loading_cart,
                                       user=db.people[session["username"]],
                                       people=[db.people[person] for person in db.people],
                                       places=[db.places[place] for place in db.places],
                                       items=[db.items[item] for item in db.items])
            elif status == 1:
                # this is a load GET request
                # handle loading stuff to the cart here
                # all the QR codes have this particular request status
                for item in db.items:
                    working_item = db.items[item]
                    if working_item.id == item_id:
                        loading_cart.append(working_item)
                        return redirect("/edit_item")

                # now redirect to the cart again
                raise ItemNotFound()

            elif status == 2:
                # handle a deleting stuff out of the cart here
                for item in db.items:
                    working_item = db.items[item]

                    if working_item.id == item_id:
                        # if this matches, pop it off the list and redirect
                        loading_cart.remove(working_item)
                        return redirect("/cart")

                raise ItemNotFound()
            elif status == 3:
                # here's where we're going to transfer you to the label gen template
                return render_template("label.html",
                                       item=db.items[item_id],
                                       user=db.people[session["username"]],
                                       address="https://" + config.Config.global_addy + db.items[item_id].make_cart_load_url())
            else:
                raise InvalidRequest("Carts meed the variable 0, 1, 2, or 3.  Those values must be interpreted by Flask as strings, and type casting might have broken.")

    except Exception as err:
        if isinstance(err, NotLoggedInError):
            # if you're not logged in go back to the redirect page
            return redirect("/")
        elif isinstance(err, InvalidRequest):
            # if it's an invalid request return the error
            return str(err)
        elif isinstance(err, ItemNotFound):
            # if it's a missing item shoot that error out to the browser
            return str(err)
        else:
            # if it's something else, return the error to the browser
            print(err)
            return str(err)


@app.route("/edit_item", methods=["POST", "GET"])
def edit_item() -> str:
    global db

    try:
        if request.method == "GET":
            #  print("received a get request")  # debug
            # if it's a get request, render the editor template
            # we're passing the user to the template,
            # we're passing a list of people objects to the template
            # and we're passing a list of item objects to the template
            return render_template("edit_item.html",
                                   user=db.people[session["username"]],
                                   people=[db.people[person] for person in db.people],
                                   items=[db.items[item] for item in db.items if db.items[item] not in loading_cart],
                                   places=[db.places[place] for place in db.places])
        elif request.method == "POST":
            # if it's posting data, get the particular data it's posting and adjust the adjust the
            # item in question
            item = db.items[int(request.form["id"])]
            item.name = request.form["name"]
            item.description = request.form["description"]
            item.origin = request.form["origin"]
            item.destination = request.form["destination"]
            item.checked_in_by = request.form["checked_in_by"]
            item.customer = request.form["customer"]
            item.weight = request.form["weight"]

            return redirect("/edit_item")
        else:
            # while we're implementing this, if anything breaks, panic and throw a flag
            raise Exception
    except Exception as err:
        print("Error!")
        print(err)
        return "There was an error! " + str(err)


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
        # check the password match on the server - otherwise back around you go!
        if new_password == verify_pass:
            # print("Password changed!")  # debug
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
        del db.people[old_name]  # get rid of the old name in the database using the old username in case its changed
        db.people[person.username] = person
        # now change the session cookies as appropriate
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


@app.route("/new_user", methods=["POST", "GET"])
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
            person.update_log("Created new user", by=person.username)
            # now we have to change the underlying object in the db
            db.people[person.username] = person
            session["username"] = person.username
            session["password"] = person.password
            person.is_employee = True

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


@app.route("/edit_customer", methods=["POST", "GET"])
def edit_customer() -> str:
    # first get the database of all the stuff we're working with
    global db
    try:
        # everything is buried inside some error handling
        # then we evaluate if it's a "POST" or a "GET" request
        if request.method == "POST":
            # first retrieve the person out of the db using the username in the form
            username = request.form["name"]
            person = db.people[username]
            # now update all the data
            person.first_name = request.form["first_name"]
            person.last_name = request.form["last_name"]
            person.notes = request.form["notes"]
            person.phone = request.form["phone"]
            person.email = request.form["email"]
            person.address = request.form["address"]
            # after you've changed eveerything, redirect to the "edit customer page" again
            for person in db:
                print(person.username)  # debug
            return redirect("/edit_customer")
        elif request.method == "GET":
            # return the edit customer template
            return render_template("edit_customer.html",
                                   user=db.people[session["username"]],
                                   people=[db.people[person] for person in db.people])
        else:
            raise InvalidRequest("edit_customer can only understand GET and POST requests.")
    except Exception as err:
        print(err)
        return str(err)


@app.route("/new_customer", methods=["GET", "POST"])
def new_customer() -> str:
    global db
    # first we'll wrap the whole thing inside some exception handling
    try:
        if request.method == "POST":
            customer = Person()
            customer.username = str(request.form["first_name"][0]) + str(request.form["last_name"])
            customer.first_name = request.form["first_name"]
            customer.last_name = request.form["last_name"]
            customer.notes = request.form["notes"]
            customer.phone = request.form["phone"]
            customer.address = request.form["address"]
            customer.email = request.form["email"]
            customer.is_employee = False
            customer.is_active = True
            if customer.username in db.people:
                customer.username = customer.username + "copy"  # if there's a duplicate append copy to the name

            db.people[customer.username] = customer
            return redirect("edit_customer")

        elif request.method == "GET":
            # if it's a get request, use the render template for making a new customer
            return render_template("new_customer.html", message="Please enter new customer information.")
        else:
            raise InvalidRequest("/create_new_customer can only accept a get or a post.")
    except Exception as err:
        print(err)
        return str(err)


@app.route("/edit_personal_user")
def edit_personal_user() -> str:
    global db

    try:
        person = db.people[session["username"]]
        return render_template("edit_personal_user.html", person=person)
    except Exception as err:
        print(err)
        redirect("/")


@app.route("/new_item", methods=["post", "get"])
def new_item() -> str:
    global db
    # if you're getting a page from the server - render the appropriate template
    if request.method == "GET":
        return render_template("/new_item.html",
                                   user=db.people[session["username"]],
                                   people=[db.people[person] for person in db.people],
                                   items=[db.items[item] for item in db.items],
                                   places=[db.places[place] for place in db.places])
    elif request.method == "POST":
        try:
            # ok - if it's a post message, try to create a new item and add it to the cue
            item = Item()

            # we're going to make a new item, so let's figure out the highest numbered item first in the list
            # so we don't accidentally assign a previously used value
            # also, this can screw you over if there are no items in the database

            new_id = db.max_item_id() + 1
            item.id = new_id
            item.name = request.form["name"]
            item.checked_in_by = request.form["checked_in_by"]
            item.customer = request.form["customer"]
            item.weight = request.form["weight"]
            item.price = request.form["price"]
            item.description = request.form["description"]
            item.origin = request.form["origin"]
            item.destination = request.form["destination"]
            db.items[item.id] = item

            item.cart_load_url = item.make_cart_load_url()
            item.cart_unload_url = item.make_cart_remove_url()
            item.qr_code_url = item.make_qr_redirect_url()

            return redirect("/edit_item")

        except Exception as err:
            print("Catastrophe!  Gnashing of teeth!  The following error occurred.")
            print(err)
            return str(err)
    else:
        print("POST and GET are the only acceptable requests.")
        return "POST and GET are the only acceptable requests."


@app.route("/logout")
def logout() -> None:

    session.clear()  # clear the session history then go back to the main page
    return redirect("/")


@app.route("/new_place", methods=["GET", "POST"])
def new_place() -> str:
    # we'll access the global db
    global db
    try:
        if request.method == "GET":
            return redirect("/edit_place")
        elif request.method == "POST":
            place = Place()
            place.name = request.form["name"]
            place.airport_code = request.form["airport_code"]
            place.description = request.form["description"]
            # place.price = request.form["price"]  # when implemented
            db.places[request.form["name"]] = place
            return redirect("/edit_place")
        else:
            raise InvalidRequest("Only supported methods are GET and POST.")
    except Exception as err:
        print(err)
        return str(err)


@app.route("/edit_place", methods=["GET", "POST"])
def edit_places() -> str:
    # like all the other methods we'll get the global database, then
    # wrap the handling into some try and except statements to handle the errors
    global db
    try:
        if request.method == "GET":
            # all get requests get the "edit place" template
            return render_template("edit_places.html",
                                   message="",
                                   user=session["username"],
                                   places=[db.places[place] for place in db.places])
        elif request.method == "POST":
            # get the referenced place
            new_name = request.form["name"]
            place = db.places[new_name]
            old_name = place.name  # copy the old name so we can pop it out of the dictionary later
            place.name = request.form["new_name"]  # get the new name
            place.airport_code = request.form["airport_code"]
            place.description = request.form["description"]
            db.places[place.name] = place
            # finally, delete the old key-value pair
            del db.places[old_name]

            return render_template("edit_places.html",
                                   user=session["username"],
                                   message="Successfully edited place.",
                                   places=[db.places[place] for place in db.places])
        else:
            raise InvalidRequest("Only GET and POST are valid request types.")
    except Exception as err:
        print(err)
        return str(err)


# we'll use SSL to hide submitted passwords
if __name__ == '__main__':
    app.run(ssl_context=config.Config.ssl_context)

