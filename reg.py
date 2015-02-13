# -*- coding: utf-8 -*-

# -- stdlib --
from cStringIO import StringIO
import argparse
import csv
import sys
import time

# -- third party --
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType

# -- own --
from deathbycaptcha import SocketClient as DBCClient


# -- code --
parser = argparse.ArgumentParser('scanproxy')
parser.add_argument('list')
parser.add_argument('--proxy', default='')
options = parser.parse_args()


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


def do_reg(account, password, nick):

    if options.proxy:
        proxy = Proxy({
            'proxyType': ProxyType.MANUAL,
            'httpProxy': options.proxy,
            'ftpProxy': '',
            'sslProxy': options.proxy,
            'noProxy': '',
        })
    else:
        proxy = Proxy({'proxyType': ProxyType.DIRECT})

    driver = webdriver.Firefox(proxy=proxy)
    driver.implicitly_wait(30)

    driver.get("https://account.bilibili.com/register/mail")
    driver.find_element_by_name("uname").clear()
    driver.find_element_by_name("uname").send_keys(account + "@163.com")
    driver.find_element_by_id("vdCodeTxt").click()

    '''
    print 'Get captcha'
    resp = requests.get('https://account.bilibili.com/captcha')
    print 'Solve captcha'
    captcha = solve(resp.content)
    driver.delete_cookie('sid')
    driver.add_cookie({'name': 'sid', 'value': resp.cookies['sid']})
    print 'End solve'
    '''

    print 'Captcha:'
    captcha = raw_input().strip()

    driver.find_element_by_id("vdCodeTxt").clear()
    driver.find_element_by_id("vdCodeTxt").send_keys(captcha)
    driver.find_element_by_id("agree").click()
    driver.find_element_by_id("emailStn").click()

    driver.find_element_by_link_text(u"查看验证邮箱")

    mail = webdriver.Firefox(proxy=Proxy({'proxyType': ProxyType.DIRECT}))
    mail.implicitly_wait(30)

    mail.get('http://mail.163.com')
    mail.find_element_by_id("idInput").click()
    mail.find_element_by_id("idInput").clear()
    mail.find_element_by_id("idInput").send_keys(account)
    mail.find_element_by_id("pwdInput").click()
    mail.find_element_by_id("pwdInput").clear()
    mail.find_element_by_id("pwdInput").send_keys(password)
    mail.find_element_by_id("loginBtn").click()

    mail.find_element_by_id("_mail_tree_1_50count").click()
    mail.find_element_by_css_selector("span.da0").click()

    for f in mail.find_elements_by_tag_name('iframe'):
        i = f.get_attribute('id')
        if i.endswith('_frameBody'):
            mail.switch_to.frame(i)
            break

    url = mail.find_element_by_partial_link_text("checkMail").get_attribute('href')

    mail.quit()
    driver.get(url)

    driver.find_element_by_name("uname").clear()
    driver.find_element_by_name("uname").send_keys(nick)
    driver.find_element_by_id("userpwd").clear()
    driver.find_element_by_id("userpwd").send_keys("feisuzhu")
    driver.find_element_by_css_selector("input.cjzh").click()

    time.sleep(1)

    driver.quit()


for name, pwd in csv.reader(open(options.list)):
    print name, pwd
    do_reg(name, pwd, name)
