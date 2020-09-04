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

import os
import sys
import queue
import json
import socket
import struct
import re
import fcntl
import getopt
from kci_dbg import *

# Class: parse the command line arguments
class KciParseCmdline:
    # server ip & port
    IP = ''
    PORT = 19998

    # specified toolchain absolute path
    toolchain_path = ''

    # HW board name
    hwboard = ''

    # Linux kernle srouce absolute path
    kernel_name = ''

    # Linux deconfig rel/abs path
    defconfig_name = ''

    # Linux image path
    linux_image_dir = ''

    tftp_dir = ''

    # dicide whether compile Linux kernel firstly, or directly use generated Linux images
    # True: compile Linux firstly
    # False: use generated images directly
    compileLinux = False

    # the runtime path for KMD and UMD source code,
    # this is for recompile aipu.ko according to different Linux kernel
    runtime_path = ''

    # test log ouput control
    # True: directly output to current terminal
    # False: output log to log file
    VERBOSE = True

    def server_help(self):
        print('help:')
        print('kci_server.py -i ip -p port -t toolchain_path \
            -b board_platform -k linux_path -f linux_config \
            --tftp TFTP_DIR -c -r runtime_path -v -h]')
        print(' -i: ip_address')
        print(' -p: port')
        print(' -t: toolchain path')
        print(' -b: hw platform [juno, 6cg]')
        print(' -k: Linux kernel version name')
        print(' -f: Linux defconfig name')
        print(' --tftp: TFTP server directory')
        print(' -c: compile Linux kernel or not')
        print(' -r: runtime KMD&UMD path')
        print(' -v: verbose')
        print(' -h: help')
        sys.exit(0)

    def __init__(self, _argv):
        '''
        parse command line arguments
        '''
        try:
            opts, args = getopt.getopt(_argv, "hi:p:t:b:k:f:r:cv", ["loop=","dbg_lvl=","tftp="])
        except getopt.GetoptError:
            LOG_ERR('kci_server.py cmdline args invalid ' + args)
            sys.exit(1)

        for opt, arg in opts:
            if opt == '-h':
                self.server_help()
            elif opt == '-i':
                self.IP = arg
                LOG_DBG("ip: " + self.IP)
            elif opt == '-p':
                self.PORT = int(arg)
                LOG_DBG("port: " + str(self.PORT))
            elif opt == '-t':
                self.toolchain_path = arg
                LOG_DBG("toolchain path: " + self.toolchain_path)
            elif opt == '-b':
                self.hwboard = arg
                LOG_DBG("toolchain path: " + self.toolchain_path)
            elif opt == '-k':
                self.kernel_name = arg
                LOG_DBG("Linux kernel name: " + self.kernel_name)
            elif opt == '-f':
                self.defconfig_name = arg
                LOG_DBG("Linux defconfig name: " + self.defconfig_name)
            elif opt in ('--tftp'):
                self.tftp_dir = arg
                LOG_DBG("TFTP Server path: " + self.tftp_dir)
            elif opt == '-c':
                self.compileLinux = True
                LOG_DBG("Linux defconfig path: " + self.defconfig_name)
            elif opt == '-r':
                self.runtime_path = arg
                LOG_DBG("Runtime KMD&UMD path: " + self.runtime_path)
            elif opt == '-v':
                self.VERBOSE = True

        if self.VERBOSE not in (True, False):
            LOG_ERR(self.VERBOSE + " is invalid")
            self.server_help()
            sys.exit(1)

        if self.IP == '':
            LOG_ERR('IP: is NULL')
            self.server_help()
            sys.exit(1)

        if self.PORT == 0:
            LOG_ERR('PORT: is NULL')
            self.server_help()
            sys.exit(1)

        if os.path.exists(self.toolchain_path) == False:
            LOG_ERR('toolchain_path {}: invalid'.format(self.toolchain_path))
            sys.exit(1)

        # if os.path.exists(self.kernel_name) == False:
        #     LOG_ERR('kernel_name {}: invalid'.format(self.kernel_name))
        #     sys.exit(1)

        # if os.path.exists(self.defconfig_name) == False:
        #     LOG_ERR('defconfig_name {}: invalid'.format(self.defconfig_name))
        #     sys.exit(1)

        if os.path.exists(self.tftp_dir) == False:
            LOG_ERR('TFTP Server path {}: invalid'.format(self.tftp_dir))
            sys.exit(1)

        if os.path.exists(self.runtime_path) == False:
            LOG_ERR('runtime path {}: invalid'.format(self.runtime_path))
            sys.exit(1)