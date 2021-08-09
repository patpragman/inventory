# this test uses selenium to attempt to login over the local host
# user is "Patrick"
# password is a highly secure "a"
# note that this is a vulnerability if you aren't running your own DB

from seleniumrequests import Safari
from selenium import webdriver

address = "https://ciegoservices.pythonanywhere.com/"


def test_login():
    user = "Patrick"
    password = "a"
    # start the web driver
    driver = webdriver.Safari()
    driver.get(address + "logout")

    username_id = driver.find_element_by_id("username_id")
    password_id = driver.find_element_by_id("password_id")
    submit = driver.find_element("submit")

    print(username_id.id)
    print(password_id.cl)

test_login()
