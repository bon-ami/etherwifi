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
import ctypes
from datetime import datetime
import time
import tkinter as tk
import threading
import queue
import requests
import urllib3
# import xml.etree.ElementTree as ET
import ewcust

EN = 'Enabled'
DA = 'Disabled'
CO = 'Connected'
DC = 'Disconnected'
CFG_DEF = 'etherwifi_def.xml'
CFG_CUST = 'etherwifi_cust.xml'

def get_cfg1(cfg_file):
    """ get one config file """
    gui_print(cfg_file)

def get_cfgs():
    '''get configurations'''
    for cfg_file in [CFG_DEF, CFG_CUST]:
        if os.path.exists(cfg_file) and os.path.isfile(cfg_file):
            get_cfg1(cfg_file)

def interfaces_get():
    '''get interfaces'''
    my_cmd = 'netsh interface show interface'
    conn_res = os.popen(my_cmd).read()
    # gui_print(conn_res)
    res = {}
    headers = True
    for line in str.splitlines(conn_res):
        # gui_print(headers, line)
        if headers:
            if re.match(r'-+', line):
                headers = False
            else:
                continue
        elif not re.match(r'.+', line):
            continue
        eles = re.split(r'\W+', line, 3)
        if len(eles) < 4:
            continue
        if re.match(re.escape(CMD_STRS['w']) + r'.*', eles[3]):
            res['w'] = eles
        elif re.match(re.escape(CMD_STRS['e']) + r'.*', eles[3]):
            res['e'] = eles
        else:
            gui_print(eles[3] + "NOT recognized as an interface")
    return res

def intf_dis_connect_wifi_chk(interfaces, connect):
    '''check whether action needed for (dis-)connection'''
    intf = interfaces['w']
    if intf is None:
        gui_print("NO WIFI interface found!")
        return [True, intf]
    if connect:
        if intf[0] == EN and intf[1] == CO:
            gui_print(intf[3] + " connected.")
            return [False, intf] # still needs to connect to an AP
    else:
        if intf[0] == DA or intf[1] == DC:
            gui_print(intf[3] + " disconnected.")
            return [True, intf]
    # gui_print(intf[3], intf[0], intf[1])
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
        gui_print("NO ethernet interface found!")
        return False
    if connect:
        if intf[0] == EN and intf[1] == CO:
            gui_print(intf[3] + " connected.")
        else:
            return intf_dis_connect(intf[3], True)
    else:
        if intf[0] == DA or intf[0] == DC:
            gui_print(intf[3] + " disconnected.")
        else:
            return intf_dis_connect(intf[3], False)
    return True

def intf_dis_connect(intf, connect):
    '''(dis-)connect a network'''
    if connect:
        conn_str = "ENABLED"
    else:
        conn_str = "DISABLED"
    if not is_admin():
        # elevate()
        gui_print('Run this as administrator!')
    my_cmd = 'netsh interface set interface name="'+intf+'" admin='+conn_str
    conn_res = os.popen(my_cmd).read()
    if re.match(r'\W+', conn_res):
        gui_print(intf + conn_str)
        return True
    gui_print(conn_res)
    return False

def wifi_dis_connect(ssid, profiles, intf, connect):
    '''real action to (dis-)connect WiFi'''
    #filter out profile name
    if len(profiles) < 1:
        gui_print('No ever-connected WIFI found!')
        return False
    if profiles.find(CMD_STRS['p'] + ssid) >= 0:
        if connect:
            conn_str = "connect name="+ssid
        else:
            conn_str = 'disconnect interface="'+intf+'"'
        my_cmd = 'netsh wlan '+conn_str
        conn_res = os.popen(my_cmd).read()
        succ_str = r'Connection request was completed successfully\.'
        if re.match(r'\W+', conn_res) or re.match(succ_str, conn_res):
            if connect:
                gui_print(intf + " on")
            else:
                gui_print(intf + " off")
            return True
        gui_print(conn_res)
    else:
        gui_print('Have you ever connected to '+ssid+"?")
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
    # gui_print(pinged)
    if len(pinged) > 0 and not '(100% ' in pinged:
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
    gui_print('Authenticating...')
    time.sleep(2) # to avoid MaxRetryError
    try:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.post(url, headers=heads, data=values, verify=False)
    except (requests.exceptions.ConnectionError,
            urllib3.exceptions.MaxRetryError,
            TimeoutError, urllib3.exceptions.NewConnectionError):
        rounds += 1
        if rounds > 2:
            gui_print("Tired of trying and timing out. Giving up...")
            return False
        gui_print("Time out. Retry again. Round " + str(rounds))
        return auth_web(url, name, passwd, rounds)
    except (RuntimeError, SystemError):
        logging.exception("Please report error to author.")
        return False
    if response:
        if response.status_code != requests.codes['ok']:
            gui_print(response.status_code + response.text)
        else:
            data = response.text
            if "Login Successful" in data:
                gui_print('Authentication succeeded.')
                return True
            if '<title>Web Authentication Failure</title>' in data:
                gui_print('Server rejected our authentication, '
                          'but it was most likely a false alarm.')
                return True
            gui_print(data)
    return False

def gui_print(txt):
    '''call this to refresh GUI'''
    if Q_GUI is not None:
        Q_GUI.put(datetime.now().strftime('%M:%S') + ':' + txt)
    if WINDOW is not None:
        WINDOW.event_generate('<<MessageGenerated>>')

