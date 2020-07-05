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

# debug level
EM_ERROR = 1
EM_CRIT = 2
EM_INFO = 3
EM_DBG = 4
EM_MAX = 5

# default debug level
g_dbg_level = EM_INFO

# log print func
def dbg_log(level, x):
    if (level <= g_dbg_level):
        if (level == EM_ERROR):
            print("ERROR ", end='')
            print(x)
        elif (level == EM_CRIT):
            print("CRIT ", end='')
            print(x)
        elif (level == EM_INFO):
            print("info ", end='')
            print(x)
        elif (level == EM_DBG):
            print("DBG ", end='')
            print(x)
