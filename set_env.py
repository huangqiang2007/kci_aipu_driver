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
from dbg import *

class SetEnv_CLS:
    '''
    config environment
    - load aipu driver: aipu.ko
    - config LD_LIBRARY_PATH: libaipu.so*
    '''

    # platform: juno-linux-4.9, hybrid-linux-4.9, x86-linux
    platform = ''

    def __init__(self, _platform):
        self.platform = _platform
        if _platform != "x86-linux":
            self.se_load_driver()
        self.se_set_lib_path()

    def se_load_driver(self):
        '''
        load aipu driver
        '''

        aipu_driver_path = "/dev/aipu"
        if os.path.exists(aipu_driver_path) == False:
            aipu_ko = aipu_lib_path = os.getcwd() + "/../build/" \
                + self.platform + "/lib/" + "aipu.ko"
            ret = os.system("insmod " + aipu_ko)
            if ret != 0:
                dbg_log(EM_ERROR, "insmod aipu.ko failed")
                sys.exit(1)
            else:
                dbg_log(EM_CRIT, "insmod aipu.ko ok")

    def se_set_lib_path(self):
        '''
        config LD_LIBRARY_PATH
        '''

        try:
            aipu_lib_path = os.getenv('AIPU_LIB_PATH')
            if aipu_lib_path == None:
                aipu_lib_path = os.getcwd() + "/../build/" + self.platform + "/lib"
                os.environ['AIPU_LIB_PATH'] = aipu_lib_path

                try:
                    env_lib_path = os.getenv('LD_LIBRARY_PATH')
                    if env_lib_path == None:
                        env_lib_path = aipu_lib_path
                    else:
                        env_lib_path = aipu_lib_path + ":" +env_lib_path

                    os.environ['LD_LIBRARY_PATH'] = env_lib_path

                    print(os.environ['AIPU_LIB_PATH'])
                    print(os.environ['LD_LIBRARY_PATH'])
                except Exception:
                    print("set LD_LIBRARY_PATH: NULL, exception")
            else:
                print(aipu_lib_path)
        except Exception:
            print("sl_set_lib_path: exception")
            sys.exit(1)
