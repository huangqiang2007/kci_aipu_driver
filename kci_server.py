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
		return null

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
		except Exception as e:
			LOG_ERR("{}, {}".format(self.client_address, "exception error"))
		finally:
			self.request.close()

	def setup(self):
		p_dbg(DBG_ALERT, "connect setup() {}\n".format(self.client_address))

	def finish(self):
		server = get_TCPserver()
		server.close_request(self.request)
		p_dbg(DBG_ALERT, "connect finish req {}\n".format(self.client_address))

if __name__ == "__main__":
	verbose = False
	if (len(sys.argv) == 2):
		print(len(sys.argv), sys.argv[1])
		if (sys.argv[1] == "True"):
			verbose = True # output log to stdout for debugging quickly
		else:
			verbose = False # output log to file for debug daemon service
	else:
		LOG_INFO("argv[1] = True: output log to stdout\nargv[1] = False: output log to file")

	p_dbg_init(verbose)

	ip = get_ip_address(str.encode("lo"))
	HOST,PORT = ip,9998
	LOG_ALERT("ip: {}, port: {}\n".format(HOST, PORT))
	Thread(target = consum_thread, args = (con,)).start()
	server = socketserver.ThreadingTCPServer((HOST, PORT), SockTCPHandler)
	set_TCPserver(server)
	server.serve_forever()