def gui_print_onoff(wifi, ether):
    '''debug switches'''
    switch_w = "off"
    switch_e = "off"
    if wifi:
        switch_w = "on"
    if ether:
        switch_e = "on"
    gui_print("Wi-Fi="+switch_w+",Ethernet="+switch_e)

def work_thrd(q_sub, wifi_on, ether_on):
    """ work thread """
    q_evt = '1'
    global INTERFACE_ARR
    while True: # hell mode
        if len(q_evt) > 0:
            if q_evt == 'q':
                return
            if q_evt != '1':
                wifi_on = False
                ether_on = False
                if q_evt in ('w', 'b'):
                    wifi_on = True
                if q_evt in ('e', 'b'):
                    ether_on = True
            INTERFACE_ARR = interfaces_get()
            # q_evt to be reset later
            if not intf_dis_connect_eth(INTERFACE_ARR, ether_on):
                gui_print('Ethernet failure not preventing WIFI operations...')
        try:
            q_evt = q_sub.get_nowait()
            continue
        except queue.Empty:
            q_evt = ''
            # time.sleep(ewcust.LAPSE_LP)
        # gui_print_onoff(wifi_on, ether_on)
        if not intf_dis_connect_wifi_wait(INTERFACE_ARR,
                                          ewcust.SSID_STR, wifi_on):
            gui_print('Wi-Fi off not preventing further operations...')
            # break
        q_evt = wifi_loop(q_sub, wifi_on)

def wifi_loop(q_sub, wifi_on):
    '''loop to check Internet and authenticate if needed'''
    sec_left = 0
    while True:
        try:
            q_evt = q_sub.get_nowait()
            break
        except queue.Empty:
            q_evt = ''
        if sec_left <= 0:
            if wifi_on:
                if chk_web():
                    lapse = ewcust.LAPSE_OK
                else:
                    if auth_web(ewcust.URL_STR, ewcust.NAME_STR,
                                ewcust.PASSWD_STR):
                        lapse = ewcust.LAPSE_OK
                    else:
                        lapse = ewcust.LAPSE_NG
                        break # we need to check connections again
                # if not ETHER_ON: # only loop for both wifi and ethernet
                    # break
                gui_print('Authentication check will reoccur in '
                          + str(lapse) + ' minute(s).')
                sec_left = lapse * 60
            else:
                sec_left = ewcust.LAPSE_LP * 60
        else:
            sec_left -= 1
        # to check for events, sleep 1 sec only
        time.sleep(ewcust.LAPSE_LP)
    return q_evt

def butt_click_e():
    """ethernet clicked"""
    try:
        Q_MAIN.put('e')
    except queue.Full:
        gui_print('too many commands')

def butt_click_w():
    """wifi clicked"""
    try:
        Q_MAIN.put('w')
    except queue.Full:
        gui_print('too many commands')

def butt_click_b():
    """both clicked"""
    try:
        Q_MAIN.put('b')
    except queue.Full:
        gui_print('too many commands')

def gui_update(q_sub, evt):
    """GUI updater"""
    global LBLS_BUF
    msg = q_sub.get()
    if msg == 'exit':
        LBLS["text"] = "I'm dead."
        return
    if len(LBLS_BUF) < 250:
        LBLS_BUF = LBLS_BUF+"\n"+msg
    else:
        LBLS_BUF = msg
    LBLS["text"] = LBLS_BUF

def is_admin():
    '''True if running as admin'''
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def elevate():
    '''run sth. as admin. not working.'''
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable,
                                        __file__, None, 1)

CMD_STRS = {}
CMD_STRS = ewcust.get_lang()
if len(CMD_STRS) < 3:
    print('Not enough string resource')
    sys.exit(1)
INTERFACE_ARR = interfaces_get()
WIFI_ON = ewcust.WIFI_ON
ETHER_ON = ewcust.ETHER_ON
if len(sys.argv) > 1:
    if sys.argv[1] == '-e':
        WIFI_ON = False
    elif sys.argv[1] == '-w':
        ETHER_ON = False
WINDOW = tk.Tk()
Q_MAIN = queue.Queue()
Q_GUI = queue.Queue()
LBLS = tk.Label(text="Bonjour", width=50, height=10,)
LBLS_BUF = 'etherwifi 0.1'
THRDWORK = threading.Thread(target=work_thrd,
                            args=(Q_MAIN, WIFI_ON, ETHER_ON,))
THRDWORK.start()
# GUI
BUTTB = tk.Button(master=WINDOW, command=butt_click_b,
                  text="Both", width=50, height=5,)
BUTTE = tk.Button(master=WINDOW, command=butt_click_e,
                  text="Ethernet", width=25, height=5,)
BUTTW = tk.Button(master=WINDOW, command=butt_click_w,
                  text="Wi-Fi", width=25, height=5,)
BUTTB.pack()
BUTTE.pack(side=tk.LEFT)
BUTTW.pack()
LBLS.pack()
WINDOW.bind('<<MessageGenerated>>', lambda e: gui_update(Q_GUI, e))
WINDOW.mainloop()
WINDOW = None
try:
    Q_MAIN.put('q')
except queue.Full:
    print('too many commands')
