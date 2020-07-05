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
import getopt
import subprocess
from dbg import *
from run_case import ParseBenchmark
from set_env import *
from Test_Logger import logger
# sys.path.append(os.path.abspath(os.curdir) + "/kci")
import kci.kci_common
from kci.kci_client import *

class ParseCmdline:

    # test target: [runtime_sanity, runtime_test]
    test_target = 'runtime_sanity'

    def __init__(self):
        pass

    def help(self):
        print('help:')
        print('main_entry.py -p platform -a arch -b bench_dir [-l <loop>, -d <debug_level>, -h]')
        print(' -p: platform (juno-linux-4.9, hybrid-linux-4.9, x86-linux)')
        print(' -a: arch (Z1_0904, Z1_1002, Z1_0701, Z2_1104)')
        print(' -b: bench case dir, eg: ../Z1_0701/')
        print(' -l: loop tet times')
        print(' -d: debug level (1: CRIT, 2: INFO, 3: DEBUG)')
        print(' -f: report file name (default: report.txt)')
        print(' -t: test target [runtime_sanity, runtime_sanity_onsimulator, runtime_test, validation_sanity]')
        print(' -ip: server ip (10.190.12.20)')
        print(' -port: server port (19998)')
        sys.exit(0)

    def parse_cmdline_args(self, _argv):
        '''
        parse command line arguments
        '''
        PLATFORM = 'juno-linux-4.9'
        ARCH = 'Z1_0701'
        BENCH = ''
        LOOP = 1
        DBG_LVL = '1'
        REPORT_FILE = 'report.txt'

        try:
            opts, args = getopt.getopt(_argv, "hp:a:b:l:d:f:t:", ["loop=","dbg_lvl=",'ip=','port='])
        except getopt.GetoptError:
            dbg_log(EM_ERROR, 'main_entry.py cmdline args invalid')
            sys.exit(1)

        for opt, arg in opts:
            if opt == '-h':
                self.help()
            elif opt == '-p':
                PLATFORM = arg
            elif opt == '-a':
                ARCH = arg
            elif opt == '-b':
                BENCH = arg + "/"
            elif opt == '-l':
                LOOP = int(arg)
            elif opt == '-d':
                DBG_LVL = arg
            elif opt == '-f':
                REPORT_FILE = arg
            elif opt == '-t':
                self.test_target = arg
            elif opt in ('--ip'):
                self.ip = arg
            elif opt in ('--port'):
                self.port = int(arg)

        if PLATFORM not in ('juno-linux-4.9', 'hybrid-linux-4.9', 'x86-linux'):
            dbg_log(EM_ERROR, PLATFORM + " is invalid")
            sys.exit(1)

        if ARCH not in ('Z1_0904', 'Z1_1002', 'Z1_0701', 'Z2_1104'):
            dbg_log(EM_ERROR, ARCH + " is invalid")
            sys.exit(1)

        if os.path.exists(BENCH) == False:
            dbg_log(EM_ERROR, BENCH + " is not exist")
            sys.exit(1)

        if int(LOOP) < 1:
            dbg_log(EM_ERROR, LOOP + " is invalid")
            sys.exit(1)

        if int(DBG_LVL) < 1 or int(DBG_LVL) > 3:
            dbg_log(EM_ERROR, DBG_LVL + " is invalid")
            sys.exit(1)

        # setup socket connection
        kci.kci_common.g_message_sender_obj = MessageSender(self.ip, self.port)

        # send begin-packet to client
        kci.kci_common.g_message_sender_obj.handle_begin_pkt()

        return (PLATFORM, ARCH, BENCH, LOOP, DBG_LVL, REPORT_FILE)

