#!/usr/bin/python 
# -*- coding: utf-8 -*-
#
# foscam_scan.py : 25/05/11
# g.revaillot, revaillot@archos.com

import sys, time
from socket import *
from struct import *

magic = '\x4d\x4f\x5f\x49\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x01'

s = socket(AF_INET, SOCK_DGRAM)
s.bind(('', 10000))
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

while 1:
    s.sendto(magic, ('<broadcast>', 10000))
    (data, addr) = s.recvfrom(1024)
    if len(data) == 88:

        msgtype, pad1, \
        id, name, \
        ip3,  ip2,  ip1,  ip0, \
        msk3, msk2, msk1, msk0, \
        gw3,  gw2,   gw1,   gw0, \
        dns3, dns2,  dns1,  dns0, \
        pad2, \
        = unpack('<' + '15s 8s 12s 22s' + 'BBBB BBBB BBBB BBBB' +'15s', data)

        print " ipcam found @ %s" % (addr[0])
        print "name :%s" % (name)
        print "id   :%s" % (id)
        print "ip   :%s.%s.%s.%s" % (ip3, ip2, ip1, ip0)
        print "mask :%s.%s.%s.%s" % (msk3, msk2, msk1, msk0)
        print "gw   :%s.%s.%s.%s" % (gw3, gw2, gw1, gw0)
        print "dns  :%s.%s.%s.%s" % (dns3, dns2, dns1, dns0)

        print ""
        print "pad1 :",

        for char in pad1:
            print hex(ord(char)),
        print ""

        print "pad2 :",
        for char in pad2:
            print hex(ord(char)),
        print ""

        print ""

    time.sleep(1);
