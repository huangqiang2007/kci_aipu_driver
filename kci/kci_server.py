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
import os
import sys
import queue
import json
import socket
import struct
import re
import fcntl
import getopt
import select
import time
from kci_packet import *
from kci_misc import *
from kci_dbg import *

#
# initial
#
g_rcv_dic = {}
#re_rule = re.compile(r'\{.*?\}+')
g_server = None
g_result_file = './kci_result.txt'
g_ResultData_obj = None
g_genLiuxImage_obj = None


class ResultData:
    result_fp = None

    def __init__(self):
        global g_result_file

        try:
            self.result_fp = open(g_result_file, mode='a+')
            LOG_ALERT('ResultData: open: {}'.format(g_result_file))
        except:
            LOG_ERR('ResultData: open: {}'.format(g_result_file))
            sys.exit(1)

    def __del__(self):
        if self.result_fp:
            self.result_fp.close()

    def store_data(self, data):
        try:
            self.result_fp.write(data)
            self.result_fp.flush()
        except:
            LOG_ERR('store_data')

class GenLiuxImage:
    tftp_dir = './tftp_root'
    tftp_idx = 0
    image_dir = 'images/'
    tftp_cur_image_name = ''
    image_abs_path = ''
    cur_abs_path = ''
    toolchain_path = ''
    kernel_path = ''
    defconfig_abs_path = ''
    defconfig_list = []
    image_list = []

    # record compile log
    resultData_obj = None

    def __init__(self, _toolchain_path, _kernel_path, _defconfig_path, _resultData_obj):
        self.resultData_obj = _resultData_obj

        if os.path.exists(self.image_dir) == True:
            os.system('rm -fr ' + self.image_dir)
        os.mkdir(self.image_dir)
        self.cur_abs_path = os.path.abspath('./')
        self.image_abs_path = self.cur_abs_path + '/' + self.image_dir

        if os.path.exists(_toolchain_path) == True:
            self.toolchain_path = _toolchain_path

            # add toolchain path to system 'PATH'
            env_path = os.getenv('PATH')
            env_path = self.toolchain_path + ":" + env_path
            os.environ['PATH'] = env_path
            # os.system('aarch64-linux-gnu-gcc -v')
        else:
            LOG_ERR('GenLiuxImage __init__: _toolchain_path {} invalid'.format(_toolchain_path))
            sys.exit(1)

        if os.path.exists(_kernel_path) == True:
            self._kernel_path = os.path.abspath(_kernel_path)
            LOG_DBG(self._kernel_path)
        else:
            LOG_ERR('GenLiuxImage __init__: _kernel_path {} invalid'.format(_kernel_path))
            sys.exit(1)

        if os.path.exists(_defconfig_path) == True:
            self.defconfig_abs_path = os.path.abspath(_defconfig_path)
            LOG_DBG(self.defconfig_abs_path)
            self.defconfig_list = os.listdir(_defconfig_path)
            LOG_INFO(self.defconfig_abs_path)
        else:
            LOG_ERR('GenLiuxImage __init__: _defconfig_path {} invalid'.format(_defconfig_path))
            sys.exit(1)

        self.compile_linux()

    def compile_single_linux(self, _defconfig):
        LOG_DBG('compile_single_linux')
        # the commands for compiling Linux kernel
        # CMD1 = 'cd ' + self._kernel_path
        CMD2 = 'make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- clean'
        CMD3 = 'cp ' + _defconfig +  ' ' + self._kernel_path + '/.config'
        CMD4 = 'make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j4'
        # CMD5 = 'cd ' + self.cur_abs_path

        cmd_list = [CMD3, CMD4]

        os.chdir(self._kernel_path)
        for cmd in cmd_list:
            LOG_DBG(cmd)
            ret = os.system(cmd)
            if ret < 0:
                LOG_ERR(cmd)
                return ret

        return 0

    def compile_linux(self):
        LOG_DBG('compile_linux')
        for linux_defconfig in self.defconfig_list:
            os.chdir(self.cur_abs_path)
            ret = self.compile_single_linux(self.defconfig_abs_path + '/' + linux_defconfig)
            if ret < 0:
                LOG_ERR("compile_linux {}".format(linux_defconfig))
                self.resultData_obj.store_data("compile linux: {} [fail]\n".format(linux_defconfig))
                continue
            else:
                self.resultData_obj.store_data("compile linux: {} [ok]\n".format(linux_defconfig))

            CMD = 'cp ' + self._kernel_path + '/arch/arm64/boot/Image' \
                + ' ' + self.image_abs_path + '/' + linux_defconfig + '-Image'

            LOG_INFO(CMD)
            ret = os.system(CMD)
            if ret < 0:
                LOG_ERR(CMD + ' [fail]')

        # store all images to specific List
        self.image_list = os.listdir(self.image_abs_path)
        LOG_ALERT(self.image_list)

    def tftp_loop_one_image(self):
        os.chdir(self.cur_abs_path)
        LOG_DBG('tftp_loop_one_image cur_path: ' + os.path.abspath(self.tftp_dir))
        LOG_DBG('TFTP-idx: {}, len(image_list): {}'.format(self.tftp_idx, len(self.image_list)))
        if self.tftp_idx >= len(self.image_list):
            LOG_ALERT('tftp_loop_one_image loop end')
            self.tftp_cur_image_name = ''
            sys.exit(0)

        while self.tftp_idx < len(self.image_list):
            self.tftp_cur_image_name = self.image_list[self.tftp_idx]
            CMD = 'cp ' + self.image_abs_path + '/' +  self.tftp_cur_image_name \
                + ' ' + os.path.abspath(self.tftp_dir) + '/Image'

            self.tftp_idx += 1
            LOG_DBG(CMD)
            if os.system(CMD) < 0:
                LOG_ERR(CMD + ' [fail]')
                continue
            else:
                break
                # Todo... relay switch control

        # return current test image name
        prompt = 'TFTP Image name: {}'.format(self.tftp_cur_image_name)
        # self.resultData_obj.store_data(prompt + '\n')
        LOG_ALERT(prompt)
        return self.tftp_cur_image_name


