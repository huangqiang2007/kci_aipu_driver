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
from set_env import *
from Test_Logger import logger
# sys.path.append(os.path.abspath(os.curdir) + "/kci")
import kci.kci_common
import kci.kci_client

class ParseBenchmark:
	'''
	@ brief:
		this class is for a group benchmark cases and extract *.bin files in each case
	'''

	# Z1_0904, Z1_1002, Z1_0701, Z2_1104
	arch = ''

	# ./Z1_0701/ etc
	benchPath = ''

	# this list is the keys for benchmark_data_dic
	benchmark_name_list = []
	benchmark_data_dic = {}

	def __init__(self, _arch, _benchPath):
		self.arch = _arch
		self.benchPath = _benchPath
		self.benchmark_name_list = os.listdir(_benchPath)
		dbg_log(EM_DBG, ', '.join(self.benchmark_name_list))

		# check whethre each benchmark has multi-batch input/output data
		_batch = False
		if os.path.isdir(_benchPath + "/" + self.benchmark_name_list[0] + "/batch_0"):
			_batch = True

		if _batch == False:
			# one benchmark has one bin group
			for benchName in self.benchmark_name_list:
				binGroup_list = self.find_benchmark_bin_group(_benchPath + "/" + benchName)
				dbg_log(EM_DBG, benchName + ":")
				dbg_log(EM_DBG, binGroup_list)
				self.benchmark_data_dic[benchName] = binGroup_list
				dbg_log(EM_DBG, self.benchmark_data_dic)
		else:
			# one benchmark has multiple bin group
			for benchName in self.benchmark_name_list:
				binGroup_list = self.find_benchmark_batch_bin_group(_benchPath + "/" + benchName)
				dbg_log(EM_DBG, benchName + ":")
				dbg_log(EM_DBG, binGroup_list)
				self.benchmark_data_dic[benchName] = binGroup_list
				dbg_log(EM_DBG, self.benchmark_data_dic)

		dbg_log(EM_DBG, self.benchmark_data_dic)

	def find_benchmark_bin_group(self, _benchmark_name):
		'''
		find aipu.bin, input.bin and output.bin
		@ _benchmark_name: benchmark case name
		@ retval: bin files list
		'''

		# the list for *.bin files belong to one Benchmark case
		singleBinGroup_list = []

		# extract aipu.bin
		ret_list = glob.glob(_benchmark_name + '/aipu.bin')
		if (len(ret_list) > 0):
			pos = ret_list[0].rfind("/")
			bin = ret_list[0][(pos + 1) : len(ret_list[0])]
			singleBinGroup_list.append(bin)
			dbg_log(EM_DBG, bin)
		else:
			dbg_log(EM_ERROR, "aipu.bin not exist")

		for i in range(10):
			# int a temp list for each batch
			binGroup_list = []

			# extract input*.bin
			ret_list = glob.glob(_benchmark_name + '/input*.bin')
			if (len(ret_list) > 0):
				input_bin_list = []
				for input_bin in ret_list:
					pos = input_bin.rfind("/")
					bin = input_bin[(pos + 1) : len(input_bin)]
					input_bin_list.append(bin)
					dbg_log(EM_DBG, bin)

				binGroup_list.append(input_bin_list)
			else:
				dbg_log(EM_ERROR, "input.bin not exist")

			# extract check.bin
			ret_list = glob.glob(_benchmark_name + '/output1.bin')
			if (len(ret_list) > 0):
				pos = ret_list[0].rfind("/")
				bin = ret_list[0][(pos + 1) : len(ret_list[0])]
				binGroup_list.append(bin)
				dbg_log(EM_DBG, bin)
			else:
				dbg_log(EM_ERROR, "output.bin not exist")

			singleBinGroup_list.append(binGroup_list)

		#dbg_log(EM_INFO, binGroup_list)
		return singleBinGroup_list

	def find_benchmark_batch_bin_group(self, _benchmark_name):
		'''
		find aipu.bin, input.bin and output.bin for every batch
		@ _benchmark_name: benchmark case path
		@ retval: bin files list
		'''

		# the list for *.bin files belong to one Benchmark case
		batchBinGroup_list = []

		# extract aipu.bin
		ret_list = glob.glob(_benchmark_name + '/aipu.bin')
		if (len(ret_list) > 0):
			pos = ret_list[0].rfind("/")
			bin = ret_list[0][(pos + 1) : len(ret_list[0])]
			batchBinGroup_list.append(bin)
			dbg_log(EM_DBG, bin)
		else:
			dbg_log(EM_ERROR, "aipu.bin not exist")

		for i in range(10):
			# int a temp list for each batch
			binGroup_list = []

			batch_folder = "batch_" + str(i)
			batch_folder_path = _benchmark_name + "/" + batch_folder
			if os.path.isdir(batch_folder_path) == False:
				print(batch_folder_path + " no exist")
				continue

			# extract input*.bin
			ret_list = glob.glob(batch_folder_path + '/input*.bin')
			if (len(ret_list) > 0):
				input_bin_list = []
				for input_bin in ret_list:
					pos = input_bin.rfind("/")
					bin = batch_folder + "/" + input_bin[(pos + 1) : len(input_bin)]
					input_bin_list.append(bin)
					dbg_log(EM_DBG, bin)

				binGroup_list.append(input_bin_list)
			else:
				dbg_log(EM_ERROR, "input.bin not exist")

			# extract check.bin
			ret_list = glob.glob(batch_folder_path + '/output1.bin')
			if (len(ret_list) > 0):
				pos = ret_list[0].rfind("/")
				bin = batch_folder + "/" + ret_list[0][(pos + 1) : len(ret_list[0])]
				binGroup_list.append(bin)
				dbg_log(EM_DBG, bin)
			else:
				dbg_log(EM_ERROR, "output.bin not exist")

			#dbg_log(EM_INFO, binGroup_list)
			batchBinGroup_list.append(binGroup_list)

		#dbg_log(EM_INFO, batchBinGroup_list)
		return batchBinGroup_list

