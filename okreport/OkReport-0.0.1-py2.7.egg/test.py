# !/usr/bin/python -u

"""
Copyright (C) 2018 LingoChamp Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from okreport.config import Config
from okreport.helper import handle_home_case
from okreport.report import Report
from sender import send_mail
from html import BASIC_REPORT_HTML, END_HTML

config_path = handle_home_case("~/.okreport")

report = Report()

report.fromConfig(config_path)
report.addParse("../reports")

BASIC_REPORT_HTML += '<h2>OkPmd</h2>\n'
BASIC_REPORT_HTML += report.getPmdChartHtmlFragment()
BASIC_REPORT_HTML += '<h2>OkFindbugs</h2>\n'
BASIC_REPORT_HTML += report.getFindbugsChartHtmlFragment()
BASIC_REPORT_HTML += '<h2>OkLint</h2>\n'
BASIC_REPORT_HTML += report.getLintChartHtmlFragment()
BASIC_REPORT_HTML += END_HTML

report.addLastConfig(config_path)
report.maintainConfigs(config_path)

config = Config(config_path + "/.config")

send_mail(BASIC_REPORT_HTML, config)
