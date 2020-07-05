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
import subprocess
from config_case import *
from common_misc import *
from run_case import LoopAllCases
from dbg import *

print("argc {}, argv {}".format(len(sys.argv), sys.argv))

pcl_obj = ParseCmdline()
cmdargs_tuple = pcl_obj.parse_cmdline_args(sys.argv[1:])
print(cmdargs_tuple)

if pcl_obj.test_target == 'runtime_sanity':
    config_list = runtime_sanity_test_case_config_list
elif pcl_obj.test_target == 'runtime_test':
    config_list = test_case_config_list
elif pcl_obj.test_target == 'validation_sanity':
    config_list = validation_sanity_test_case_config_list
elif pcl_obj.test_target == 'runtime_sanity_onsimulator':
    config_list = runtime_sanity_onsimulator_test_case_config_list
else:
    print("no support " + pcl_obj.test_target)
    sys.exit(1)

lac_obj = LoopAllCases()
lac_obj.lac_run_all(cmdargs_tuple, config_list)