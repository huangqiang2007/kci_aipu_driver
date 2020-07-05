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

# single_graph_single_frame test group
single_graph_single_frame_dic = {
    '[simulator]' : './aipu_simulator',
    '[loop]' : '1',
    '[output]' : 'single_graph_single_frame',
    '[cfg_dir]' : 'single_graph_single_frame',
    '[dump]' : '',
    '[debug]' : '',
    '[pipeline]' : 'n',
    '[profiling]' : 'n',
    '[thread_num]' : '0',
    '[process_num]' : '0',
    '[graph_num]' : '1',
    '[frame_num]' : '1',
    '[use_case]' : "single_graph_single_frame_test"
}

# single_graph_multi_frame test group
single_graph_multi_frame_dic = {
    '[simulator]' : './aipu_simulator',
    '[loop]' : '1',
    '[output]' : 'single_graph_multi_frame',
    '[cfg_dir]' : 'single_graph_multi_frame',
    '[dump]' : '',
    '[debug]' : '',
    '[pipeline]' : 'n',
    '[profiling]' : 'n',
    '[thread_num]' : '0',
    '[process_num]' : '0',
    '[graph_num]' : '1',
    '[frame_num]' : '4',
    '[use_case]' : "single_graph_multi_frame_test"
}

# multi_graph_single_frame test group
multi_graph_single_frame_dic = {
    '[simulator]' : './aipu_simulator',
    '[loop]' : '1',
    '[output]' : 'multi_graph_single_frame',
    '[cfg_dir]' : 'multi_graph_single_frame',
    '[dump]' : '',
    '[debug]' : '',
    '[pipeline]' : 'n',
    '[profiling]' : 'n',
    '[thread_num]' : '0',
    '[process_num]' : '0',
    '[graph_num]' : '4',
    '[frame_num]' : '1',
    '[use_case]' : "multi_graph_single_frame_test"
}

# multi_graph_multi_frame test group
mgmf_m4_f4_dic = {
    '[simulator]' : './aipu_simulator',
    '[loop]' : '1',
    '[output]' : 'mgmf_m4_f4',
    '[cfg_dir]' : 'mgmf_m4_f4',
    '[dump]' : '',
    '[debug]' : '',
    '[pipeline]' : 'n',
    '[profiling]' : 'n',
    '[thread_num]' : '0',
    '[process_num]' : '0',
    '[graph_num]' : '4',
    '[frame_num]' : '4',
    '[use_case]' : "multi_graph_multi_frame_test"
}

mgmf_m5_f4_dic = {
    '[simulator]' : './aipu_simulator',
    '[loop]' : '1',
    '[output]' : 'mgmf_m5_f4',
    '[cfg_dir]' : 'mgmf_m5_f4',
    '[dump]' : '',
    '[debug]' : '',
    '[pipeline]' : 'n',
    '[profiling]' : 'n',
    '[thread_num]' : '0',
    '[process_num]' : '0',
    '[graph_num]' : '5',
    '[frame_num]' : '2',
    '[use_case]' : "multi_graph_multi_frame_test"
}

mgmf_m6_f4_dic = {
    '[simulator]' : './aipu_simulator',
    '[loop]' : '1',
    '[output]' : 'mgmf_m6_f4',
    '[cfg_dir]' : 'mgmf_m6_f4',
    '[dump]' : '',
    '[debug]' : '',
    '[pipeline]' : 'n',
    '[profiling]' : 'n',
    '[thread_num]' : '0',
    '[process_num]' : '0',
    '[graph_num]' : '6',
    '[frame_num]' : '2',
    '[use_case]' : "multi_graph_multi_frame_test"
}

