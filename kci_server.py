#!/usr/bin/env python3
#
# File name: kci_server.py
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
from kci_packet import *
from misc import *
from dbg import *

#
# initial
#
g_rcv_dic = {}
#re_rule = re.compile(r'\{.*?\}+')
g_server = None

#
# MessageParser handle each connection from client
#
class MessageParser:
    send_pkt_dic = {}
    def __init__(self, request, client_address):
        self.request = request
        self.client_address = client_address
        self.con = Condition()
        self.message_queue = queue.Queue(20)
        LOG_INFO("init MessageParser")

    def common_send(self, send_dic):
        try:
           self.request.send(str.encode(json.dumps(send_dic)))
        except Exception:
            LOG_ERR('MessageParser common_send id: {}, type: {} [fail]'.format(send_dic['id'], send_dic['type']))

    def handle_begin_pkt(self, rcv_dic):
        self.send_pkt_dic.clear()
        self.send_pkt_dic['id'] = rcv_dic['id']
        self.send_pkt_dic['type'] = PT_BEGIN_ACK
        self.send_pkt_dic['imageName'] = 'Image_01'
        self.common_send(self.send_pkt_dic)

    def handle_end_pkt(self, rcv_dic):
        self.send_pkt_dic.clear()
        self.send_pkt_dic['id'] = rcv_dic['id']
        self.send_pkt_dic['type'] = PT_END_ACK
        self.common_send(self.send_pkt_dic)

    def handle_file_pkt(self, rcv_dic):
        self.send_pkt_dic.clear()
        self.send_pkt_dic['id'] = rcv_dic['id']
        self.send_pkt_dic['type'] = PT_FILE_ACK
        file_data = rcv_dic['fileData']
        LOG_INFO("handle_file_pkt: \n" + file_data)
        self.common_send(self.send_pkt_dic)

    def handle_rcv_msg(self, rcv_dic):
        pkt_type = rcv_dic['type']
        if pkt_type == PT_BEGIN:
            self.handle_begin_pkt(rcv_dic)
        elif pkt_type == PT_END:
            self.handle_end_pkt(rcv_dic)
        elif pkt_type == PT_FILE:
            self.handle_file_pkt(rcv_dic)
        else:
            LOG_ERR("handle_rcv_msg packet id: {}, type: {} error".format(rcv_dic['id'], rcv_dic['type']))

    #
    # fetch each message from queue and parse it
    #
    def consume_queue(self):
        LOG_DBG("consume_queue(): {}".format(self.client_address))

        # fetch packet form message queue
        q_str = self.message_queue.get()
        try:
            packets_str = q_str["data"]
            # # LOG_DBG("rcv: " + packets_str.decode())
            packets_dic = eval(packets_str)
            LOG_INFO(packets_dic)
            self.handle_rcv_msg(packets_dic)
        except Exception:
            LOG_ERR("g_server.send: {}".format(packets_str))
            sys.exit(1)

    #
    # one specific thread for consuming message queue
    # @message_parser: MessageParser object
    #
    def consum_thread(self, message_parser):
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
                self.data = self.request.recv(PKT_LEN_1M)
                LOG_INFO( "{} send: {}".format(self.client_address, self.data))
                if (not self.data):
                    LOG_ERR("connection lost")
                    break

                try:
                    rcv_data = bytes.decode(self.data)
                    g_rcv_dic["request"] = self.request
                    g_rcv_dic["data"] = rcv_data
                except:
                    LOG_ERR("bytes.decode({}), error\n".format(self.data))
                    continue

                # put one packet to message queue
                self.message_parser.con.acquire()
                self.message_parser.message_queue.put(g_rcv_dic)
                # LOG_DBG("queue.put {}".format(g_rcv_dic["data"]))
                self.message_parser.con.notify()
                self.message_parser.con.release()
        except Exception:
            LOG_ERR("handle exception {}\n".format(self.client_address))
        finally:
            self.request.close()

    def setup(self):
        #
        # create a new message parser object for a fresh connection
        # at the same time, a specific thread being created to handle
        # packets based on this connection.
        #
        self.message_parser = MessageParser(self.request, self.client_address)
        Thread(target = self.message_parser.consum_thread, args = (self.message_parser,)).start()
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
