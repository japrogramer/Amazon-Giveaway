import argparse
import glob
import subprocess
import time
import zipfile
import re

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.common.exceptions import NoSuchElementException

binary = FirefoxBinary('/usr/bin/firefox')
output_path = '/home/archangel/Desktop/Seeds'
profile = webdriver.FirefoxProfile()
profile.set_preference('browser.download.folderList', 2);
profile.set_preference('browser.download.manager.showWhenStarting', False)
profile.set_preference('browser.download.dir', output_path);
profile.set_preference('browser.download.useDownloadDir', True);
profile.set_preference("browser.helperApps.neverAsk.saveToDisk",
                       'application/octet-stream'+
                       ',application/zip'+
                       ',text/plain'+
                       ',application/x-rar-compressed'+
                       ',application/x-gzip'+
                       ',application/msword')

# options = webdriver.FirefoxOptions()
# options.add_argument('-headless')

# browser = webdriver.Firefox(firefox_options=options, firefox_profile=profile, firefox_binary=binary)
browser = webdriver.Firefox(firefox_profile=profile, firefox_binary=binary)


parser = argparse.ArgumentParser(description="Options for mailchimp test")
parser.add_argument('--shell', action='store_true')
parser.add_argument('--update', action='store_true')


def ipython(loc):
    from IPython import start_ipython
    start_ipython(argv=[], user_ns=loc)


def enter_shell(loc):
    try:
        ipython(loc)
    except ImportError:
        import code
        code.interact(local=loc)


def enter_text(element_id, message, hide=False):
    tt = browser.find_element_by_id(element_id)
    tt.click()
    if hide:
        from getpass import getpass
        text = getpass(message)
    else:
        print(message)
        text = input()
    tt.send_keys(text)


def login(url):
    browser.get(url)
    time.sleep(3)
    try:
        enter_text('ap_email', 'Enter username')
        time.sleep(1)
        enter_text('ap_password', 'Enter password', hide=True)
        sign_in = browser.find_element_by_id('signInSubmit')
        sign_in.click()
        try:
            tt = browser.find_element_by_id('auth-mfa-otpcode')
            if tt:
                enter_text('auth-mfa-otpcode', 'Enter verification')
                tt = browser.find_element_by_id('auth-signin-button')
                tt.click()
        except NoSuchElementException:
            pass

    except NoSuchElementException:
        print('error', url)
    finally:
        time.sleep(1)


def main(u):
    login('https://smile.amazon.com/')
    from giveaway_clickbater import navigator
    navigator(browser)


if __name__ == '__main__':
    args = parser.parse_args()
    update = False
    if args.shell:
        enter_shell(locals())
    if args.update:
        update = True

    main(update)

