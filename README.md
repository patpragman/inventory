# inventory controller

### pat pragman

This is the "do whatever the hell you want with it license" - no seriously, do anything you want with this.  Eventually this will be something, but now it's not much.  Presently it's just an extremely crude connection between a couple of python objects and a SQLite database.

### Update 7/12/2021:
got password hashing and verification to work, set up logging for password verificiation, and ability to purge logs.  Tested the code in the main "inventory.py" section.  Passwords are stored in the db in a hash, password verification works.  Created a method to test if a username already existed in the database.

### Update 7/25/2021:
quite a bit since last time - I've done numerous commits creating the majority of the app.
It could use refactoring, but as of right now, here's how it works - you can create and edit items, places, and people.
You can store things in the "warehouse" and you can create "carts" that allow you to check them out of the warehouse.
There are still bugs and glitches but for the most part it seems to function as advertised.  Next up is QR code labels.