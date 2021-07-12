# inventory controller

### pat pragman

This is the "do whatever the hell you want with it license" - no seriously, do anything you want with this.  Eventually this will be something, but now it's not much.  Presently it's just an extremely crude connection between a couple of python objects and a SQLite database.

### Update 7/12/2021:
got password hashing and verification to work, set up logging for password verificiation, and ability to purge logs.  Tested the code in the main "inventory.py" section.  Passwords are stored in the db in a hash, password verification works.  Created a method to test if a username already existed in the database.

