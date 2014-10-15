#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# foscam_scan.py : 25/05/11
# g.revaillot, revaillot@archos.com

import sys, time
from socket import *
from struct import *
import binascii

header = '\x4d\x4f\x5f\x49'  # MO_I
magic_opcode = '\x00\x00'    # opcode = 0
reserve_0 = '\x00'           # always 0
reserve_1 = '\x00\x00\x00\x00\x00\x00\x00\x00' # 8 byte len string
magic_order_len = '\x04\x00\x00\x00' # order len
reserve_3 = '\x04\x00\x00\x00'
order = '\x00\x00\x00\x01'

magicPacket = header + magic_opcode + reserve_0 + reserve_1 + magic_order_len + reserve_3  + order

class FoscamUDPPacket():
    mo_i_magic = "MO_I"
    mo_v_magic = "MO_V"
    mo_o_magic = "MO_O"

    default_magic = mo_i_magic
    default_opcode = 0
    default_res0 = 0
    default_res1 = ""
    default_payload_len = 0
    default_res2 = 0

    header = ''
    payload = ''

    def get_head_len(self):
        return 23

    def rebuild_header(self):
        self.header = pack('<' + '4s h b 8s i i', self.magic, self.opcode, self.res0, self.res1, self.payload_len, self.res2)

    def set_payload(self, payload):
        self.payload = payload
        self.payload_len = len(payload)
        self.rebuild_header()

    def set_opcode(self, opcode):
        self.opcode = opcode
        self.rebuild_header()

    def __init__(self, udpPacket=None):
        if (udpPacket == None):
            print "creating blank packet"
            udpPacket = pack('<' + '4s h b 8s i i', self.default_magic, self.default_opcode, self.default_res0, self.default_res1, self.default_payload_len, self.default_res2)

        self.header = udpPacket[0:self.get_head_len()]
        self.payload = udpPacket[self.get_head_len():]


        try:
            self.magic, self.opcode, self.res0, self.res1, self.payload_len, self.res2 = unpack('<' + '4s h b 8s i i', self.header)
        except Exception as err:
            self.dump();
            print "unpack error ", err
            return;

        if (self.magic != self.mo_i_magic and self.magic != self.mo_v_magic and self.magic != self.mo_o_magic):
            print "wrong magic!"

        if (self.payload_len != len(self.payload)):
            print "msg size inconsistent : ", self.payload_len, " vs hdr:", len(self.payload)

    @classmethod
    def buildPacket(cls, opcode, payload):
        packet=cls();
        packet.set_opcode(opcode)
        packet.set_payload(payload)
        return packet

    def parse(self):
        if (self.opcode == 0):
            self.parse_search_req()
        elif (self.opcode == 1):
            self.parse_search_resp()
        elif (self.opcode == 2):
            self.parse_init_req()
        elif (self.opcode == 3):
            self.parse_init_resp()

    def parse_search_req(self):
        print "search request..."
        pass

    def parse_search_resp(self):
        print "search response..."

        # Camera ID BINARY_STREAM[13]
        # Camera name BINARY_STREAM[21]
        # IP INT32_R
        # mask INT32_R
        # gateway IP INT32_R
        # DNS INT32_R
        # reserve BINARY_STREAM[4]
        # Sys_software version BINARY_STREAM[4] a.b.c.d
        # App_software version BINARY_STREAM[4] a.b.c.d
        # Camera port INT16_R
        # dhcp enabled INT8 0:dhcp disabled;1:dhcp enabled  Note: system software x.x.2.2 and above have this field

        self.dump()

        cam_id, cam_name, \
        ip3,  ip2,  ip1,  ip0, \
        msk3, msk2, msk1, msk0, \
        gw3,  gw2,   gw1,   gw0, \
        dns3, dns2,  dns1,  dns0, \
        reserved, \
        sys_version_a, sys_version_b, sys_version_c, sys_version_d, \
        app_version_a, app_version_b, app_version_c, app_version_d, \
        cam_port, dhcp_enabled \
        = unpack('! 13s 21s BBBB BBBB BBBB BBBB 4s BBBB BBBB h ?', self.payload[:65])

        print "name :%s" % (cam_name)
        print "id   :%s" % (cam_id)
        print "ip   :%s.%s.%s.%s" % (ip3, ip2, ip1, ip0)
        print "mask :%s.%s.%s.%s" % (msk3, msk2, msk1, msk0)
        print "gw   :%s.%s.%s.%s" % (gw3, gw2, gw1, gw0)
        print "dns  :%s.%s.%s.%s" % (dns3, dns2, dns1, dns0)
        print "port :%s" % (cam_port)
        print "sysv :%s.%s.%s.%s" % (sys_version_a, sys_version_b, sys_version_c, sys_version_d)
        print "appv :%s.%s.%s.%s" % (app_version_a, app_version_b, app_version_c, app_version_d)
        print "dhcp :%s" % (dhcp_enabled)

    def parse_init_req(self):
        print "init request..."
        pass

    def parse_init_resp(self):
        print "init response..."
        pass

    def get_packet(self):
        return self.header + self.payload

    def dump(self):
        print "hdr         :", binascii.hexlify(self.header)
        print "payload len :", len(self.payload)
        print "payload     :", binascii.hexlify(self.payload)

s = socket(AF_INET, SOCK_DGRAM)
s.bind(('', 10000))
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

discover_req_packet = FoscamUDPPacket.buildPacket(opcode=0, payload='\x00\x00\x00\x01')

while 1:
    s.sendto(discover_req_packet.get_packet(), ('<broadcast>', 10000))

    (data, addr) = s.recvfrom(1024)

    FoscamUDPPacket(udpPacket=data).parse()

    print "-------------------------------------------------------------------"

    time.sleep(1);

