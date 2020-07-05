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
import glob
import random
from dbg import *
from config_case import *
from common_misc import *
from set_env import *

pcl_obj = ParseCmdline()
cmdargs_tuple = pcl_obj.parse_cmdline_args(sys.argv[1:])
print(cmdargs_tuple)

gcf_obj = GenConfigFile(cmdargs_tuple, single_graph_single_frame_dic)
gcf_obj.gcf_run_bench()