class GenConfigFile:
    '''
    self._platform: running platform, (juno-linux-4.9, hybrid-linux-4.9, x86-linux)
    self._arch: hardware ARCH, (Z1_0904, Z1_1002, Z1_0701, Z2_1104)
    self._bench_dir: benchmark path, eg: ../Z1_0701/
    self._loop: loop test times
    self._dbg_levl: debug level
    self._report_file: report file name, eg: ../report.txt
    self.cfg_dic = _cfg_dic
    self.test_case_dir
    '''
    # test case path
    test_case_dir = ''

    def __init__(self, _cmdargs_tuple, _cfg_dic):
        self._platform = _cmdargs_tuple[0]
        self._arch = _cmdargs_tuple[1]
        self._bench_dir = _cmdargs_tuple[2]
        self._loop = _cmdargs_tuple[3]
        self._dbg_levl = _cmdargs_tuple[4]
        self._report_file = _cmdargs_tuple[5]

        self.cfg_dic = _cfg_dic

        self.test_case_dir = "../build/" + self._platform + "/" + _cfg_dic['[use_case]']
        if os.path.exists(self.test_case_dir) == False:
            dbg_log(EM_ERROR, self.test_case_dir + " not exist")
            sys.exit(1)

        # construct output directory
        self.output_rel_dir = "./" + self._arch + "_ouput"
        self.output_abs_dir = os.getcwd() + "/../" + self._arch + "_ouput/"
        ret = os.system("mkdir -p " + self.output_abs_dir)
        if ret != 0:
            dbg_log(EM_ERROR, "mkdir -p " + self.output_abs_dir + " failed")

    def gcf_gen_cfg_data(self, fp, _frameNum, _bench_case):
        '''
        extract data group of chosen Benchmark case
        @ fp: config file handle
        @ _frameNum: loop times of each Benchmark data group
        '''

        fp.writelines("\n[bench_dir]\n")
        if self._bench_dir[0:2] == "..":
            fp.writelines(self._bench_dir[1:] + "\n")
        else:
            fp.writelines(self._bench_dir + "\n")

        bin_list = self.pb_obj.benchmark_data_dic[_bench_case]

        # case begin
        fp.writelines("\n[case_name]\n")
        fp.writelines(_bench_case + "\n\n")
        fp.writelines("[aipubin]\n")
        fp.writelines(bin_list[0] + "\n")

        # input.bin and output.bin pairs
        for frame in range(1, _frameNum + 1):
            fp.writelines("\n[input]\n")
            for input_bin in bin_list[frame][0]:
                fp.writelines(input_bin + "\n")
            fp.writelines("[end]\n")
            fp.writelines("[check]\n")
            fp.writelines(bin_list[frame][1] + "\n")

        # case end
        fp.writelines("\n[case_end]" + "\n")
        fp.flush()

    def gcf_gen_cfg_file(self, _cfg_dic, _bench_case):
        '''
        generate config file for each test case
        @ cfg_dic: config parameters dictionary which has to contain the below parameters
        [simulator]:
        [arch]:
        [loop]:
        [output]:
        [cfg_dir]:
        [dump]:
        [debug]:
        [pipeline]:
        [profiling]:
        [thread_num]:
        [process_num]:
        [graph_num]:
        [frame_num]:
        [use_case]:
        '''

        # return value
        ret = -1

        use_case = _cfg_dic["[use_case]"]
        output_item = _cfg_dic["[output]"]

        cfg_file_name = self.test_case_dir + "/" + _bench_case + ".cfg"
        fp_cfg_file = open(cfg_file_name, "w+")

        _graphNum = _cfg_dic["[graph_num]"]
        _frameNum = _cfg_dic["[frame_num]"]

        # generate basic items, write [arch] item at file head
        fp_cfg_file.writelines('[arch]' + "\n")
        fp_cfg_file.writelines(_cfg_dic['[arch]'] + "\n")
        for key, val in _cfg_dic.items():
            # [output] item: one kind of test config
            if key == '[output]' or key == '[cfg_dir]':
                val = self.output_rel_dir + "/" + use_case + "/" + _bench_case + "/"
                fp_cfg_file.writelines(key + "\n")
                if val[0:2] == "..":
                    fp_cfg_file.writelines(val[1:] + "\n")
                else:
                    fp_cfg_file.writelines(val + "\n")
            # skip these items
            elif val == "" or key == '[graph_num]' or key == '[frame_num]' \
                or key == '[use_case]' or key == '[arch]':
                continue
            else:
                fp_cfg_file.writelines(key + "\n")
                fp_cfg_file.writelines(val + "\n")

        self.gcf_gen_cfg_data(fp_cfg_file, int(_frameNum), _bench_case)

        fp_cfg_file.flush()
        fp_cfg_file.close()

    def gcf_gen_cfgs_for_testcase(self, _cfg_dic):
        self.pb_obj = ParseBenchmark(self._arch, self._bench_dir)
        for _benchcase in self.pb_obj.benchmark_name_list:
            self.gcf_gen_cfg_file(_cfg_dic, _benchcase)

    def gcf_run_bench(self):
        loop = 0
        ret = 0

        if self._arch == 'Z1_0904':
            _arch_num = '0'
        elif self._arch == 'Z1_1002':
            _arch_num = '2'
        elif self._arch == 'Z1_0701':
            _arch_num = '3'
        elif self._arch == 'Z2_1104':
            _arch_num = '0'
        else:
            dbg_log(EM_ERROR, self._arch + " is not support")
            sys.exit(1)

        self.cfg_dic['[arch]'] = _arch_num

        # set environment parameters
        sl_obj = SetEnv_CLS(self._platform)

        self.gcf_gen_cfgs_for_testcase(self.cfg_dic)
        os.chdir("../")

        rst_file = "./" + self._arch + "_result.log"
        if os.path.exists(rst_file):
            os.remove(rst_file)

        _result_fp = open(rst_file, "w+")

        # init test logger
        logger.set_module_name('Benchmark')
        logger.set_print_level('Test_Element')

        while loop < self._loop:
            _result_fp.writelines("loop: " + str(loop) + "\n")
            for _benchcase in self.pb_obj.benchmark_name_list:
                dbg_log(EM_DBG, _benchcase)
                dbg_log(EM_DBG, self.pb_obj.benchmark_data_dic[_benchcase])

                # get use case name and output directory name
                use_case = self.cfg_dic["[use_case]"]
                output = self.cfg_dic["[output]"]
                logger.add_group('all')
                logger.add_unit(use_case)
                logger.add_element(output)
                logger.add_case(_benchcase)

                cfg_file_name = "./build/" + self._platform + "/" \
                     + use_case + "/" + _benchcase + ".cfg"
                if os.path.isfile(cfg_file_name) == False:
                    dbg_log(EM_ERROR, cfg_file_name + " is not exist")
                    ret = -1
                dbg_log(EM_DBG, cfg_file_name)
                # check use case binary
                if ret == 0:
                    use_case_bin = "aipu_" + use_case
                    case_path = "./build/" +  self._platform + "/" + use_case + "/" + use_case_bin
                    if os.path.isfile(case_path) == False:
                        dbg_log(EM_ERROR, case_path + " is not exist")
                        ret = -1

                    dbg_log(EM_DBG, case_path)

                # realy run use case here
                if ret == 0:
                    ret = os.system(case_path + " " + cfg_file_name + " " + self._dbg_levl)
                    if ret == 0:
                        result = "case: " + use_case + ", " + _benchcase + " [ok]"
                        dbg_log(EM_CRIT, result)
                        _result_fp.writelines(result + "\n")
                        _result_fp.flush()
                        logger.set_result(True)
                    else:
                        result = "case: " + use_case + ", " + _benchcase + " [failed]"
                        dbg_log(EM_ERROR, result)
                        _result_fp.writelines(result + "\n")
                        _result_fp.flush()
                        logger.set_result(False)

            # next loop
            loop += 1

        # store test result to file
        logger.end_record()
        #print(logger)
        logger.to_txt(self._report_file)
