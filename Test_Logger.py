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

import datetime
import re
import time
# from py._xmlgen import html


class Result:
    unknown = "UNKNOWN"
    error = 'ERROR'
    failed = 'FAILED'
    passed = 'PASSED'
    skiped = 'SKEPED'
    xfailed = 'X_FAILED'
    xpassed = 'X_PASSED'


def get_level_name(level: int):
    if level == -1:
        return "All"
    elif level == 0:
        return "Test_Logger"
    elif level == 1:
        return 'Test_Group'
    elif level == 2:
        return 'Test_Unit'
    elif level == 3:
        return 'Test_Element'
    # elif level == 4:
    #     return 'Test_Case'    # Case no a 'level'
    else:
        # for > 5 lever tree
        return '+'


def get_level_prefix_name(level: int):
    if level == -1:
        return "All"
    elif level == 0:
        return "Logger"
    elif level == 1:
        return 'Group'
    elif level == 2:
        return 'Unit'
    elif level == 3:
        return 'Element'
    # elif level == 4:
    #     return 'Case'
    else:
        # for > 5 lever tree
        return '+'


class LoggerTreeNode(object):

    def __init__(self, level: int, desc: str = 'untitled'):
        self.level = level
        self.level_name = '+'
        self.desc = desc
        self.result = Result.unknown
        self.logs = []
        self.log_expect = None
        self.__duration = 0
        self.__start_time = None
        self.__end_time = None
        self.__step = 1
        self.children = []
        self.start_timing()

    def start_timing(self):
        self.__start_time = time.time()

    def end_timing(self):
        self.__end_time = time.time()
        self.__duration = self.__end_time - self.__start_time

    def add_step(self, log: str):
        log = str(log)
        self.logs.append(
            '[Step ' + str(self.__step) + ']' + log
        )
        self.__step += 1

    def add_comment(self, log: str):
        log = str(log)
        self.logs.append(
            '[Comment]' + log
        )

    def add_error(self, err_desc, is_exception):
        # todo: ? exception means...?
        log = str(err_desc)
        self.logs.append(
            '[Error]' + log
        )

    def set_expect(self, log):
        log = str(log)
        self.log_expect = '[Expect]' + log

    def get_passed_num(self):
        if not self.children:
            if self.result == Result.passed:
                return 1
            else:
                return 0
        else:
            cnt = 0
            for child in self.children:
                cnt += child.get_passed_num()
            return cnt

    def get_passed_num_on_level(self, level):
        if not self.children:
            if self.result == Result.passed and self.level >= level:
                return 1
            else:
                return 0
        else:
            cnt = 0
            for child in self.children:
                cnt += child.get_passed_num_on_level(level)
            return cnt

    def get_total_num(self):
        if not self.children:
            return 1
        else:
            cnt = 0
            for child in self.children:
                cnt += child.get_total_num()
            return cnt

    def get_total_num_on_level(self, level):
        assert isinstance(level, int)
        if not self.children:
            if self.level >= level:
                return 1
            else:
                return 0
        else:
            cnt = 0
            for child in self.children:
                cnt += child.get_total_num_on_level(level)
            return cnt

    def get_passrate(self):
        b = self.get_total_num()
        if b is not 0:
            return self.get_passed_num() / b
        else:
            return 0

    def get_passrate_on_level(self, level):
        assert isinstance(level, int)
        b = self.get_total_num_on_level(level)
        if b is not 0:
            return self.get_passed_num_on_level(level) / b
        else:
            return 0

    def get_duration(self):
        if not self.children:
            return self.__duration
        else:
            cnt = 0
            for child in self.children:
                cnt += child.get_duration()
            return cnt

    def set_duration(self, d):
        self.__duration = d

    def get_duration_on_level(self, level):
        assert isinstance(level, int)
        if not self.children:
            if self.level >= level:
                return self.__duration
            else:
                return 0
        else:
            cnt = 0
            for child in self.children:
                cnt += child.get_duration_on_level(level)
            return cnt

    def get_tree_str_list(self, node_flag: str = '', stop_level=-1):
        if stop_level != -1 and stop_level < self.level:
            return []
        if self.children:
            lines = ["{}level{}/{}: {}".format(node_flag, self.level, self.level_name, self.desc)]
            if node_flag == '  `' :
                node_flag = '   '
                lines += ["{}Result: "
                      "{}_Passrate {:.2f}%, "
                      "Total {}, "
                      "Failed {}, "
                      "Passed {}, "
                      "{}_Total_Time {:.3f}s".format(\
                    node_flag,\
                    get_level_prefix_name(self.level), self.get_passrate() * 100,\
                    self.get_total_num(),\
                    self.get_total_num() - self.get_passed_num(),\
                    self.get_passed_num(),\
                    get_level_prefix_name(self.level), self.get_duration())]
        else:
            lines = ["{}level{}/{}: {}".format(node_flag, self.level, self.level_name, self.desc)]
            if node_flag == '  `':
                node_flag = '   '
            lines += ["{}Result: {}, duration {:.3f}s".format(node_flag, self.result, self.get_duration())]
        if node_flag == '  `':
            node_flag = '   '
        for i, child in enumerate(self.children):
            if i == len(self.children) - 1:
                extra_lines = child.get_tree_str_list('  `', stop_level)
            else:
                extra_lines = child.get_tree_str_list('  |', stop_level)
            for extra_line in extra_lines:
                lines.append(node_flag + extra_line)
        for log in self.logs:
            lines.append(node_flag + '  ' + log)
        if self.log_expect:
            lines.append(node_flag + '  ' + self.log_expect)
        return lines


    # def get_tree_html(self):
    #     level_name = get_level_name(self.level)
    #     if self.get_passrate() < 1:
    #         flag = html.span('Passed', class_='summary-flag')
    #     else:
    #         flag = html.span('Failed', class_='summary-flag')
    #     desc = html.span(self.desc, class_='summary-desc')
    #     #result = html.span(
    #     #    f"{level_name}  {self.desc}  passrate: {self.get_passrate() * 100:.2f}%"
    #     #    f"  duration: {self.get_duration():.3f} s",
    #     #    class_='summary-result')
    #     result = html.span(
    #         "{}  {}  passrate: {:.2f}%".format(level_name, self.desc, self.get_passrate() * 100),
    #         "  duration: {:.3f} s".format(self.get_duration()),
    #         class_='summary-result')
    #     extra = html.div('', class_="extra")
    #     # for every case
    #     logs = html.p()

    #     if self.result is None:
    #         logs.append(html.p('No Result Case'))
    #         logs.append('FAILED')
    #         # no error:

    #     for log in self.logs:
    #         logs.append(html.p(log))
    #     if self.log_expect:
    #         logs.append(html.p(self.log_expect))

    #     for i, child in enumerate(self.children):
    #         extra.append(child.get_tree_html())

    #     extra.append(logs)
    #     return html.div([html.div([flag, desc, result]), extra], class_='summary-line')


    def __str__(self):
        lines = self.get_tree_str_list()
        str = ''
        for line in lines:
            str += line + '\n'
        return str

    def __eq__(self, other):
        return self.desc == other


