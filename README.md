# inventory controller

### pat pragman

### License

This project uses the MIT License - see associated files.

### Update 7/12/2021:
got password hashing and verification to work, set up logging for password verificiation, and ability to purge logs.  Tested the code in the main "inventory.py" section.  Passwords are stored in the db in a hash, password verification works.  Created a method to test if a username already existed in the database.

### Update 7/25/2021:
quite a bit since last time - I've done numerous commits creating the majority of the app.
It could use refactoring, but as of right now, here's how it works - you can create and edit items, places, and people.
You can store things in the "warehouse" and you can create "carts" that allow you to check them out of the warehouse.
There are still bugs and glitches but for the most part it seems to function as advertised.  Next up is QR code labels.

### Update 8/9/2021

It's pretty much the way I'd like it now.  Yes there's a lot more I could do, however I think I'm going to move on to some other projects for the time being.
You can create users, create airports, log in, and check items out of the warehouse.  If this was going to production there's a lot more I'd do, but for the time being I'm going to shelve this project to start learning some new stuff.

If you're reading this, send me an email at pat@pragman.io with any questions.