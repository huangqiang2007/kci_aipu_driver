#!/usr/bin/env python3
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

class KciParseCmdline:
    IP = ''
    PORT = 19998
    toolchain_path = ''
    kernel_path = ''
    defconfig_path = ''
    VERBOSE = True

    def server_help(self):
        print('help:')
        print('kci_server.py -i ip -p port -t toolchain_path -k kernel_path -f defconfig_path -v -h]')
        print(' -i: ip_address')
        print(' -p: port')
        print(' -t: toolchain path')
        print(' -k: Linux kernel path')
        print(' -f: Linux defconfig path')
        print(' -v: verbose')
        print(' -h: help')
        sys.exit(0)

    def __init__(self, _argv):
        '''
        parse command line arguments
        '''
        try:
            opts, args = getopt.getopt(_argv, "hi:p:t:k:f:v", ["loop=","dbg_lvl="])
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
            elif opt == '-k':
                self.kernel_path = arg
                LOG_DBG("Linux kernel path: " + self.kernel_path)
            elif opt == '-f':
                self.defconfig_path = arg
                LOG_DBG("Linux defconfig path: " + self.defconfig_path)
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

        if os.path.exists(self.kernel_path) == False:
            LOG_ERR('kernel_path {}: invalid'.format(self.kernel_path))
            sys.exit(1)

        if os.path.exists(self.defconfig_path) == False:
            LOG_ERR('defconfig_path {}: invalid'.format(self.defconfig_path))
            sys.exit(1)