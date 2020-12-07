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
#
# Note: this file is the main logic for server, it
# wait and receive packets coming from client(Juno).
# then it's responsible for parsing packets and handle them.
#
# - compile Linux kernel and generate Image according to different defconfig
# - loop Images one by one via TFTP
# - wait BEGIN packet from Juno
# - wait AIPU test result from Juno
# - wait END packet form Juno
# - decide to send 'reboot' command to Juno
# - exit or loop next Image again
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

# container for received packets
g_rcv_dic = {}

# TCP socket server
g_server = None

# log file for the whole test
g_result_file = './kci_result.txt'

# ResultData object
g_ResultData_obj = None

# GenLinuxImage object
g_genLiuxImage_obj = None


# Class: wrapper for storing all test log
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

# Class: hanle Linux Image generation for different kernel config
class GenLiuxImage:
    # the collection for all information
    #
    # define for genLinuxImage_dic
    # struct genLinuxImage_dic {
    #     'kci_top_dir':
    #     'kci_toolchain_dir':
    #     'kci_board':
    #     'kci_linux_list': ['linux-1', 'linux-2']
    #     'kci_runtime_dir':
    #     'kci_tftp_dir':
    #     'kci_compile': (True, False)
    #     'kci_linux_list'[0]: {
    #         'linux_path':
    #         'linux_images':
    #         'linux_defconfig_path':
    #         'linux_defconfig_list':
    #     }
    #     'kci_linux_list'[1]: {
    #         'linux_path':
    #         'linux_images':
    #         'linux_defconfig_path':
    #         'linux_defconfig_list':
    #     }
    #     'kci_gen_images_list':[['linux-def1', 'linux-def1_image_path'], [], []...]
    # }
    genLinuxImage_dic = {}

    # the index for genLinuxImage_dic['kci_gen_images_list']
    tftp_idx = 0

    # linux version name
    linux_version = ''

    # linux defconfig file name
    linux_config = ''

    # object for recording compile log
    resultData_obj = None

    def __init__(self, _toolchain_path, _platform, _linux_version,\
        _linux_config, _runtime_path, _tftp_dir, _compileLinux, _resultData_obj):
        curcwd = os.path.abspath(".")
        self.genLinuxImage_dic['kci_gen_images_list'] = []
        self.genLinuxImage_dic['kci_toolchain_dir'] = os.path.abspath(_toolchain_path)
        self.genLinuxImage_dic['kci_board'] = _platform
        self.genLinuxImage_dic['kci_top_dir'] = curcwd
        LOG_DBG(self.genLinuxImage_dic['kci_top_dir'])
        self.genLinuxImage_dic['kci_runtime_dir'] = os.path.abspath(_runtime_path)
        self.genLinuxImage_dic['kci_tftp_dir'] = os.path.abspath(_tftp_dir)
        self.genLinuxImage_dic['kci_compile'] = _compileLinux

        self.linux_version = _linux_version
        self.linux_config = _linux_config
        self.resultData_obj = _resultData_obj

        self.genLinuxImage_dic['kci_linux_list'] = os.listdir(curcwd + "/" + _platform)
        LOG_DBG(self.genLinuxImage_dic['kci_linux_list'])

        for linux_version in self.genLinuxImage_dic['kci_linux_list']:
            linux_base_path = curcwd + '/' + _platform + '/' + linux_version
            LOG_DBG(linux_base_path)
            self.genLinuxImage_dic[linux_version] = {}
            self.genLinuxImage_dic[linux_version]['linux_path'] = \
                linux_base_path + '/' + linux_version
            self.genLinuxImage_dic[linux_version]['linux_images'] = linux_base_path + '/images'
            self.genLinuxImage_dic[linux_version]['linux_defconfig_path'] = \
                linux_base_path + '/linux_defconfig'
            self.genLinuxImage_dic[linux_version]['linux_defconfig_list'] = \
                os.listdir(self.genLinuxImage_dic[linux_version]['linux_defconfig_path'])
            LOG_DBG(self.genLinuxImage_dic[linux_version]['linux_path'])
            LOG_DBG(self.genLinuxImage_dic[linux_version]['linux_images'])
            LOG_DBG(self.genLinuxImage_dic[linux_version]['linux_defconfig_list'])

            if(os.system('mkdir -p ' + self.genLinuxImage_dic[linux_version]['linux_images']) < 0):
                LOG_ERR('mkdir -p ' + self.genLinuxImage_dic[linux_version]['linux_images'] + ' [failed]')
                sys.exit(1)

            if self.genLinuxImage_dic['kci_compile'] == True:
                if(os.system('rm -fr ' + self.genLinuxImage_dic[linux_version]['linux_images'] + '/*') < 0):
                    LOG_ERR('rm -fr ' + self.genLinuxImage_dic[linux_version]['linux_images'] + '/*' + ' [failed]')
                    sys.exit(1)

            # add toolchain path to system PATH
            env_path = os.getenv('PATH')
            os.environ['PATH'] = self.genLinuxImage_dic['kci_toolchain_dir'] + ':' + env_path
            LOG_INFO(os.getenv('PATH'))

        self.compile_linux()

    #
    # compile Linux kernel according to some one defconfig
    # @_linux_version: linux version name
    # @_linux_defconfig: linux kernel defconfig name
    #
    def compile_single_linux(self, _linux_version, _linux_defconfig):
        LOG_DBG('compile_single_linux')
        LOG_DBG(self.genLinuxImage_dic[_linux_version]['linux_defconfig_path'])
        linux_path = self.genLinuxImage_dic[_linux_version]['linux_path']
        linux_defconfig = self.genLinuxImage_dic[_linux_version]['linux_defconfig_path'] \
            + '/' + _linux_defconfig

        # the commands for compiling Linux kernel
        # CMD1 = 'cd ' + self._kernel_path
        CMD2 = 'make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- clean'
        CMD3 = 'cp ' + linux_defconfig +  ' ' + linux_path + '/.config'
        CMD4 = 'make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j4'
        cmd_list = [CMD2, CMD3, CMD4]

        # change work directory to kernel source directory
        os.chdir(linux_path)
        for cmd in cmd_list:
            LOG_DBG(cmd)
            ret = os.system(cmd)
            if ret < 0:
                LOG_ERR('compile_single_linux ' + cmd)
                return ret

        return 0

    # loop all defconfig and generate Image for every defconfig
    def compile_linux(self):
        LOG_DBG('compile_linux')

        tmp_runtime_path = ''

        for linux_version in self.genLinuxImage_dic['kci_linux_list']:
            for linux_defconfig in self.genLinuxImage_dic[linux_version]['linux_defconfig_list']:
                os.chdir(self.genLinuxImage_dic["kci_top_dir"])
                LOG_DBG('def: ' + linux_defconfig)

                # filter image by linux version name
                # only test specified linux version
                if self.linux_version == '':
                    pass
                elif self.linux_version != linux_version:
                    continue

                # filter image by linux defconfig name
                # only test specified defconfig belong to specified linux version
                if self.linux_config == '':
                    pass
                elif self.linux_config != linux_defconfig:
                    continue

                # whether it needs to recompile linux and runtime
                if self.genLinuxImage_dic["kci_compile"] == True:
                    # 1. compile Linux
                    ret = self.compile_single_linux(linux_version, linux_defconfig)
                    if ret < 0:
                        LOG_ERR("compile_linux {}".format(linux_defconfig))
                        self.resultData_obj.store_data("compile linux: {} [fail]\n".format(linux_defconfig))
                        continue
                    else:
                        self.resultData_obj.store_data("compile linux: {} [ok]\n".format(linux_defconfig))

                    # 2. compile KMD and UMD
                    tmp_runtime_path = self.genLinuxImage_dic["kci_runtime_dir"] \
                        + '/AIPU_runtime_validation/linux/api_use_scene_test/'
                    os.chdir(tmp_runtime_path)

                    if self.genLinuxImage_dic['kci_board'] == 'juno':
                        CMD1 = './build_all.sh juno-linux-4.9 ' + \
                            self.genLinuxImage_dic[linux_version]['linux_path'] + ' ' + \
                            self.genLinuxImage_dic['kci_toolchain_dir']
                    else:
                        CMD1 = './build_all.sh 6cg-linux-4.14 ' + \
                            self.genLinuxImage_dic[linux_version]['linux_path'] + ' ' + \
                            self.genLinuxImage_dic['kci_toolchain_dir']

                    CMD2 = 'tar czf build.tgz build'
                    cmd_list = [CMD1, CMD2]

                    for cmd in cmd_list:
                        LOG_INFO(cmd)
                        ret = os.system(cmd)
                        if ret < 0:
                            LOG_ERR(cmd + ' [fail]')
                            continue

                # 3. copy Linux Image&dtb and Runtime library to destination
                tmp_image_path = self.genLinuxImage_dic[linux_version]['linux_images'] \
                    + '/' + linux_defconfig

                if self.genLinuxImage_dic["kci_compile"] == True:
                    # change dir to current path
                    os.chdir(self.genLinuxImage_dic['kci_top_dir'])

                    cmd = 'mkdir -p ' + tmp_image_path
                    ret = os.system(cmd)
                    if ret < 0:
                        LOG_ERR(cmd + ' [fail]')
                        sys.exit(1)

                    CMD0 = 'cp ' + self.genLinuxImage_dic[linux_version]['linux_path'] \
                        + '/arch/arm64/boot/dts/arm/juno-r2.dtb' + ' ' + tmp_image_path
                    CMD1 = 'cp ' + self.genLinuxImage_dic[linux_version]['linux_path'] \
                        + '/arch/arm64/boot/Image' + ' ' + tmp_image_path
                    CMD2 = 'cp ' + tmp_runtime_path + '/build.tgz' + ' ' + tmp_image_path
                    cmd_list = [CMD0, CMD1, CMD2]

                    for cmd in cmd_list:
                        LOG_INFO(cmd)
                        ret = os.system(cmd)
                        if ret < 0:
                            LOG_ERR(cmd + ' [fail]')
                            os.system('rm -fr ' + tmp_image_path)
                            continue

                temp_gen_image_list = []
                temp_gen_image_list.append(linux_defconfig)
                temp_gen_image_list.append(tmp_image_path)

                self.genLinuxImage_dic['kci_gen_images_list'].append(temp_gen_image_list)

    def tftp_loop_one_image(self):
        kci_gen_images_list_len = len(self.genLinuxImage_dic['kci_gen_images_list'])
        LOG_INFO('tftp_loop_one_image: TFTP-idx: {}, len(image_list): {}'.\
            format(self.tftp_idx, kci_gen_images_list_len))
        if self.tftp_idx >= kci_gen_images_list_len:
            LOG_ALERT('tftp_loop_one_image loop end')
            self.tftp_cur_image_name = ''
            sys.exit(0)

        while self.tftp_idx < kci_gen_images_list_len:
            self.tftp_cur_image_name = self.genLinuxImage_dic['kci_gen_images_list'][self.tftp_idx][0]
            self.tftp_cur_image_path = self.genLinuxImage_dic['kci_gen_images_list'][self.tftp_idx][1]

            # copy one Image to TFTP root directory
            CMD = 'cp ' + self.tftp_cur_image_path + '/*' + ' ' + self.genLinuxImage_dic['kci_tftp_dir']

            self.tftp_idx += 1
            LOG_INFO('tftp_loop_one_image: ' + CMD)
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
    # ResultData object
    resultData_obj = None

    # GenLinuxImage object
    genLiuxImage_obj = None

    # container for sending back packet to Juno
    send_pkt_dic = {}

    def __init__(self, request, client_address, _resultData_obj, _genLiuxImage_obj):
        self.request = request
        self.client_address = client_address
        self.con = Condition()
        self.message_queue = queue.Queue(20)
        self.resultData_obj = _resultData_obj
        self.genLiuxImage_obj = _genLiuxImage_obj
        LOG_INFO("init MessageParser")

    # wrapper for sending back packet
    def common_send(self, send_dic):
        ret = 0
        try:
           self.request.send(str.encode(json.dumps(send_dic)))
        except Exception:
            LOG_ERR('MessageParser common_send id: {}, type: {} [fail]'.format(send_dic['id'], send_dic['type']))
            ret = -1
        return ret

    # handle begin packet coming from Juno
    def handle_begin_pkt(self, rcv_dic):
        self.send_pkt_dic.clear()
        self.send_pkt_dic['id'] = rcv_dic['id']
        self.send_pkt_dic['type'] = PT_BEGIN_ACK
        self.send_pkt_dic['imageName'] = self.genLiuxImage_obj.tftp_cur_image_name
        self.resultData_obj.store_data('\n\nImage Begin: ' + self.send_pkt_dic['imageName'] + '\n')
        return self.common_send(self.send_pkt_dic)

    # handle end packer coming from Juno
    def handle_end_pkt(self, rcv_dic):
        self.send_pkt_dic.clear()
        self.send_pkt_dic['id'] = rcv_dic['id']
        self.send_pkt_dic['type'] = PT_END_ACK

        if self.genLiuxImage_obj.tftp_idx < len(self.genLiuxImage_obj.genLinuxImage_dic['kci_gen_images_list']):
            self.send_pkt_dic['reboot'] = 'reboot'
        else:
            self.send_pkt_dic['reboot'] = ''
        # self.resultData_obj.store_data('Image End: ' + rcv_dic['imageName'] + '\n')
        return self.common_send(self.send_pkt_dic)

    # handle file data packet coming from Juno
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

    # listen the coming packet from Juno
    def loop_images(self, message_parser):
        # input file set for select API
        inputs = [self.request]

        # output file set for select API
        outputs = []

        # container for received packet
        rcv_dic = {}

        # flag for socket connection
        connect_lost = False

        # timeout value for select API
        TIMEOUT_1MIN = 60
        # TIMEOUT_20MIN = 1200
        TIMEOUT_20MIN = 4800
        timeout = TIMEOUT_1MIN

        # if it has looped all Images, don't loop again
        if self.genLiuxImage_obj.tftp_cur_image_name == '':
            LOG_ALERT('loop_images done')
            sys.exit(0)

        while True:
            LOG_ALERT('loop_images select, timeout: {}, connect_lost: {}'.format(timeout, connect_lost))
            try:
                readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)
            except:
                LOG_ERR('\n\nloop_images select exception: timeout')
                connect_lost = True

            # select API timeout occurs
            if len(readable) == 0:
                LOG_ERR('loop_images select: timeout')
                connect_lost = True
            # have readable socket
            else:
                for s in readable:
                    data = s.recv(PKT_LEN_1M)
                    if (not data):
                        # LOG_ERR("connection lost")
                        connect_lost = True
                        break
                    rcv_dic = eval(bytes.decode(data))
                    LOG_DBG(rcv_dic)
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
                LOG_ALERT('loop_images [exit]')
                self.request.close()
                # self.genLiuxImage_obj.tftp_loop_one_image()

                # clear this critical variable, so that the tcp socket
                # connection ( see: SockTCPHandler->handle() ) disconnet normally.
                self.genLiuxImage_obj.tftp_cur_image_name = ''
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

                # time.sleep(10)
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

        LOG_ALERT("connect setup() {}\n".format(self.client_address))
        #
        # create a new message parser object for a fresh connection
        # at the same time, a specific thread being created to handle
        # packets based on this connection.
        #
        self.message_parser = MessageParser(self.request, self.client_address, g_ResultData_obj, g_genLiuxImage_obj)
        # Thread(target = self.message_parser.consum_thread, args = (self.message_parser,)).start()
        Thread(target = self.message_parser.loop_images, args = (self.message_parser,)).start()

    def finish(self):
        LOG_ALERT("connect finish req {}\n".format(self.client_address))
        g_server.close_request(self.request)

        if self.message_parser.genLiuxImage_obj.tftp_idx >= \
            len(self.message_parser.genLiuxImage_obj.genLinuxImage_dic['kci_gen_images_list']):
            LOG_ALERT('loop all image, exit [ok]')
            g_server.shutdown()
            sys.exit(0)
        else:
            self.message_parser.genLiuxImage_obj.tftp_loop_one_image()
            # reboot Juno
            REBOOT_CMD = "sshpass -p '' ssh root@10.190.0.102 '/sbin/reboot'"
            if os.system(REBOOT_CMD) < 0:
                LOG_ERR('reboot Linux [fail]')
                sys.exit(1)
            else:
                LOG_ALERT('reboot Linux [ok]')