mgmf_m7_f3_dic = {
    '[simulator]' : './aipu_simulator',
    '[loop]' : '1',
    '[output]' : 'mgmf_m7_f3',
    '[cfg_dir]' : 'mgmf_m7_f3',
    '[dump]' : '',
    '[debug]' : '',
    '[pipeline]' : 'n',
    '[profiling]' : 'n',
    '[thread_num]' : '0',
    '[process_num]' : '0',
    '[graph_num]' : '7',
    '[frame_num]' : '1',
    '[use_case]' : "multi_graph_multi_frame_test"
}

mgmf_m8_f2_dic = {
    '[simulator]' : './aipu_simulator',
    '[loop]' : '1',
    '[output]' : 'mgmf_m8_f2',
    '[cfg_dir]' : 'mgmf_m8_f2',
    '[dump]' : '',
    '[debug]' : '',
    '[pipeline]' : 'n',
    '[profiling]' : 'n',
    '[thread_num]' : '0',
    '[process_num]' : '0',
    '[graph_num]' : '8',
    '[frame_num]' : '1',
    '[use_case]' : "multi_graph_multi_frame_test"
}

# pipeline test group
pipeline_dic = {
    '[simulator]' : './aipu_simulator',
    '[loop]' : '1',
    '[output]' : 'pipeline',
    '[cfg_dir]' : 'pipeline',
    '[dump]' : '',
    '[debug]' : '',
    '[pipeline]' : 'y',
    '[profiling]' : 'n',
    '[thread_num]' : '0',
    '[process_num]' : '0',
    '[graph_num]' : '2',
    '[frame_num]' : '3',
    '[use_case]' : "pipeline_test"
}

'''
dump flag
#INST -> AIPU_DUMP_INST
#RO -> AIPU_DUMP_RO
#STACK -> AIPU_DUMP_STACK
#STATIC_TENSOR -> AIPU_DUMP_STATIC_TENSOR
#REUSE_TENSOR -> AIPU_DUMP_REUSE_TENSOR
#OUT_TENSOR -> AIPU_DUMP_OUT_TENSOR
#INTER_TENSOR -> AIPU_DUMP_INTER_TENSOR
#BEFORE_RUN -> AIPU_DUMP_BEFORE_RUN
#AFTER_RUN -> AIPU_DUMP_AFTER_RUN
#eg:
# INST,RO,STACK,STATIC_TENSOR,REUSE_TENSOR,OUT_TENSOR,INTER_TENSOR,BEFORE_RUN,AFTER_RUN
'''
# dump test group
dump_dic = {
    '[simulator]' : './aipu_simulator',
    '[loop]' : '1',
    '[output]' : 'dump',
    '[cfg_dir]' : 'dump',
    '[dump]' : 'INST,RO,OUT_TENSOR,INTER_TENSOR,BEFORE_RUN,AFTER_RUN',
    '[debug]' : '',
    '[pipeline]' : 'n',
    '[profiling]' : 'n',
    '[thread_num]' : '0',
    '[process_num]' : '0',
    '[graph_num]' : '1',
    '[frame_num]' : '1',
    '[use_case]' : "dump_test"
}

# multi_thread_one_context_non_pipeline test group
multi_thread_one_context_non_pipeline_dic = {
    '[simulator]' : './aipu_simulator',
    '[loop]' : '1',
    '[output]' : 'multi_thread_one_context_non_pipeline',
    '[cfg_dir]' : 'multi_thread_one_context_non_pipeline',
    '[dump]' : '',
    '[debug]' : '',
    '[pipeline]' : 'n',
    '[profiling]' : 'n',
    '[thread_num]' : '2',
    '[process_num]' : '0',
    '[graph_num]' : '2',
    '[frame_num]' : '2',
    '[use_case]' : "multi_thread_one_context_non_pipeline_test"
}

