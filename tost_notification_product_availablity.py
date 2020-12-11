#!/usr/bin/env python
# Flipkart Alerts by author @ github.com/4nkitd

#pip install requests
#pip install pyfiglet 
#pip install beautifulsoup4
#pip install win10toast
#pip install selenium

import re
import time
import signal
import os
import sys
import smtplib
import requests
import pyfiglet
import subprocess
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from win10toast import ToastNotifier
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

pincode = ['122051']
driver_location = 'lib/chromedriver.exe'
toaster = ToastNotifier()
regex = r".*/p/.*"
pattern = re.compile(regex)

# clear terminal
print("\033[H\033[J")

# print script name and author details.
print(pyfiglet.figlet_format("Flipkart Alerts."))
print('by Ankit on github.com/4nkitd')
print('')
print('-------------------------')
print('')

# functions

# ctrl + c exit handler


def signal_handler(sig, frame):
    print('\n\nYou pressed Ctrl+C, come again.')
    sys.exit(0)

# check selenium pincode status


def check_pincode_avl(url, pincode):
    chrome_options = Options()
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')

    browser = webdriver.Chrome(driver_location, options=chrome_options)
    browser.get(str(url))

    time.sleep(10)

    elem1 = browser.find_element_by_id("pincodeInputId")
    elem1.send_keys(pincode)

    browser.find_element_by_class_name('_2aK_gu').click()

    do = 1

    while do == 1:
        time.sleep(10)
        try:
            elm2 = browser.find_element_by_class_name('_29Zp1s')
            if elm2:
                return True
        except NoSuchElementException:
            print("-----\nNOT Avilable Now\n-----\n")
        except:
            print("-----\nUnknown Error on browser\n-----\n")    
        try:
            browser.refresh()
        except TimeoutException:
            print("-----\nInternet Issue\n-----\n")
        except:
            print("-----\nUnknown Error on refresh\n-----\n") 

# send email alert


def send_email(TO, SUBJECT, TEXT, YOUR_EMAIL, YOUR_PASS):
    # Gmail Sign In
    gmail_sender = YOUR_EMAIL
    gmail_passwd = YOUR_PASS

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_sender, gmail_passwd)

    BODY = '\r\n'.join(['To: %s' % TO,
                        'From: %s' % gmail_sender,
                        'Subject: %s' % SUBJECT,
                        '', TEXT])

    try:
        server.sendmail(gmail_sender, [TO], BODY)
        print('Email Sent')
    except:
        print('error sending mail')

    server.quit()

# stock alert


def stock_left(site):

    stock_div = site.findAll("div", {"class": "_1S11PY"})

    for stock_data in stock_div:
        return stock_data.get_text()

    return False

# get product name


def get_product_name(site):

    product_name_span = site.findAll("span", {"class": "_35KyD6"})

    for product_name_data in product_name_span:
        return product_name_data.get_text()

    return False

# check if avilable for cart


def check_availability(site):

    avilable_for_cart_div = site.findAll(
        "button", {"class": ['_2MWPVK', '_18WSRq']})
    print('.')

    for avilable_for_cart in avilable_for_cart_div:

        if avilable_for_cart.get_text().strip() == 'ADD TO CART':

            if avilable_for_cart.has_attr('disabled') == True:
                return False
            return True

    return False

# check if avilable for cart


def check_price(site):

    price_div = site.findAll("div", {"class": "_1vC4OE"})

    for price_data in price_div:
        return price_data.get_text()

    return False

# tost alert for windows


def alert(text, e, title="Flipkart Alert"):
    print(text)
    toaster.show_toast(title,
                       text,
                       icon_path=None,
                       duration=10)


# main script

signal.signal(signal.SIGINT, signal_handler)

parsed_url = urlparse(input('Flipkart Product Url : '))
print('\n')

while parsed_url.netloc != 'www.flipkart.com' or len(parsed_url.path) < 10 or pattern.match(parsed_url.path) == None:
    print('Invalid Url, Try again')
    parsed_url = urlparse(input('Flipkart Product Url : '))
    print('\n')


slp_time = input('Cycle Time in Seconds : ')

print('\n-------------------------\n')
PinCode = input('PinCode : ')

run = 1

print('Check Cycle Started\n')

while run == 1:

    r = requests.get(parsed_url.geturl())
    if r.status_code != 200:
        print('Error in Network')
        exit
    data = r.text
    site = BeautifulSoup(data, "html.parser")

    time.sleep(int(slp_time))

    p_name = get_product_name(site)
    p_price = check_price(site)
    avilable = check_availability(site)
    p_stock = stock_left(site)

    if avilable == True:
        on_pincode = check_pincode_avl(parsed_url.geturl(), PinCode)
        if on_pincode == True:
            alert_msg = ''
            if p_name != False:
                alert_msg += p_name + ' is now Avilable for '
            if p_price != False:
                alert_msg += p_price + ' '
            if p_stock != False:
                alert_msg += p_stock

            alert(alert_msg, toaster)
            run = 2
            break
