#!/usr/bin/env python3

import sys
import queue
import json
import socket
import struct
import re
import fcntl
import getopt
from dbg import *

class ParseCmdline:
    def __init__(self):
        self.IP = ''
        self.PORT = 0
        self.VERBOSE = False

    def server_help(self):
        print('help:')
        print('kci_server.py -p ip, -v -h]')
        print(' -p: ip_address')
        print(' -v: verbose')
        print('	-h: help')
        sys.exit(0)

    def parse_cmdline_server(self, _argv):
        '''
        parse command line arguments
        '''
        try:
            opts, args = getopt.getopt(_argv, "hi:p:v", ["loop=","dbg_lvl="])
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