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
"""connect WiFi and Ethernet, periodically logging in.
Administrator needed to disable or enable interfaces.
no parameters to enable both and log in periodically
-e to switch from WiFi to Ethernet
-w to switch from Ethernet to WiFi
run "pyinstaller etherwifi.py" to pack this to exe with a folder
run previous command with "-y", or "auto-py-to-exe" to pack a standalone exe
"""

import os
import re
import sys
import logging
from datetime import datetime
import time
import requests
import urllib3
import ewcust

EN = 'Enabled'
DA = 'Disabled'
CO = 'Connected'
DC = 'Disconnected'

def interfaces_get():
    '''get interfaces'''
    my_cmd = 'netsh interface show interface'
    conn_res = os.popen(my_cmd).read()
    # print(conn_res)
    res = {}
    headers = True
    for line in str.splitlines(conn_res):
        # print(headers, line)
        if headers:
            if re.match(r'-+', line):
                headers = False
            else:
                continue
        elif re.match(r'.+', line):
            eles = re.split(r'\W+', line, 3)
            if len(eles) > 3:
                if re.match(r'Wi-Fi.*', eles[3]):
                    res['w'] = eles
                elif re.match(r'Ethernet.*', eles[3]):
                    res['e'] = eles
                else:
                    print(eles[3], "NOT recognized as an interface")
    return res

def intf_dis_connect_wifi_chk(interfaces, connect):
    '''check whether action needed for (dis-)connection'''
    intf = interfaces['w']
    if intf is None:
        print("NO WIFI interface found!")
        return [True, intf]
    if connect:
        if intf[0] == EN and intf[1] == CO:
            print(intf[3], " connected.")
            return [False, intf] # still needs to connect to an AP
    else:
        if intf[0] == DA or intf[1] == DC:
            print(intf[3], " disconnected.")
            return [True, intf]
    # print(intf[3], intf[0], intf[1])
    return [False, intf]

def intf_dis_connect_wifi(intf, ssid, connect):
    '''(dis-)connect WiFi'''
    if intf is None:
        return False
    if connect: # never to disable WiFi, but to disconnect only
        intf_dis_connect(intf[3], connect)
    profiles = wifi_get_profiles()
    if wifi_dis_connect(ssid, profiles, intf[3], connect):
        return True
    return False

def intf_dis_connect_wifi_wait(interfaces, ssid, connect):
    '''disconnect WiFi or connect WiFi till connected'''
    res = intf_dis_connect_wifi_chk(interfaces, connect)
    if not res[0]:
        if not intf_dis_connect_wifi(res[1], ssid, connect):
            return False
        if connect:
            return True
        while True:
            interfaces = interfaces_get()
            res = intf_dis_connect_wifi_chk(interfaces, connect)
            if res[0] and res[1] is not None:
                return True
    return True

def intf_dis_connect_eth(interfaces, connect):
    '''(dis-)connect Ethernet'''
    intf = interfaces['e']
    if intf is None:
        print("NO ethernet interface found!")
        return False
    if connect:
        if intf[0] == EN and intf[1] == CO:
            print(intf[3], " connected.")
        else:
            return intf_dis_connect(intf[3], True)
    else:
        if intf[0] == DA or intf[0] == DC:
            print(intf[3], " disconnected.")
        else:
            return intf_dis_connect(intf[3], False)
    return True

def intf_dis_connect(intf, connect):
    '''(dis-)connect a network'''
    if connect:
        conn_str = "ENABLED"
    else:
        conn_str = "DISABLED"
    my_cmd = 'netsh interface set interface name="'+intf+'" admin='+conn_str
    conn_res = os.popen(my_cmd).read()
    if re.match(r'\W+', conn_res):
        print(intf, conn_str)
        return True
    print(conn_res)
    return False

def wifi_dis_connect(ssid, profiles, intf, connect):
    '''real action to (dis-)connect WiFi'''
    #filter out profile name
    if len(profiles) < 1:
        print('No ever-connected WIFI found!')
        return False
    if profiles.find("All User Profile     : " + ssid) >= 0:
        if connect:
            conn_str = "connect name="+ssid
        else:
            conn_str = 'disconnect interface="'+intf+'"'
        my_cmd = 'netsh wlan '+conn_str
        conn_res = os.popen(my_cmd).read()
        succ_str = r'Connection request was completed successfully\.'
        if re.match(r'\W+', conn_res) or re.match(succ_str, conn_res):
            print(intf, connect)
            return True
        print(conn_res)
    else:
        print('Have you ever connected to '+ssid+"?")
    return False

