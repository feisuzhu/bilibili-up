# -*- coding: utf-8 -*-

# -- stdlib --
from argparse import ArgumentParser
from cStringIO import StringIO
import requests
import csv
import json
import sys

# -- third party --
from selenium import webdriver

# -- own --
from deathbycaptcha import SocketClient as DBCClient


# -- code --
parser = ArgumentParser('login')
parser.add_argument('list', type=str)
parser.add_argument('cookies', type=str)
options = parser.parse_args()

cookies_file = open(options.cookies, 'w')


def solve(image):
    f = StringIO()
    f.write(image)
    f.seek(0)

    dbccli = DBCClient('feisuzhu', 'feisuzhu')
    try:
        captcha = dbccli.decode(f, 60)
    except:
        print 'Error solving captcha'
        sys.exit(1)

    return captcha['text']


def do_login(driver, user, pwd):
    print 'Login'
    driver.get("https://account.bilibili.com/login")
    driver.find_element_by_id("userIdTxt").clear()
    driver.find_element_by_id("userIdTxt").send_keys(user)
    driver.find_element_by_id("passwdTxt").clear()
    driver.find_element_by_id("passwdTxt").send_keys(pwd)
    driver.find_element_by_id("vdCodeTxt").click()

    print 'Get captcha'
    resp = requests.get('https://account.bilibili.com/captcha')
    print 'Solve captcha'
    captcha = solve(resp.content)
    driver.delete_cookie('sid')
    driver.add_cookie({'name': 'sid', 'value': resp.cookies['sid']})
    print 'End solve'

    driver.find_element_by_id("vdCodeTxt").send_keys(captcha)
    driver.find_element_by_css_selector("input.login").click()
    driver.find_element_by_link_text(u"如果你的浏览器没反应，请点击这里...")

    cookies = {c['name']: c['value'] for c in driver.get_cookies()}
    print cookies
    cookies_file.write(json.dumps(cookies) + '\n')
    driver.delete_all_cookies()

driver = webdriver.Firefox()
driver.implicitly_wait(30)

for user, pwd in csv.reader(open(options.list)):
    do_login(driver, user, 'feisuzhu')

driver.close()