class RunCases:
	'''
	@ brief:
		- generate config file for each test case
		- run test based on the generated config file
	'''

	# Z1_0904, Z1_1002, Z1_0701, Z2_1104
	arch = ''

	# confie file name
	cfg_file_name = ''

	# ./Z1_0701/ etc
	benchPath = ''
	chosen_case_dic = {}

	# case number
	case_num = 1

	# current directory
	cur_dir = ''

	# output absolute and relative directory
	output_abs_dir = ''
	output_rel_dir = ''

	def __init__(self, _parseBenchmark_cls):
		self.parseBenchmark_cls = _parseBenchmark_cls
		self.arch = _parseBenchmark_cls.arch
		self.benchPath = _parseBenchmark_cls.benchPath

		# construct output directory
		self.output_rel_dir = "../" + self.arch + "_ouput/"
		self.cur_dir = os.getcwd()
		self.output_abs_dir = self.cur_dir + "/../" + self.arch + "_ouput/"
		ret = os.system("mkdir -p " + self.output_abs_dir)
		if ret != 0:
			dbg_log(EM_ERROR, "mkdir -p " + self.output_abs_dir + " failed")
		#dbg_log(EM_INFO, _parseBenchmark_cls.benchmark_name_list)

	def rc_gen_random_case(self, _caseNum):
		'''
		random chose _caseNum Benchmark cases as current round testing
		@ _caseNum: Benchmark case number
		'''

		# clear chose_case list
		self.chosen_case_dic.clear()

		ben_name_list_len = len(self.parseBenchmark_cls.benchmark_name_list)
		case_list = random.sample(range(0, ben_name_list_len - 1), _caseNum)
		dbg_log(EM_DBG, "case_list len = {}".format(len(case_list)))
		for i in case_list:
			self.chosen_case_dic[self.parseBenchmark_cls.benchmark_name_list[i]] = \
				self.parseBenchmark_cls.benchmark_data_dic[self.parseBenchmark_cls.benchmark_name_list[i]]

		dbg_log(EM_DBG, self.chosen_case_dic)

	def rc_gen_data_file(self, fp, _frameNum):
		'''
		extract data group of chosen Benchmark case
		@ fp: config file handle
		@ _frameNum: loop times of each Benchmark data group
		'''

		fp.writelines("\n[bench_dir]\n")
		fp.writelines(self.benchPath + "\n")
		for key in self.chosen_case_dic:
			case_trace_list = []
			bin_list = self.chosen_case_dic[key]

			# case begin
			fp.writelines("\n[case_name]\n")
			fp.writelines(key + "\n\n")
			fp.writelines("[aipubin]\n")
			fp.writelines(bin_list[0] + "\n")
			case_trace_list.append(key)
			case_trace_list.append(bin_list[0])

			# input.bin and output.bin pairs
			for frame in range(1, _frameNum + 1):
				batch_bin_list = bin_list[frame]
				fp.writelines("\n[input]\n")
				case_trace_list.append(batch_bin_list)
				for input_bin in batch_bin_list[0]:
					fp.writelines(input_bin + "\n")
				fp.writelines("[end]\n")
				fp.writelines("[check]\n")
				fp.writelines(batch_bin_list[1] + "\n")

			# dump benchmark data collection
			dbg_log(EM_CRIT, case_trace_list)

			# case end
			fp.writelines("\n[case_end]" + "\n")
			fp.flush()

	def rc_gen_cfg_file(self, _cfg_dic):
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
		case_cfg_dir = self.output_abs_dir + "/" + use_case
		cfg_file_dir = case_cfg_dir + "/" + output_item
		ret = os.system("mkdir -p " + cfg_file_dir)
		if ret != 0:
			dbg_log(EM_ERROR, "mkdir -p " + cfg_file_dir + " failed")
			return ret

		self.cfg_file_name = cfg_file_dir + "/" + output_item + ".cfg"
		fp_cfg_file = open(self.cfg_file_name, "w+")

		_graphNum = _cfg_dic["[graph_num]"]
		_frameNum = _cfg_dic["[frame_num]"]

		# generate basic items, write [arch] item at file head
		fp_cfg_file.writelines('[arch]' + "\n")
		fp_cfg_file.writelines(_cfg_dic["[arch]"] + "\n")
		for key, val in _cfg_dic.items():
			# [output] item: one kind of test config
			if key == '[output]' or key == '[cfg_dir]':
				val = self.output_rel_dir + "/" + use_case + "/" + output_item + "/"
				fp_cfg_file.writelines(key + "\n")
				fp_cfg_file.writelines(val + "\n")
			# skip these items
			elif val == "" or key == '[graph_num]' or key == '[frame_num]' \
				or key == '[use_case]' or key == '[arch]':
				continue
			else:
				fp_cfg_file.writelines(key + "\n")
				fp_cfg_file.writelines(val + "\n")

		# generate random graphs conbination
		self.rc_gen_random_case(int(_graphNum))

		# generate data pairs for each graph
		self.rc_gen_data_file(fp_cfg_file, int(_frameNum))

		# close file
		fp_cfg_file.close()
		return ret

	def rc_run_case(self, _platform, _cfg_dic, _dbg_levl, _result_fp):
		'''
		run single test case
		@ _platform: platform(juno-linux-4.9, hybrid-linux-4.9, x86-linux)
		@ _cfg_dic: config parameters dictionary
		'''

    	# return value
		ret = 0

		# get use case name and output directory name
		use_case = _cfg_dic["[use_case]"]
		output = _cfg_dic["[output]"]
		logger.add_group('all')
		logger.add_unit(use_case)
		logger.add_element(output)
		logger.add_case(output)

		# check config
		ret = self.rc_gen_cfg_file(_cfg_dic)
		if ret == 0:
			if os.path.isfile(self.cfg_file_name) == False:
				dbg_log(EM_ERROR, self.cfg_file_name + " is not exist")
				ret = -1

		# check use case binary
		if ret == 0:
			use_case_bin = "aipu_" + use_case
			case_path = self.cur_dir + "/../build/" +  _platform + "/" \
				+ use_case + "/" + use_case_bin
			if os.path.isfile(case_path) == False:
				dbg_log(EM_ERROR, case_path + " is not exist")
				ret = -1

		# realy run use case here
		if ret == 0:
			ret = os.system(case_path + " " + self.cfg_file_name + " " + _dbg_levl)
			if ret == 0:
				result = "case: " + use_case + ", " + output + " [ok]"
				dbg_log(EM_CRIT, result)
				_result_fp.writelines(result + "\n")
				_result_fp.flush()
				logger.set_result(True)
				return ret

		result = "case: " + use_case + ", " + output + " [failed]"
		dbg_log(EM_ERROR, result)
		_result_fp.writelines(result + "\n")
		_result_fp.flush()
		logger.set_result(False)
		return ret

