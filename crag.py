#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# by: pantuts
# Dependencies: gevent, BeautifulSoup4, python2.7
# This is a PoC only

import gevent
from gevent import monkey
monkey.patch_all()

import socket
socket.setdefaulttimeout(120)

from bs4 import BeautifulSoup
import random
import sys
import time

from check_proxy import check_proxy
import user_agents

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException

# to be used by thread to determine if flagging is successful
FLAGGED = 0
# variable for unsuccessful retries. max is 20
PROXY_RETRIES = 0


def usage():
    print 'python2.7 crag.py links.txt proxies.txt'


def requestor(num, url, proxy):
    global FLAGGED
    global PROXY_RETRIES

    print '[+] ' + str(num) + '\t' + url
    proxy = proxy

    try:
        desired_capabilities = dict(DesiredCapabilities.PHANTOMJS)
        desired_capabilities["phantomjs.page.settings.userAgent"] = (user_agents.set_agent())
        desired_capabilities['phantomjs.page.settings.webStorageEnabled'] = True
        desired_capabilities['phantomjs.page.settings.browserConnectionEnabled'] = True
        desired_capabilities['phantomjs.page.settings.locationContextEnabled'] = True
        desired_capabilities['phantomjs.page.settings.applicationCacheEnabled'] = True

        service_args = [
            '--load-images=no',
            '--proxy=' + proxy,
            '--proxy-type=http'
        ]

        driver = webdriver.PhantomJS(service_args=service_args, desired_capabilities=desired_capabilities)
        driver.get(url)
        # debugging
        # print driver.execute_script("return navigator.userAgent;")

        elem = driver.find_element(By.CSS_SELECTOR, '.flaglink')
        elem.click()
        source = (driver.page_source).encode('utf-8')
        driver.quit()

        soup = BeautifulSoup(source, 'html.parser')
        if soup.select('.flaglink .active'):
            print '[+] ' + str(num) + ' >> needs more flagging...'
        time.sleep(random.choice([3,4,5,6]))

    except NoSuchElementException:
        print '[' + str(num) + ']' + url + ': successfully flagged at ' + proxy
        FLAGGED = 1
        pass
    except Exception as e:
        print '[-] Error encountered / timeout / urlerror'
        PROXY_RETRIES = PROXY_RETRIES + 1
        pass


def set_proxy(proxy_list):
    proxy = random.choice(proxy_list)
    return str(proxy) if proxy else None


if __name__=='__main__':
    if len(sys.argv) < 3:
        usage()
        sys.exit(1)

    proxy_list = []
    proxy_file = sys.argv[2]
    urls_file = sys.argv[1]

    with open(proxy_file) as pf:
        proxy_list = pf.read().splitlines()
        proxy_list = filter(None, proxy_list)
    with open(urls_file) as uf:
        urls = uf.read().splitlines()
        urls = filter(None, urls)

    # loop URLs
    for num, url in enumerate(urls):
        FLAGGED = 0
        PROXY_RETRIES = 0

        # get working proxy from list
        proxy_check = False
        proxy = ''

        def use_proxy():
            global proxy_list
            global proxy_check
            global proxy

            while proxy_check != True:
                proxy = set_proxy(proxy_list)
                print 'Checking proxy >> ' + proxy
                proxy_good = check_proxy(proxy)
                proxy_check = True if proxy_good else proxy_list.remove(proxy)

                if not proxy_list:
                    print "You don't have a working proxy."
                    sys.exit(0)
        use_proxy()

        # while the url is still not flagged, continue clicking prohibit link
        while FLAGGED != 1:
            print
            print 'Using >> ' + proxy
            print
            print '------------------------------------'
            print '--------------FLAGGING--------------'
            print

            # you can change range(5) to any number, but the default shall do
            threads = []
            for i in range(5):
                threads.append(gevent.spawn(requestor, i + 1, url, proxy))
                if (i + 1) % 5 == 0:
                    gevent.joinall(threads)
                else:
                    continue
            gevent.joinall(threads)

            # unsuccessful retries reached
            if PROXY_RETRIES == 20:
                print
                print 'Changing proxy...'
                use_proxy()
        print
        print '--------------END FLAGGING--------------'
        print '----------------------------------------'
        print
