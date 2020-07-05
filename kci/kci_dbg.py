#!/usr/bin/env python3
#
# File name: dbg.py
# Author: huangq@moxigroup.com
#
# Note: this file is the main logic for debugging.
#
#
#
#

import time

#
# debug level enum
#
DBG_ERROR = 0
DBG_ALERT = 1
DBG_INFO  = 2
DBG_DEBUG = 3

#
# when it reboots system successfully, the log file will be
# rewriten.
#
file_name = "/tmp/energyroom.log"

g_file = None

#
# True: directly output to terminal
# False: backup log to a  file
#
g_verbose = True

def p_dbg_init(verbose):
	global g_file
	global g_verbose
	g_verbose = verbose
	# if (g_file is None):
	# 	g_file = open(file_name, mode='w+')

	# 	if (g_verbose == True):
	# 		print("Create a new log file: ".format(g_file))
	# 	else:
	# 		g_file.write("Create a new log file: {}\n".format(file_name))

def p_dbg(dbglevel, text):
    global g_file
    global g_verbose
    if (dbglevel <= DBG_DEBUG):
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