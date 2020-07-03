#!/usr/bin/env python3
#
# File name: socketc.py
# Author: huangq@moxigroup.com
#
# Note: this file is the main logic for client connection, it
# acts as an GUI input interface. Then it's responsible for
# pasing packets to server side.
#
#
from threading import Timer, Condition, Thread
import socket
import json
import struct
import fcntl
import time
from misc import *
from dbg import *

g_test = True

def get_ip_address(ip_name):
    sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip_addr = socket.inet_ntoa(fcntl.ioctl(sk.fileno(), 0x8915, \
        struct.pack('256s', ip_name[:15]))[20:24])
    LOG_INFO("ip: {}".format(ip_addr))
    return ip_addr

class Test_cls:
    j_dic = {}
    hum_tem_dic = {}
    def __init__(self, ParseCmdline_obj):
        self.client = socket.socket()
        self.client.connect((ParseCmdline_obj.IP, ParseCmdline_obj.PORT))

    def get_hum_tem(self):
        hid = input("humidify\nid: ")
        hopcode = input("opcode: ")
        self.hum_tem_dic["id"] = int(hid)
        self.hum_tem_dic["opcode"] = int(hopcode)
        self.client.send(str.encode(json.dumps(self.hum_tem_dic)))

    def recv_thread(self, client):
        LOG_INFO("recv_thread()\n")
        while (True):
            dic_res = client.recv(1024)
            LOG_INFO("\nrcv: " + dic_res.decode() + "\n")

    def test(self):
        rcv_thrd = Thread(target = self.recv_thread, args = (self.client,))
        rcv_thrd.setDaemon(True)
        rcv_thrd.start()
        while True:
            jid = input("1. humidify\nwhich one? > ")
            if (jid < '0' or jid > '1'):
                continue

            i_id = int(jid)
            if (i_id == 0):
                break

            if (i_id == 1):
                self.get_hum_tem()
            else:
                LOG_INFO("no item {}\n".format(i_id))
                break

        self.client.close()

class MessageSender:
    def __init__(self, ParseCmdline_obj):
        try:
            self.client = socket.socket()
            self.client.connect((ParseCmdline_obj.IP, ParseCmdline_obj.PORT))
        except Exception:
            LOG_ERR("MessageSender connect({}, {}) [fail]".format(ParseCmdline_obj.IP, ParseCmdline_obj.PORT))
            sys.exit(1)

    def handle_begin_pkt(self):
        pass

    def handle_end_pkt(self):
        pass

    def handle_file_pkt(self):
        pass

if __name__ == "__main__":
    pc_obj = ParseCmdline()
    pc_obj.parse_cmdline_server(sys.argv[1:])

    try:
        HOST,PORT = pc_obj.IP, pc_obj.PORT
        LOG_ALERT("ip: {}, port: {}".format(HOST, PORT))
        if g_test == True:
            test_obj = Test_cls(pc_obj)
            test_obj.test()
        else:
            message_sender_obj = MessageSender(pc_obj)
    except Exception:
        LOG_ERR("client.connect(({}, {}))".format(pc_obj.IP, pc_obj.PORT))
        sys.exit(1)

