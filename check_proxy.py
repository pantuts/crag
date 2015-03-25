#!/usr/bin/python2.7

import urllib2
import socket
socket.setdefaulttimeout(20)

import sys
sys.dont_write_bytecode = True


def check_proxy(proxy):
    try:
        proxy_handler = urllib2.ProxyHandler({'http': proxy})
        opener = urllib2.build_opener(proxy_handler)
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; Acoo Browser 1.98.744; .NET CLR 3.5.30729)')]
        urllib2.install_opener(opener)
        req = urllib2.Request('http://www.ip-adress.com') # change to url that don't block scrapers
        sock = urllib2.urlopen(req)
        return True
    except urllib2.HTTPError:
        return False
    except Exception:
        return False