class Test_Logger(object):
    #current_group: LoggerTreeNode = None
    #current_unit: LoggerTreeNode = None
    #current_element: LoggerTreeNode = None
    #current_case: LoggerTreeNode = None
    #log_root: LoggerTreeNode = None
    #print_level: int = 1
    #print_level_str = 'Test_Group'
    #ENABLE_HTML_REPORT: bool = True
    current_group = None
    current_unit = None
    current_element = None
    current_case = None
    log_root = None
    print_level = 1
    print_level_str = 'Test_Group'
    ENABLE_HTML_REPORT = True
    TXT_REPORT_SAVE_PATH = 'report.txt'
    HTML_REPORT_SAVE_PATH = 'report.html'

    def __init__(self, logger_desc='untitled_logger'):
        self.log_root = LoggerTreeNode(0, logger_desc)
        self.log_root.level_name = 'Test_Logger'

    def set_module_name(self, name):
        """
        :param name:
        for nightly/weekly/signoff test:
        your param name must one of this str:
        'Benchmark', 'Parser', 'AQT', 'GBuilder', 'Simulator', 'Layerlib', 'Compiler', 'Runtime', 'Profiler'
        'Debugger', 'Assembler', 'Top'
        :return:
        """
        self.log_root.desc = name

    def get_passrate(self):
        cnt_pass = self.log_root.get_passed_num()
        cnt_total = self.log_root.get_total_num()
        return cnt_pass / cnt_total

    def add_group(self, group_desc='untitled_group'):
        self.log_root.children.append(LoggerTreeNode(1, group_desc))
        self.current_group = self.log_root.children[-1]
        self.current_group.level_name = get_level_name(1)
        self.current_unit = None
        self.current_element = None
        self.current_case = None

    def add_unit(self, unit_desc='untitled_unit'):
        if self.current_group is None:
            self.add_group()

        self.current_group.children.append(LoggerTreeNode(2, unit_desc))
        self.current_unit = self.current_group.children[-1]
        self.current_unit.level_name = get_level_name(2)
        self.current_element = None
        self.current_case = None

    def add_element(self, element_desc='untitled_element'):
        if self.current_unit is None:
            self.add_unit()

        self.current_unit.children.append(LoggerTreeNode(3, element_desc))
        self.current_element = self.current_unit.children[-1]
        self.current_element.level_name = get_level_name(3)
        self.current_case = None

    def add_case(self, case_desc='untitled_case'):
        if self.current_element is None:
            self.add_element()

        self.current_element.children.append(LoggerTreeNode(4, case_desc))
        self.current_case = self.current_element.children[-1]
        self.current_case.level_name = 'Test_Case'
        self.current_case.start_timing()

    def insert_fake_pytest_nodeid(self, nodeid):
        # parse pytest nodeid like:
        # "GBuilder_Auto_Tcase.py::TestGBuilder_newSection::()::TestAlexnet::()::test_Alexnet_models"
        root, _ = re.split('::', nodeid, 1)
        tail = re.match('.*(\[.+\])$', nodeid)
        nodes = re.findall('[:](\w+)', nodeid)

        if tail is not None:
            node_list = nodes + [tail[1]]
        else:
            node_list = nodes

        # got root and node list:
        if self.log_root.desc == 'untitled_logger':
            self.log_root.desc = root
        # log_root.desc is module name
        current_father = self.log_root
        level = 0
        for node in node_list:
            if level <= 4:
                current_father.level_name = get_level_name(level)
            else:
                current_father.level_name = 'Untitled'  # + str(level)

            level += 1
            # if current_father.children == [] or current_father.children[-1].desc != node:
            if node in current_father.children:
                index = current_father.children.index(node)
                current_father = current_father.children[index]
                pass
            else:
                current_father.children.append(LoggerTreeNode(level, node))
                current_father = current_father.children[-1]

        self.current_case = current_father
        self.current_case.level_name = 'Test_Case'
        self.current_case.start_timing()

    def append_pytest_report(self, report):

        if report.passed and report.when == "call":
            result = Result.passed
        elif report.failed:
            result = Result.failed
        else:
            return

        nodeid = report.nodeid

        # parse pytest nodeid:
        root, _ = re.split('::', nodeid, 1)
        tail = re.match('.*(\[.+\])$', nodeid)
        nodes = re.findall('[:](\w+)', nodeid)

        if tail is not None:
            node_list = nodes + [tail[1]]
        else:
            node_list = nodes

        # got root and node list:
        if self.log_root.desc == 'untitled_logger':
            self.log_root.desc = root
        # log_root.desc is module name
        current_father = self.log_root
        level = 0
        total_level = len(node_list)
        for node in node_list:
            if level <= 4:
                current_father.level_name = get_level_name(level)
            else:
                current_father.level_name = 'Untitled'  # + str(level)

            level += 1
            # if current_father.children == [] or current_father.children[-1].desc != node:
            if node in current_father.children:
                index = current_father.children.index(node)
                current_father = current_father.children[index]
                pass
            else:
                current_father.children.append(LoggerTreeNode(level, node))
                current_father = current_father.children[-1]

        self.current_case = current_father
        self.current_case.level_name = 'Test_Case'
        self.current_case.result = result
        self.current_case.set_duration(getattr(report, "duration", 0.0))

        # add log
        # for line in report.longreprtext.splitlines():
        #     self.current_case.logs.append(line)
            # exception = line.startswith("E   ")
            # if exception:
            #     line = line[1:]
            #     self.current_case.logs.append('[Error 2]' + line)
        # self.current_case.start_timing()

        step = 0
        for line in report.capstdout.splitlines():
            if re.match('\[.+\].+', line):
                if re.match('\[Step\].+', line):
                    step += 1
                    line = "[Step %d]" % step + line[6:]
                self.current_case.logs.append(line)

        if hasattr(report, 'longrepr') and hasattr(report.longrepr, 'reprcrash'):
            e_mst = "[Error] %s:%d: %s" % (
                report.longrepr.reprcrash.path,
                report.longrepr.reprcrash.lineno,
                report.longrepr.reprcrash.message,
            )
            self.current_case.logs.append(e_mst)

    @staticmethod
    def add_step(step):
        print('[Step]', step)
        # if self.current_case is None:
        #     self.add_case()
        # self.current_case.add_step(step)

    @staticmethod
    def add_comment(comment):
        print('[Comment]', comment)
        #
        # if self.current_case is None:
        #     self.add_case()
        # self.current_case.add_comment(comment)

    @staticmethod
    def add_error(error, is_exception):
        print('[Error]', error)
        # if self.current_case is None:
        #     self.add_case()
        # self.current_case.add_error(error, is_exception)

    @staticmethod
    def set_expect(expect):
        print('[Expect]', expect)
        # if self.current_case is None:
        #     self.add_case()
        # self.current_case.set_expect(expect)

    def set_result(self, result: bool):
        if self.current_case is None:
            self.add_case()
        if result:
            self.current_case.result = Result.passed
        else:
            self.current_case.result = Result.failed
        self.current_case.end_timing()

    def get_result(self):
        if self.current_case is None:
            self.add_case()
        return Result.passed == self.current_case.result

    def end_record(self):
        pass

    def __str__(self):
        # lines = self.log_root.get_tree_str_list(node_flag='', stop_level=self.print_level)
        lines = self.log_root.get_tree_str_list(node_flag='')
        s = ''
        for line in lines:
            s += line + '\n'
        return s

    def set_print_level(self, level):
        # """
        # :param level:-1(defalut) print all, 0:Logger 1:Module 2:Unit 3:Group 4:Case
        # """
        # assert isinstance(level, int), "input a int level"
        if level == -1 or level == 'All':
            self.print_level_str = 'All'
            self.print_level = -1
        elif level == 0 or level == 'Test_Logger':
            self.print_level_str = 'Test_Logger'
            self.print_level = 0
        elif level == 1 or level == 'Test_Group':
            self.print_level_str = 'Test_Group'
            self.print_level = 1
        elif level == 2 or level == 'Test_Unit':
            self.print_level_str = 'Test_Unit'
            self.print_level = 2
        elif level == 3 or level == 'Test_Element':
            self.print_level_str = 'Test_Element'
            self.print_level = 3
        elif level == 4 or level == 'Test_Case':
            self.print_level_str = 'Test_Case'
            self.print_level = -1
            pass
        else:
            pass

    def to_txt(self, path):
        generated = datetime.datetime.now()
        head = "Module_Name: %s\n" % self.log_root.desc
        head += "Generated_Time: %s at %s\n" % (generated.strftime("%d-%b-%Y"), generated.strftime("%H-%M-%S"))
        head += "Result: Total_Passrate {:.2f}%, " \
                "Total {}, " \
                "Failed {}, " \
                "Passed {}, " \
                "Total_Time {:.3f}s\n".format(\
                self.log_root.get_passrate_on_level(self.print_level) * 100,\
                self.log_root.get_total_num_on_level(self.print_level),\
                self.log_root.get_total_num_on_level(self.print_level) - self.log_root.get_passed_num_on_level(self.print_level),\
                self.log_root.get_passed_num_on_level(self.print_level),
                self.log_root.get_duration_on_level(self.print_level))
        head += "Print_Level: %s\n" % self.print_level_str
        head += "\n"
        tail = "____ ____ ____ ____ ____ <END Report> ____ ____ ____ ____ ____\n"
        with open(path, 'w') as f:
            f.write(
                head + str(self) + tail
            )

    # def html(self):
    #     return self.log_root.get_tree_html()

    # def html(self):
    #     return Html_Reporter(self).html()
    #
    # def to_html(self, path):
    #     Html_Reporter(self).to_html(path)


# new a logger and keep singleton when you import it
logger = Test_Logger()