#
# MessageParser handle each connection from client
#
class MessageParser:
    resultData_obj = None
    genLiuxImage_obj = None
    send_pkt_dic = {}
    def __init__(self, request, client_address, _resultData_obj, _genLiuxImage_obj):
        self.request = request
        self.client_address = client_address
        self.con = Condition()
        self.message_queue = queue.Queue(20)
        self.resultData_obj = _resultData_obj
        self.genLiuxImage_obj = _genLiuxImage_obj
        LOG_INFO("init MessageParser")

    def common_send(self, send_dic):
        ret = 0
        try:
           self.request.send(str.encode(json.dumps(send_dic)))
        except Exception:
            LOG_ERR('MessageParser common_send id: {}, type: {} [fail]'.format(send_dic['id'], send_dic['type']))
            ret = -1
        return ret

    def handle_begin_pkt(self, rcv_dic):
        self.send_pkt_dic.clear()
        self.send_pkt_dic['id'] = rcv_dic['id']
        self.send_pkt_dic['type'] = PT_BEGIN_ACK
        self.send_pkt_dic['imageName'] = self.genLiuxImage_obj.tftp_cur_image_name
        self.resultData_obj.store_data('\n\nImage Begin: ' + self.send_pkt_dic['imageName'] + '\n')
        return self.common_send(self.send_pkt_dic)


    def handle_end_pkt(self, rcv_dic):
        self.send_pkt_dic.clear()
        self.send_pkt_dic['id'] = rcv_dic['id']
        self.send_pkt_dic['type'] = PT_END_ACK
        # self.resultData_obj.store_data('Image End: ' + rcv_dic['imageName'] + '\n')
        return self.common_send(self.send_pkt_dic)

    def handle_file_pkt(self, rcv_dic):
        self.send_pkt_dic.clear()
        self.send_pkt_dic['id'] = rcv_dic['id']
        self.send_pkt_dic['type'] = PT_FILE_ACK
        file_data = rcv_dic['fileData']
        # LOG_INFO("handle_file_pkt: \n" + file_data)
        self.resultData_obj.store_data(file_data)
        return self.common_send(self.send_pkt_dic)

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

    def loop_images(self, message_parser):
        inputs = [self.request]
        outputs = []
        rcv_dic = {}
        connect_lost = False

        TIMEOUT_1MIN = 60
        TIMEOUT_20MIN = 1200
        timeout = TIMEOUT_1MIN

        while True:
            LOG_ALERT('before select, timeout {}, {}'.format(timeout, connect_lost))
            try:
                readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)
            except:
                LOG_ERR('\n\nloop_images select: timeout')
                connect_lost = True

            if len(readable) == 0:
                LOG_ERR('loop_images select: timeout')
                connect_lost = True
            else:
                for s in readable:
                    data = s.recv(PKT_LEN_1M)
                    if (not data):
                        # LOG_ERR("connection lost")
                        connect_lost = True
                        break
                    rcv_dic = eval(bytes.decode(data))
                    LOG_ALERT(rcv_dic)
                    pkt_type = rcv_dic['type']
                    if pkt_type == PT_BEGIN:
                        if self.handle_begin_pkt(rcv_dic) < 0:
                            connect_lost = True
                            prompt = 'loop_images handle_begin_pkt [fail]'
                            self.resultData_obj.store_data(prompt + '\n')
                            LOG_ERR(prompt)
                            break
                        else:
                            timeout = TIMEOUT_20MIN
                    elif pkt_type == PT_FILE:
                        if self.handle_file_pkt(rcv_dic) < 0:
                            connect_lost = True
                            prompt = 'loop_images handle_file_pkt [fail]'
                            self.resultData_obj.store_data(prompt + '\n')
                            LOG_ERR(prompt)
                            break
                        else:
                            timeout = TIMEOUT_1MIN
                    elif pkt_type == PT_END:
                        if self.handle_end_pkt(rcv_dic) < 0:
                            connect_lost = True
                            prompt = 'loop_images handle_end_pkt [fail]'
                            self.resultData_obj.store_data(prompt + '\n')
                            LOG_ERR(prompt)
                            break
                        else:
                            timeout = TIMEOUT_1MIN
                    else:
                        LOG_ERR("loop_images packet id: {}, type: {} error".format(rcv_dic['id'], rcv_dic['type']))

            if connect_lost == True:
                LOG_ALERT('loop_images exit')
                self.request.close()
                self.genLiuxImage_obj.tftp_loop_one_image()
                break

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
        struct.pack('256s', ip_name[:15].encode("utf-8")))[20:24])
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
                if self.message_parser.genLiuxImage_obj.tftp_cur_image_name == '':
                    break

                time.sleep(10)
                # self.data = self.request.recv(PKT_LEN_1M)
                # LOG_INFO( "{} send: {}".format(self.client_address, self.data))
                # if (not self.data):
                #     LOG_ERR("connection lost")
                #     break

                # try:
                #     rcv_data = bytes.decode(self.data)
                #     g_rcv_dic["request"] = self.request
                #     g_rcv_dic["data"] = rcv_data
                # except:
                #     LOG_ERR("bytes.decode({}), error\n".format(self.data))
                #     continue

                # # put one packet to message queue
                # self.message_parser.con.acquire()
                # self.message_parser.message_queue.put(g_rcv_dic)
                # # LOG_DBG("queue.put {}".format(g_rcv_dic["data"]))
                # self.message_parser.con.notify()
                # self.message_parser.con.release()
        except Exception:
            LOG_ERR("handle exception {}\n".format(self.client_address))
        finally:
            self.request.close()

    def setup(self):
        global g_ResultData_obj
        global g_genLiuxImage_obj
        #
        # create a new message parser object for a fresh connection
        # at the same time, a specific thread being created to handle
        # packets based on this connection.
        #
        self.message_parser = MessageParser(self.request, self.client_address, g_ResultData_obj, g_genLiuxImage_obj)
        # Thread(target = self.message_parser.consum_thread, args = (self.message_parser,)).start()

        Thread(target = self.message_parser.loop_images, args = (self.message_parser,)).start()
        LOG_ALERT("connect setup() {}\n".format(self.client_address))

    def finish(self):
        g_server.close_request(self.request)
        LOG_ALERT("connect finish req {}\n".format(self.client_address))

if __name__ == "__main__":
    if os.path.exists(g_result_file) == True:
        os.system('rm -f {}'.format(g_result_file))
        LOG_ALERT('rm -f {}'.format(g_result_file))

    g_ResultData_obj = ResultData()

    pc_obj = KciParseCmdline(sys.argv[1:])
    p_dbg_init(pc_obj.VERBOSE)

    g_genLiuxImage_obj = GenLiuxImage(pc_obj.toolchain_path, pc_obj.kernel_path, pc_obj.defconfig_path, g_ResultData_obj)
    g_genLiuxImage_obj.tftp_loop_one_image()

    HOST,PORT = pc_obj.IP, pc_obj.PORT
    LOG_ALERT("ip: {}, port: {}".format(HOST, PORT))
    g_server = socketserver.ThreadingTCPServer((HOST, PORT), SockTCPHandler)
    g_server.serve_forever()
