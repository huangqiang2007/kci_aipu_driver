#!/usr/bin/env python3

#-------------------------------------------------------------------------------
# This file is CONFIDENTIAL and any use by you is subject to the terms of the
# agreement between you and Arm China or the terms of the agreement between you
# and the party authorised by Arm China to disclose this file to you.
# The confidential and proprietary information contained in this file may only
# be used by a person authorised under and to the extent permitted by a
# subsisting licensing agreement from Arm China.
#
#        (C) Copyright 2020 Arm Technology (China) Co. Ltd.
#                    All rights reserved.
#
# This entire notice must be reproduced on all copies of this file and copies of
# this file may only be made by a person if such person is permitted to do so
# under the terms of a subsisting license agreement from Arm China.
#
#--------------------------------------------------------------------------------

#
# Note: this file is the main logic for client connection.
#
# - after reset, it sends BEGIN packet to server, server returns feedback
# - after Juno test cases over, it sends test log to server
# - the whole test logic done, it sends END packet to server, server sends
#   last packet which incudes 'reboot' command or not
#
#
import os
import sys
from threading import Timer, Condition, Thread
import socket
import json
import struct
import fcntl
import time
print(os.path.abspath(os.curdir))
sys.path.append(os.path.abspath(os.curdir) + "/kci")
from kci_common import *
from kci_packet import *
from kci_misc import *
from kci_dbg import *

# ip and port in server side
IP, PORT = '10.190.0.120', 19998

def get_ip_address(ip_name):
    sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip_addr = socket.inet_ntoa(fcntl.ioctl(sk.fileno(), 0x8915, \
        struct.pack('256s', ip_name[:15].encode("utf-8")))[20:24])
    LOG_INFO("ip: {}".format(ip_addr))
    return ip_addr

class MessageSender:
    ms_ip = None
    ms_port = 0
    pkt_id = 0
    image_name = ''
    send_pkt_dic = {}
    recv_pkt_dic = {}

    def __init__(self, ip, port):
        try:
            self.ms_ip = ip
            self.ms_port = port
            self.client = socket.socket()
            self.client.connect((self.ms_ip, self.ms_port))
        except Exception:
            LOG_ERR("MessageSender connect({}, {}) [fail]".format(ip, port))
            sys.exit(1)

    # def __init__(self, ParseCmdline_obj):
    #     try:
    #         self.ms_ip = ParseCmdline_obj.IP
    #         self.ms_port = ParseCmdline_obj.PORT
    #         self.client = socket.socket()
    #         self.client.connect((self.ms_ip, self.ms_port))
    #     except Exception:
    #         LOG_ERR("MessageSender connect({}, {}) [fail]".format(ParseCmdline_obj.IP, ParseCmdline_obj.PORT))
    #         sys.exit(1)

    def __del__(self):
        try:
            self.client.close()
        except Exception:
            LOG_ERR("MessageSender close({}, {}) [fail]".format(self.ms_ip, self.ms_port))
            sys.exit(1)

    def handle_begin_pkt(self):
        self.send_pkt_dic.clear()
        self.recv_pkt_dic.clear()

        self.send_pkt_dic['id'] = self.pkt_id
        self.send_pkt_dic['type'] = PT_BEGIN
        self.pkt_id += 1
        self.client.send(str.encode(json.dumps(self.send_pkt_dic)))

        rcv_data = self.client.recv(PKT_LEN_1M)
        self.recv_pkt_dic = eval(rcv_data.decode())
        self.image_name = self.recv_pkt_dic['imageName']
        LOG_INFO("handle_begin_pkt rcv: " + str(self.recv_pkt_dic))

    def handle_end_pkt(self):
        self.send_pkt_dic.clear()
        self.recv_pkt_dic.clear()

        self.send_pkt_dic['id'] = self.pkt_id
        self.send_pkt_dic['type'] = PT_END
        self.send_pkt_dic['imageName'] = self.image_name
        self.pkt_id += 1
        self.client.send(str.encode(json.dumps(self.send_pkt_dic)))

        rcv_data = self.client.recv(PKT_LEN_1M)
        self.recv_pkt_dic = eval(rcv_data.decode())
        LOG_INFO("handle_end_pkt rcv: " + str(self.recv_pkt_dic))
        if self.recv_pkt_dic['reboot'] == 'reboot':
            LOG_ALERT('reboot Juno now')
            os.system('reboot')
        else:
            LOG_ALERT('all images test done on Juno, no reboot')
            sys.exit(0)

    def handle_file_pkt(self, file_path):
        self.send_pkt_dic.clear()
        self.recv_pkt_dic.clear()

        if os.path.exists(file_path) == True:
            fp_file = open(file_path, "r")
        else:
            LOG_ERR(file_path + " not exist")
            sys.exit(1)

        self.send_pkt_dic['id'] = self.pkt_id
        self.send_pkt_dic['type'] = PT_FILE
        self.send_pkt_dic['imageName'] = self.image_name
        self.send_pkt_dic['fileName'] = os.path.basename(file_path)
        file_stat = os.stat(file_path)
        self.send_pkt_dic['fileLen'] = file_stat.st_size
        self.send_pkt_dic['fileData'] = fp_file.read()
        #LOG_INFO('file_data: {}'.format(self.send_pkt_dic['fileData']))
        self.pkt_id += 1
        self.client.send(str.encode(json.dumps(self.send_pkt_dic)))

        rcv_data = self.client.recv(PKT_LEN_1M)
        self.recv_pkt_dic = eval(rcv_data.decode())
        LOG_INFO("handle_file_pkt rcv: " + str(self.recv_pkt_dic))

        fp_file.close()

    def test(self):
        while True:
            id = input('id: > ')
            if id == '0':
                self.handle_begin_pkt()
            elif id == '1':
                self.handle_end_pkt()
            elif id == '2':
                self.handle_file_pkt("./kci_packet.py")
            else:
                break

if __name__ == "__main__":
    try:
        LOG_ALERT("ip: {}, port: {}".format(IP, PORT))
        g_message_sender_obj = MessageSender(IP, PORT)
        g_message_sender_obj.test()
    except Exception:
        LOG_ERR("client.connect(({}, {}))".format(IP, PORT))
        sys.exit(1)