# multi_thread_one_context_pipeline test group
multi_thread_one_context_pipeline_dic = {
    '[simulator]' : './aipu_simulator',
    '[loop]' : '1',
    '[output]' : 'multi_thread_one_context_pipeline',
    '[cfg_dir]' : 'multi_thread_one_context_pipeline',
    '[dump]' : '',
    '[debug]' : '',
    '[pipeline]' : 'y',
    '[profiling]' : 'n',
    '[thread_num]' : '2',
    '[process_num]' : '0',
    '[graph_num]' : '2',
    '[frame_num]' : '2',
    '[use_case]' : "multi_thread_one_context_pipeline_test"
}

# multi_thread_non_pipeline test group
multi_thread_non_pipeline_dic = {
    '[simulator]' : './aipu_simulator',
    '[loop]' : '1',
    '[output]' : 'multi_thread_non_pipeline',
    '[cfg_dir]' : 'multi_thread_non_pipeline',
    '[dump]' : '',
    '[debug]' : '',
    '[pipeline]' : 'n',
    '[profiling]' : 'n',
    '[thread_num]' : '2',
    '[process_num]' : '0',
    '[graph_num]' : '2',
    '[frame_num]' : '2',
    '[use_case]' : "multi_thread_non_pipeline_test"
}

# multi_thread_pipeline test group
multi_thread_pipeline_dic = {
    '[simulator]' : './aipu_simulator',
    '[loop]' : '1',
    '[output]' : 'multi_thread_pipeline',
    '[cfg_dir]' : 'multi_thread_pipeline',
    '[dump]' : '',
    '[debug]' : '',
    '[pipeline]' : 'y',
    '[profiling]' : 'n',
    '[thread_num]' : '2',
    '[process_num]' : '0',
    '[graph_num]' : '2',
    '[frame_num]' : '2',
    '[use_case]' : "multi_thread_pipeline_test"
}

# multi_process_non_pipeline test group
multi_process_non_pipeline_dic = {
    '[simulator]' : './aipu_simulator',
    '[loop]' : '1',
    '[output]' : 'multi_process_non_pipeline',
    '[cfg_dir]' : 'multi_process_non_pipeline',
    '[dump]' : '',
    '[debug]' : '',
    '[pipeline]' : 'n',
    '[profiling]' : 'n',
    '[thread_num]' : '0',
    '[process_num]' : '2',
    '[graph_num]' : '2',
    '[frame_num]' : '2',
    '[use_case]' : "multi_process_non_pipeline_test"
}

# multi_process_pipeline test group
multi_process_pipeline_dic = {
    '[simulator]' : './aipu_simulator',
    '[loop]' : '1',
    '[output]' : 'multi_process_pipeline',
    '[cfg_dir]' : 'multi_process_pipeline',
    '[dump]' : '',
    '[debug]' : '',
    '[pipeline]' : 'y',
    '[profiling]' : 'n',
    '[thread_num]' : '0',
    '[process_num]' : '2',
    '[graph_num]' : '2',
    '[frame_num]' : '2',
    '[use_case]' : "multi_process_pipeline_test"
}

'''
test case config sets

single_graph_single_frame_dic,
single_graph_multi_frame_dic,
multi_graph_single_frame_dic,
mgmf_m4_f4_dic,
mgmf_m5_f4_dic,
mgmf_m6_f4_dic,
mgmf_m7_f3_dic,
mgmf_m8_f2_dic,
pipeline_dic,
dump_dic,
multi_thread_one_context_non_pipeline_dic,
multi_thread_one_context_pipeline_dic,
multi_thread_non_pipeline_dic,
multi_thread_pipeline_dic,
multi_process_non_pipeline_dic,
multi_process_pipeline_dic
'''
test_case_config_list = [
    single_graph_single_frame_dic
]

runtime_sanity_test_case_config_list = [
    single_graph_single_frame_dic,
    single_graph_multi_frame_dic,
    multi_graph_single_frame_dic
]

validation_sanity_test_case_config_list = [
    single_graph_single_frame_dic,
    single_graph_multi_frame_dic,
    multi_graph_single_frame_dic
]

runtime_sanity_onsimulator_test_case_config_list = [
    single_graph_single_frame_dic
]
