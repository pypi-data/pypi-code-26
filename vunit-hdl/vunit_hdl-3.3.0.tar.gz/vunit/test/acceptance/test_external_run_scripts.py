# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2014-2018, Lars Asplund lars.anders.asplund@gmail.com

"""
Verify that all external run scripts work correctly
"""


import unittest
from os import environ
from os.path import join, dirname
from subprocess import call
import sys
from vunit import ROOT
from vunit.builtins import VHDL_PATH
from vunit.test.common import has_simulator, check_report, simulator_is


def simulator_supports_verilog():
    """
    Returns True if simulator supports Verilog
    """
    return simulator_is("modelsim", "incisive")


# pylint: disable=too-many-public-methods
@unittest.skipUnless(has_simulator(), "Requires simulator")
class TestExternalRunScripts(unittest.TestCase):
    """
    Verify that example projects run correctly
    """

    def test_vhdl_uart_example_project(self):
        self.check(join(ROOT, "examples", "vhdl", "uart", "run.py"))

    @unittest.skipUnless(simulator_supports_verilog(), "Verilog")
    def test_verilog_uart_example_project(self):
        self.check(join(ROOT, "examples", "verilog", "uart", "run.py"))

    @unittest.skipUnless(simulator_supports_verilog(), "Verilog")
    def test_verilog_ams_example(self):
        self.check(join(ROOT, "examples", "verilog", "verilog_ams", "run.py"))
        check_report(self.report_file,
                     [("passed", "lib.tb_dut.Test that pass"),
                      ("failed", "lib.tb_dut.Test that fail")])

    def test_vhdl_logging_example_project(self):
        self.check(join(ROOT, "examples", "vhdl", "logging", "run.py"))

    def test_vhdl_run_example_project(self):
        self.check(join(ROOT, "examples", "vhdl", "run", "run.py"), exit_code=1)
        check_report(self.report_file,
                     [("passed", "lib.tb_with_watchdog.Test to_string for boolean"),
                      ("passed", "lib.tb_standalone.Test to_string for boolean"),
                      ("passed", "lib.tb_with_test_cases.Test to_string for integer"),
                      ("passed", "lib.tb_with_test_cases.Test to_string for boolean"),
                      ("passed", "lib.tb_with_lower_level_control.Test something"),
                      ("passed", "lib.tb_with_lower_level_control.Test something else"),
                      ("passed", "lib.tb_running_test_case.Test scenario A"),
                      ("passed", "lib.tb_running_test_case.Test scenario B"),
                      ("passed", "lib.tb_running_test_case.Test something else"),
                      ("passed", "lib.tb_minimal.all"),
                      ("passed", "lib.tb_magic_paths.all"),
                      ("failed", "lib.tb_with_watchdog.Test that stalls"),
                      ("failed", "lib.tb_counting_errors.Test that fails multiple times but doesn't stop"),
                      ("failed", "lib.tb_standalone.Test that fails on VUnit check procedure"),
                      ("failed", "lib.tb_many_ways_to_fail.Test that fails on an assert"),
                      ("failed", "lib.tb_many_ways_to_fail.Test that crashes on boundary problems"),
                      ("failed", "lib.tb_many_ways_to_fail.Test that fails on VUnit check procedure")])

    def test_vhdl_third_party_integration_example_project(self):
        self.check(join(ROOT, "examples", "vhdl", "third_party_integration", "run.py"), exit_code=1)
        check_report(self.report_file,
                     [("passed", "lib.tb_external_framework_integration.Test that pass"),
                      ("failed",
                       "lib.tb_external_framework_integration.Test that stops the simulation on first error"),
                      ("failed",
                       "lib.tb_external_framework_integration.Test that doesn't stop the simulation on error")])

    def test_vhdl_check_example_project(self):
        self.check(join(ROOT, "examples", "vhdl", "check", "run.py"))

    def test_vhdl_generate_tests_example_project(self):
        self.check(join(ROOT, "examples", "vhdl", "generate_tests", "run.py"))
        check_report(self.report_file,
                     [("passed", "lib.tb_generated.data_width=1,sign=False.Test 1"),
                      ("passed", "lib.tb_generated.data_width=1,sign=True.Test 1"),
                      ("passed", "lib.tb_generated.data_width=2,sign=False.Test 1"),
                      ("passed", "lib.tb_generated.data_width=2,sign=True.Test 1"),
                      ("passed", "lib.tb_generated.data_width=3,sign=False.Test 1"),
                      ("passed", "lib.tb_generated.data_width=3,sign=True.Test 1"),
                      ("passed", "lib.tb_generated.data_width=4,sign=False.Test 1"),
                      ("passed", "lib.tb_generated.data_width=4,sign=True.Test 1"),
                      ("passed", "lib.tb_generated.data_width=16,sign=True.Test 2")])

    def test_vhdl_composite_generics_example_project(self):
        self.check(join(ROOT, "examples", "vhdl", "composite_generics", "run.py"))
        check_report(self.report_file,
                     [("passed", "tb_lib.tb_composite_generics.VGA.Test 1"),
                      ("passed", "tb_lib.tb_composite_generics.tiny.Test 1")])

    def test_vhdl_json4vhdl_example_project(self):
        self.check(join(ROOT, "examples", "vhdl", "json4vhdl", "run.py"))

    def test_vhdl_array_example_project(self):
        self.check(join(ROOT, "examples", "vhdl", "array", "run.py"))

    def test_vhdl_array_axis_vcs_example_project(self):
        self.check(join(ROOT, "examples", "vhdl", "array_axis_vcs", "run.py"))

    def test_vhdl_axi_dma_example_project(self):
        self.check(join(ROOT, "examples", "vhdl", "axi_dma", "run.py"))

    def test_vhdl_user_guide_example_project(self):
        self.check(join(ROOT, "examples", "vhdl", "user_guide", "run.py"), exit_code=1)
        check_report(self.report_file,
                     [("passed", "lib.tb_example.all"),
                      ("passed", "lib.tb_example_many.test_pass"),
                      ("failed", "lib.tb_example_many.test_fail")])

    @unittest.skipUnless(simulator_supports_verilog(), "Verilog")
    def test_verilog_user_guide_example_project(self):
        self.check(join(ROOT, "examples", "verilog", "user_guide", "run.py"), exit_code=1)
        check_report(self.report_file,
                     [("passed", "lib.tb_example_basic.all"),
                      ("passed", "lib.tb_example.Test that a successful test case passes"),
                      ("failed", "lib.tb_example.Test that a failing test case actually fails"),
                      ("failed", "lib.tb_example.Test that a test case that takes too long time fails with a timeout")])

    def test_vhdl_com_example_project(self):
        self.check(join(ROOT, "examples", "vhdl", "com", "run.py"))

    def test_array_vhdl_2008(self):
        self.check(join(VHDL_PATH, "array", "run.py"))

    def test_data_types_vhdl_2008(self):
        self.check(join(VHDL_PATH, "data_types", "run.py"))

    def test_data_types_vhdl_2002(self):
        self.check(join(VHDL_PATH, "data_types", "run.py"),
                   vhdl_standard="2002")

    def test_data_types_vhdl_93(self):
        self.check(join(VHDL_PATH, "data_types", "run.py"),
                   vhdl_standard="93")

    def test_random_vhdl_2008(self):
        self.check(join(VHDL_PATH, "random", "run.py"))

    def test_verification_components_vhdl_2008(self):
        self.check(join(VHDL_PATH, "verification_components", "run.py"))

    def test_check_vhdl_2008(self):
        self.check(join(VHDL_PATH, "check", "run.py"))

    def test_check_vhdl_2002(self):
        self.check(join(VHDL_PATH, "check", "run.py"),
                   vhdl_standard='2002')

    def test_check_vhdl_93(self):
        self.check(join(VHDL_PATH, "check", "run.py"),
                   vhdl_standard='93')

    def test_logging_vhdl_2008(self):
        self.check(join(VHDL_PATH, "logging", "run.py"))

    def test_logging_vhdl_2002(self):
        self.check(join(VHDL_PATH, "logging", "run.py"),
                   vhdl_standard='2002')

    def test_logging_vhdl_93(self):
        self.check(join(VHDL_PATH, "logging", "run.py"),
                   vhdl_standard='93')

    def test_run_vhdl_2008(self):
        self.check(join(VHDL_PATH, "run", "run.py"))

    def test_run_vhdl_2002(self):
        self.check(join(VHDL_PATH, "run", "run.py"),
                   vhdl_standard='2002')

    def test_run_vhdl_93(self):
        self.check(join(VHDL_PATH, "run", "run.py"),
                   vhdl_standard='93')

    def test_string_ops_vhdl_2008(self):
        self.check(join(VHDL_PATH, "string_ops", "run.py"))

    def test_string_ops_vhdl_2002(self):
        self.check(join(VHDL_PATH, "string_ops", "run.py"),
                   vhdl_standard='2002')

    def test_string_ops_vhdl_93(self):
        self.check(join(VHDL_PATH, "string_ops", "run.py"),
                   vhdl_standard='93')

    def test_dictionary_vhdl_2008(self):
        self.check(join(VHDL_PATH, "dictionary", "run.py"))

    def test_dictionary_vhdl_2002(self):
        self.check(join(VHDL_PATH, "dictionary", "run.py"),
                   vhdl_standard='2002')

    def test_dictionary_vhdl_93(self):
        self.check(join(VHDL_PATH, "dictionary", "run.py"),
                   vhdl_standard='93')

    def test_path_vhdl_2008(self):
        self.check(join(VHDL_PATH, "path", "run.py"))

    def test_path_vhdl_2002(self):
        self.check(join(VHDL_PATH, "path", "run.py"),
                   vhdl_standard='2002')

    def test_path_vhdl_93(self):
        self.check(join(VHDL_PATH, "path", "run.py"),
                   vhdl_standard='93')

    def test_com_vhdl_2008(self):
        self.check(join(VHDL_PATH, "com", "run.py"))

    def setUp(self):
        self.output_path = join(dirname(__file__), "external_run_out")
        self.report_file = join(self.output_path, "xunit.xml")

    def check(self, run_file, args=None, vhdl_standard='2008', exit_code=0):
        """
        Run external run file and verify exit code
        """
        args = args if args is not None else []
        new_env = environ.copy()
        new_env["VUNIT_VHDL_STANDARD"] = vhdl_standard
        retcode = call([sys.executable, run_file,
                        "--clean",
                        "--output-path=%s" % self.output_path,
                        "--xunit-xml=%s" % self.report_file] + args,
                       env=new_env)
        self.assertEqual(retcode, exit_code)