if __name__ == "__main__":
    if os.path.exists(g_result_file) == True:
        os.system('rm -f {}'.format(g_result_file))
        LOG_ALERT('rm -f {}'.format(g_result_file))

    g_ResultData_obj = ResultData()

    pc_obj = KciParseCmdline(sys.argv[1:])
    p_dbg_init(pc_obj.VERBOSE)

    g_genLiuxImage_obj = GenLiuxImage(pc_obj.toolchain_path, pc_obj.hwboard, pc_obj.kernel_name, \
        pc_obj.defconfig_name, pc_obj.runtime_path, \
        pc_obj.tftp_dir, pc_obj.compileLinux, g_ResultData_obj)

    g_genLiuxImage_obj.tftp_loop_one_image()

    # reboot Juno
    REBOOT_CMD = "sshpass -p '' ssh root@10.190.0.102 '/sbin/reboot'"
    if os.system(REBOOT_CMD) < 0:
        LOG_ERR('reboot Linux [fail]')
        sys.exit(1)
    else:
        LOG_ALERT('reboot Linux [ok]')

    HOST,PORT = pc_obj.IP, pc_obj.PORT
    LOG_ALERT("ip: {}, port: {}".format(HOST, PORT))
    g_server = socketserver.ThreadingTCPServer((HOST, PORT), SockTCPHandler)
    g_server.serve_forever()