class LoopAllCases:
	'''
	@ brief:
		loop all test cases
	'''

	# record file handle
	result_fp = None

	def __init__(self):
		pass

	def lac_result_file(self, _arch):
		'''
		create test result record file
		'''

		rst_file = "../" + _arch + "_result.log"
		if os.path.exists(rst_file):
			os.remove(rst_file)

		rst_fp = open(rst_file, "w+")
		return rst_fp

	def lac_run_all(self, _cmdargs_tuple, _all_cfg_list):
		'''
		run all test cases
		@ _cmdargs_tuple[5]: cmdline args tuple
			_cmdargs_tuple[0]: running platform, (juno-linux-4.9, hybrid-linux-4.9, x86-linux)
			_cmdargs_tuple[1]: hardware ARCH, (Z1_0904, Z1_1002, Z1_0701, Z2_1104)
			_cmdargs_tuple[2]: benchmark path, eg: ../Z1_0701/
			_cmdargs_tuple[3]: loop test times
			_cmdargs_tuple[4]: debug level
			_cmdargs_tuple[5]: report file name, eg: ../report.txt
		@ _all_cfg_list: the list contains all test configuration
		'''
		# init loop time
		loop = 0

		_platform = _cmdargs_tuple[0]
		_arch = _cmdargs_tuple[1]
		_bench_dir = _cmdargs_tuple[2]
		_loop = _cmdargs_tuple[3]
		_dbg_levl = _cmdargs_tuple[4]
		_report_file = _cmdargs_tuple[5]

		# convert string ARCH to number ARCH
		if _arch == 'Z1_0904':
			_arch_num = '0'
		elif _arch == 'Z1_1002':
			_arch_num = '2'
		elif _arch == 'Z1_0701':
			_arch_num = '3'
		elif _arch == 'Z2_1104':
			_arch_num = '0'
		else:
			dbg_log(EM_ERROR, _arch + " is not support")
			sys.exit(1)

		# init test logger
		logger.set_module_name('Runtime')
		logger.set_print_level('Test_Element')

		# create record file
		self.result_fp = self.lac_result_file(_arch)

		# set environment parameters
		sl_obj = SetEnv_CLS(_platform)

		# parse benchmark cases
		pb_obj = ParseBenchmark(_arch, _bench_dir)

		# run single test case based on the generated config file
		rc = RunCases(pb_obj)

		# set simulator's path
		_simulator = '.' + _all_cfg_list[0]['[simulator]']
		while loop < _loop:
			self.result_fp.writelines("loop: " + str(loop) + "\n")
			for _cfg_dic in _all_cfg_list:
				_cfg_dic['[arch]'] = _arch_num
				_cfg_dic['[simulator]'] = _simulator
				rc.rc_run_case(_platform, _cfg_dic, _dbg_levl, self.result_fp)
			loop += 1

		# close result file
		self.result_fp.close()

		# store test result to file
		logger.end_record()
		#print(logger)
		logger.to_txt(_report_file)

		# send back data-packet
		kci.kci_common.g_message_sender_obj.handle_file_pkt(_report_file)

		# send back end-packet
		kci.kci_common.g_message_sender_obj.handle_end_pkt()