def wifi_get_profiles():
    '''get WiFi profiles'''
    my_cmd = 'netsh wlan show profile'
    # os.system(my_cmd)
    profiles = os.popen(my_cmd).read()
    return profiles

def chk_web():
    '''check whether Internet is accessible'''
    my_cmd = 'ping google.com -n 1'
    pinged = os.popen(my_cmd).read()
    # print(pinged)
    if len(pinged) > 0 and not '(100% loss)' in pinged:
        return True
    return False

def auth_web(url, name, passwd, rounds=0):
    '''authrizing portal'''
    values = {'username': name,
              'password': passwd,
              'buttonClicked': '4',
              'err_flag': '0',
              'err_msg': '',
              'info_flag': '0',
              'info_msg': '',
              'redirect_url': '',
              'network_name': 'Guest Network'}
    heads = {'Upgrade-Insecure-Requests': '1',
             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/77.0.3865.75 Safari/537.36',
             'Sec-Fetch-Mode': 'navigate',
             'Sec-Fetch-User': '?1',
             'Accept': 'text/html,application/xhtml+xml,'
                       'application/xml;q=0.9,image/webp,image/apng,'
                       '*/*;q=0.8,application/signed-exchange;v=b3',
             'Sec-Fetch-Size': 'same-origin',
             'Referer': 'https://1.1.1.1/login.html',
             'Accept-Encoding': 'gzip, deflate, br',
             'Accept-Language': 'en-US,en;q=0.9'}
    print(datetime.now(), 'Authenticating...')
    time.sleep(2) # to avoid MaxRetryError
    try:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.post(url, headers=heads, data=values, verify=False)
    except (requests.exceptions.ConnectionError,
            urllib3.exceptions.MaxRetryError,
            TimeoutError, urllib3.exceptions.NewConnectionError):
        rounds += 1
        if rounds > 2:
            print("Tired of trying and timing out. Giving up...")
            return False
        print("Time out. Retry again. Round", rounds)
        return auth_web(url, name, passwd, rounds)
    except (RuntimeError, SystemError):
        logging.exception("Please report error to author.")
        return False
    if response:
        if response.status_code != requests.codes['ok']:
            print(response.status_code, response.text)
        else:
            data = response.text
            if "Login Successful" in data:
                print('Authentication succeeded.')
                return True
            if '<title>Web Authentication Failure</title>' in data:
                print('Server rejected our authentication, but it was most '
                      'likely a false alarm.')
                return True
            print(data)
    return False

INTERFACE_ARR = interfaces_get()
WIFI_ON = ewcust.WIFI_ON
ETHER_ON = ewcust.ETHER_ON
if len(sys.argv) > 1:
    if sys.argv[1] == '-e':
        WIFI_ON = False
    elif sys.argv[1] == '-w':
        ETHER_ON = False
if not intf_dis_connect_eth(INTERFACE_ARR, ETHER_ON):
    print('Ethernet failure not preventing WIFI operations...')
while True: # hell mode
    if intf_dis_connect_wifi_wait(INTERFACE_ARR, ewcust.SSID_STR, WIFI_ON):
        # exec_post_connect(ETHER_ON, WIFI_ON)
        if WIFI_ON:
            while True:
                if chk_web():
                    LAPSE = ewcust.LAPSE_OK
                else:
                    if auth_web(ewcust.URL_STR, ewcust.NAME_STR,
                                ewcust.PASSWD_STR):
                        LAPSE = ewcust.LAPSE_OK
                    else:
                        LAPSE = ewcust.LAPSE_NG
                        break # we need to check connections again
                # if not ETHER_ON: # only loop for both wifi and ethernet
                    # break
                print('Authentication check will reoccur in',
                      LAPSE, 'minute(s).')
                time.sleep(LAPSE * 60)
    else:
        break
