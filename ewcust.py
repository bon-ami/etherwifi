# wifi
# Copyright 2019 Allen Tse
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
sensitive values
"""

import os
import re

SSID_STR = "wifissid"
LAPSE_OK = 2
LAPSE_NG = 0
LAPSE_LP = 1
ETHER_ON = True
WIFI_ON = True
URL_STR = 'https://1.1.1.1/login.html'
NAME_STR = 'user'
PASSWD_STR = 'password'

# You may also need to change following cmd_strs, if your connection names
# have been customized or your language is not listed below.
# run as my_cmd to get your language for eles[2]

def get_lang():
    '''get command results in system language'''
    cmd_strs = {}
    my_cmd = 'reg query "HKCU\\Control Panel\\International" /v sLanguage'
    conn_res = os.popen(my_cmd).read()
    for line in str.splitlines(conn_res):
        if re.match(r'sLanguage.*', line):
            eles = re.split(r'\W+', line, 3)
            if len(eles) > 2:
                if eles[2] == 'CHS':
                    cmd_strs['w'] = '无线网络连接'
                    cmd_strs['e'] = '本地连接'
                    cmd_strs['p'] = '所有用户配置文件 : '
    if len(cmd_strs) < 1: #default ENU
        cmd_strs['w'] = 'Wi-Fi'
        cmd_strs['e'] = 'Ethernet'
        cmd_strs['p'] = 'All User Profile     : '
    return cmd_strs
