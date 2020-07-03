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
from misc import *
from dbg import *

#
# initial
#
j_dic = {}
re_rule = re.compile(r'\{.*?\}+')
g_server = None

#
# MessageParser handle each connection from client
#
class MessageParser:
    def __init__(self, request, client_address):
        self.request = request
        self.client_address = client_address
        self.con = Condition()
        self.message_queue = queue.Queue(20)
        LOG_INFO("init MessageParser")

    #
    # fetch each message from queue and parse it
    #
    def consume_queue(self):
        LOG_DBG("consume_queue(): {}".format(self.client_address))

        #
        # the below logic is for handling such case:
        # more than one message packets are included in single one network packet.
        # we have to iterate each message packet and parse them.
        #
        q_str = self.message_queue.get()
        try:
            request_str = q_str["request"]
            packets_str = q_str["data"]
            #re_match_packets = re.findall('\{.*?\}+', packets_str, re.M|re.I)
            #re_match_packets = re_rule.findall(packets_str)
            LOG_DBG(request_str)
            LOG_DBG(packets_str)
            self.request.sendall(str.encode(json.dumps(packets_str)))
        except Exception:
            LOG_ERR("g_server.send: {}".format(packets_str))
            sys.exit(1)

#
# one specific thread for consuming message queue
# @message_parser: MessageParser object
#
def consum_thread(message_parser):
    LOG_DBG("consum_thread(): {}".format(message_parser.client_address))
    while(True):
        if(message_parser.message_queue.qsize() == 0):
            LOG_INFO( "consumer waiting ...\n")
            message_parser.con.acquire()
            message_parser.con.wait()
            message_parser.con.release()
            LOG_INFO( "consumer run again ...\n")
        else:
            try:
                message_parser.consume_queue()
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
    LOG_INFO("get_ip_address " + ip_addr)
    return ip_addr

#
# Socket server handler class needed by socketserver
#
class SockTCPHandler(socketserver.BaseRequestHandler):
    message_parser = None

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

                self.message_parser.con.acquire()
                self.message_parser.message_queue.put(j_dic)
                LOG_DBG("queue.put {}".format(j_dic["data"]))
                self.message_parser.con.notify()
                self.message_parser.con.release()
        except Exception:
            LOG_ERR("{}, {}".format(self.client_address, "exception error"))
        finally:
            self.request.close()

    def setup(self):
        #
        # create a new message parser object for a fresh connection
        # at the same time, a specific thread being created to handle
        # packets based on this connection.
        #
        self.message_parser = MessageParser(self.request, self.client_address)
        Thread(target = consum_thread, args = (self.message_parser,)).start()
        LOG_ALERT("connect setup() {}\n".format(self.client_address))

    def finish(self):
        g_server.close_request(self.request)
        LOG_ALERT("connect finish req {}\n".format(self.client_address))

if __name__ == "__main__":
    pc_obj = ParseCmdline()
    pc_obj.parse_cmdline_server(sys.argv[1:])
    p_dbg_init(pc_obj.VERBOSE)

    HOST,PORT = pc_obj.IP, pc_obj.PORT
    LOG_ALERT("ip: {}, port: {}".format(HOST, PORT))
    g_server = socketserver.ThreadingTCPServer((HOST, PORT), SockTCPHandler)
    g_server.serve_forever()
