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

j_dic = {}

hum_tem_dic = {}

client = socket.socket()

def get_ip_address(ip_name):
    sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip_addr = socket.inet_ntoa(fcntl.ioctl(sk.fileno(), 0x8915, \
        struct.pack('256s', ip_name[:15]))[20:24])
    LOG_INFO("ip: {}".format(ip_addr))
    return ip_addr

class Test_cls:
    def __init__(self):
        pass

    def get_hum_tem(self):
        hid = input("humidify\nid: ")
        hopcode = input("opcode: ")
        hum_tem_dic["id"] = int(hid)
        hum_tem_dic["opcode"] = int(hopcode)
        client.send(str.encode(json.dumps(hum_tem_dic)))

    def recv_thread(self, client):
        LOG_INFO("recv_thread()\n")
        while (True):
            dic_res = client.recv(1024)
            LOG_INFO("\nrcv: " + dic_res.decode() + "\n")

    def test(self):
        rcv_thrd = Thread(target = self.recv_thread, args = (client,))
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

        client.close()

if __name__ == "__main__":
    pc_obj = ParseCmdline()
    pc_obj.parse_cmdline_server(sys.argv[1:])

    try:
        HOST,PORT = pc_obj.IP, pc_obj.PORT
        LOG_ALERT("ip: {}, port: {}\n".format(HOST, PORT))
        client.connect((pc_obj.IP, 9998))
    except Exception:
        LOG_ERR("client.connect(({}, {}))".format(pc_obj.IP, pc_obj.PORT))
        sys.exit(1)

    test_obj = Test_cls()
    test_obj.test()