#!/usr/bin/env python3
#
# File name: sockets.py
# Author: huangq@moxigroup.com
#
# Note: this file is the main logic for server, it
# wait and receive packets coming from client(UI level).
# then it's responsible for parsing packets and handle them.
#
#
#
from threading import Timer, Condition, Thread
import socketserver
import sys
import queue
import json
import socket
import struct
import re
import fcntl
import getopt
from dbg import *

#
# initial
#
j_dic = {}
con = Condition()
message_queue = queue.Queue(20)
re_rule = re.compile(r'\{.*?\}+')
g_server = None


#
# fetch each message from queue and parse it
#
def consume_queue():
    global message_parser
    global message_queue
    LOG_DBG("consume_queue()\n")

    #
    # the below logic is for handling such case:
    # more than one message packets are included in single one network packet.
    # we have to iterate each message packet and parse them.
    #
    q_str = message_queue.get()
    try:
        request = q_str["request"]
        packets_str = q_str["data"]
        #re_match_packets = re.findall('\{.*?\}+', packets_str, re.M|re.I)
        #re_match_packets = re_rule.findall(packets_str)
    except:
        LOG_ERR("re.findall() error\npacket_str: {}".format(packets_str))
        return

    for i in range(len(re_match_packets)):
        message_dic = json.loads(re_match_packets[i])
        LOG_DBG("re: {}".format(re_match_packets[i]))

#
# one specific thread for consuming message queue
# @con: Condition variable
#
def consum_thread(con):
    LOG_DBG("consum_thread()")
    while(True):
        if(message_queue.qsize() == 0):
            LOG_INFO( "consumer waiting ...\n")
            con.acquire()
            con.wait()
            con.release()
            LOG_INFO( "consumer run again ...\n")
        else:
            try:
                consume_queue()
            except:
                LOG_ERR("consume_queue() fail\n")

#
# get host IP
# @ip_name: eth0
#
def get_ip_address(ip_name):
    sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip_addr = socket.inet_ntoa(fcntl.ioctl(sk.fileno(), 0x8915, \
        struct.pack('256s', ip_name[:15]))[20:24])
    LOG_INFO("get_ip_address " + ip_addr);
    return ip_addr

def set_TCPserver(server):
    global g_server
    g_server = server

def get_TCPserver():
    global g_server
    if (g_server):
        return g_server
    else:
        LOG_ERR("get_TCPserver g_server is NULL\n")
        return Null

#
# a socket server handler class needed by socketserver
#
class SockTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        try:
            while (True):
                self.data = self.request.recv(1024)
                LOG_INFO( "{} send: {}\n".format(self.client_address, self.data))
                if (not self.data):
                    LOG_ERR("connection lost")
                    break

                try:
                    rcv_data = bytes.decode(self.data)
                    j_dic["request"] = self.request
                    j_dic["data"] = rcv_data
                except:
                    LOG_ERR("bytes.decode({}), error\n".format(self.data))
                    continue

                con.acquire()
                message_queue.put(j_dic)
                LOG_DBG("queue.put {}".format(j_dic["data"]))
                con.notify()
                con.release()
        except Exception:
            LOG_ERR("{}, {}".format(self.client_address, "exception error"))
        finally:
            self.request.close()

    def setup(self):
        p_dbg(DBG_ALERT, "connect setup() {}\n".format(self.client_address))

    def finish(self):
        server = get_TCPserver()
        server.close_request(self.request)
        p_dbg(DBG_ALERT, "connect finish req {}\n".format(self.client_address))

class ParseCmdline:
    def __init__(self, _argv):
        self.IP = ''
        self.VERBOSE = False
        print(_argv)
        self.parse_cmdline_args(_argv)

    def help(self):
        print('help:')
        print('kci_server.py -p ip, -h]')
        print(' -p: ip_address')
        print(' -v: verbose')
        print('	-h: help')
        sys.exit(0)

    def parse_cmdline_args(self, _argv):
        '''
        parse command line arguments
        '''
        try:
            opts, args = getopt.getopt(_argv, "hp:v:", ["loop=","dbg_lvl="])
        except getopt.GetoptError:
            LOG_ERR('kci_server.py cmdline args invalid ' + args)
            sys.exit(1)
        print(args)
        for opt, arg in opts:
            print(opt)
            if opt == '-h':
                self.help()
            elif opt == '-p':
                self.IP = arg
                LOG_DBG("ip: " + self.IP)
            elif opt == '-v':
                if arg == 'True':
                    self.VERBOSE = True
                elif arg == 'False':
                    self.VERBOSE = False
                LOG_DBG("verbose: " + str(self.VERBOSE))

        if self.VERBOSE not in (True, False):
            LOG_ERR(self.VERBOSE + " is invalid")
            sys.exit(1)

if __name__ == "__main__":
    pc_obj = ParseCmdline(sys.argv[1:])
    if pc_obj.IP == '':
        print("ip is null")
        sys.exit(1)

    p_dbg_init(pc_obj.VERBOSE)

    # ip = get_ip_address(str.encode("lo"))
    HOST,PORT = pc_obj.IP,9998
    LOG_ALERT("ip: {}, port: {}\n".format(HOST, PORT))
    Thread(target = consum_thread, args = (con,)).start()
    server = socketserver.ThreadingTCPServer((HOST, PORT), SockTCPHandler)
    set_TCPserver(server)
    server.serve_forever()
