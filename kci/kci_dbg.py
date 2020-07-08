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
# Note: this file is the main logic for debugging.
#
import sys
import time

#
# debug level enum
#
DBG_ERROR = 0
DBG_ALERT = 1
DBG_INFO  = 2
DBG_DEBUG = 3
g_debug_level = DBG_INFO

#
# when it reboots system successfully, the log file will be
# rewriten.
#
file_name = "./kci_test.log"

g_file = None

#
# True: directly output to terminal
# False: backup log to a file
#
g_verbose = True

def p_dbg_init(verbose):
    global g_file
    global g_verbose
    g_verbose = verbose
    if g_verbose == False:
        try:
            g_file = open(file_name, mode='w+')
        except:
            print('p_dbg_init open {} [fail]'.format(file_name))
            sys.exit(1)

        g_file.write("Create a new log file: {}\n".format(file_name))
    else:
        print("Create a new log file: {}".format(file_name))

def p_dbg(dbglevel, text):
    global g_file
    global g_verbose
    global g_debug_level

    if (dbglevel <= g_debug_level):
        if (dbglevel == DBG_ERROR):
            if (g_verbose == True):
                print("[error] {}".format(text))
            else:
                g_file.write("{} [error] {}\n".format(time.time(), text))
        elif (dbglevel == DBG_ALERT):
            if (g_verbose == True):
                print("[alert] {}".format(text))
            else:
                g_file.write("{} [alert] {}\n".format(time.time(), text))
        elif (dbglevel == DBG_INFO):
            if (g_verbose == True):
                print("[info] {}".format(text))
            else:
                g_file.write("{} [info] {}\n".format(time.time(), text))
        elif (dbglevel == DBG_DEBUG):
            if (g_verbose == True):
                print("[debug] {}".format(text))
            else:
                g_file.write("{} [debug] {}\n".format(time.time(), text))

    if (g_verbose == False):
        g_file.flush()

def LOG_ERR(x):
    p_dbg(DBG_ERROR, x)

def LOG_ALERT(x):
    p_dbg(DBG_ALERT, x)

def LOG_INFO(x):
    p_dbg(DBG_INFO, x)

def LOG_DBG(x):
    p_dbg(DBG_DEBUG, x)

if __name__ == "__main__":
	print("p_dbg_init()\n")
	p_dbg_init(True)
	p_dbg(DBG_ALERT, "alert log")
	p_dbg(DBG_INFO, "info log")
	p_dbg(DBG_DEBUG, "debug log")
