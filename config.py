# eventually I'll manage all the dependencies in here I think

class Config:
    # config status for setting up individual instances of the app
    local_url = "/"
    global_addy = "https://ciegoservices.pythonanywhere.com"

    # dev server stuff
    ssl_context = "adhoc"
    host = "192.168.86.69"

    secret_key = b"""\x92Ja\xc6u\xa83\x0b\xac\x84\x91\xf2O\x00\xa6<a\xa1\xdd^\xf5\xcc\xf5
                    \xe1\xca\xa5\xf0>\xf60\\\xb4<a\x9e\xa6\xff\x15\xa1*O\x12D&Mq\x0f\x96\
                    x07o'"""