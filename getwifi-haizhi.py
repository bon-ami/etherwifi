#codingutf-8
import os
import re
import sys
import time
from selenium import webdriver
import requests

wiredipaddr=''
wirelessipaddr=''

def setLanRoute(str):
    r = os.popen(str)
    info = r.readlines()
    print("len", len(info))
    print(info)
    while (len(info) != 1):
        r = os.popen(str)
        time.sleep(1)
        info = r.readlines()
        print(info)

# 设置route函数,输入为内网有线ip
def setLANroute(ipaddr):
    print("setLANroute for " + ipaddr)
    os.popen('route delete 0.0.0.0')
    os.popen('route delete 0.0.0.0')
    os.popen('route delete 10.0.0.0')
    os.popen('route delete 192.168.1.1')
    os.popen('route delete 192.168.1.0')
    os.popen('route delete 224.0.0.0')
    # os.popen('route add 192.168.1.1 mask 255.255.255.255  '+ ipaddr +  ' if '+ '12')
    os.popen('route add 192.168.1.1 mask 255.255.255.255  '+ ipaddr +  ' if '+ '12')
    os.popen('ipconfig /flushdns')
    # os.popen('route add 224.0.0.0 mask 240.0.0.0  '+ ipaddr + ' if '+ '12')
    # os.popen('route add 10.0.0.0 mask 255.0.0.0 '+ ipaddr + ' if '+ '12')
    # os.popen('route add 192.168.1.0 mask 255.255.255.0 '+ ipaddr + ' if '+ '12')
    # setLanRoute('route add 192.168.1.0 mask 255.255.255.0 '+ ipaddr + ' if '+ '12')
    # setLanRoute('route add 224.0.0.0 mask 240.0.0.0  192.168.1.1 if '+ '12')
    # setLanRoute('route add 10.0.0.0 mask 255.0.0.0 192.168.1.1 if '+ '12')
    if ipaddr.find("10.75.") != -1:
        print("Add route for 10.75")
        setLanRoute('route add 224.0.0.0 mask 240.0.0.0  10.75.10.1 if '+ '12')
        setLanRoute('route add 10.0.0.0 mask 255.0.0.0 10.75.10.1 if '+ '12')
        print("Add route for 10.75 end")
    else:
        print("Add route for 192.168")
        setLanRoute('route add 224.0.0.0 mask 240.0.0.0  192.168.1.1 if '+ '12')
        setLanRoute('route add 10.0.0.0 mask 255.0.0.0 192.168.1.1 if '+ '12')
        setLanRoute('route add 192.168.1.0 mask 255.255.255.0 192.168.1.1 if '+ '12')
        print("Add route for 192.168 end")

    r = os.popen('route add 0.0.0.0 mask 0.0.0.0 '+ ipaddr + ' if '+ '12')
    info = r.readlines()
    print("len", len(info))
    print(info)
    while (len(info) != 1):
        r = os.popen('route add 0.0.0.0 mask 0.0.0.0 '+ ipaddr + ' if '+ '12')
        info = r.readlines()
        print("len", len(info))
        print(info)
        time.sleep(1)


# 设置route函数,输入为外网无线ip
def setWLANroute(ipaddr):
    print("setWLANroute for " + ipaddr)
    os.popen('route delete 1.1.1.1')
    os.popen('route delete 8.8.8.8 ')
    os.popen('route delete 4.2.2.2')
    r = os.popen('route change 0.0.0.0 mask 0.0.0.0  '+ ipaddr )
    info = r.readlines()
    print("len", len(info))
    print(info)
    while (len(info) != 1):
        r = os.popen('route change 0.0.0.0 mask 0.0.0.0  '+ ipaddr )
        time.sleep(1)
        info = r.readlines()
        print(info)
    os.popen('route add 1.1.1.1 mask 255.255.255.255  '+ ipaddr)
    os.popen('route add 8.8.8.8 mask 255.255.255.255  '+ ipaddr)
    os.popen('route add 4.2.2.2 mask 255.255.255.255  '+ ipaddr)

# 查找ip
wlanipaddr = '0'
def getipaddr():
    a_config=os.popen('ipconfig')
    s_config=a_config.read()
    c_config=re.findall('   IPv4 Address. . . . . . . . . . . :(.*?)\n',s_config,re.S)
    print(c_config)

    lanipaddr = '0'
    global wlanipaddr
    wlanipaddr = '0'
    for i in c_config:
        if i.find("192.168.1.") != -1:
            print("lanipaddr "+i)
            lanipaddr = i
            break
        if i.find("10.75.") != -1:
            print("lanipaddr "+i)
            lanipaddr = i
            break

    for i in c_config:
        if i.find("172.31.") != -1 :
            print("wlanipaddr ip allocated： " + i )
            wlanipaddr = i
        elif i.find("172.26.") != -1 :
            print("wlanipaddr ip allocated： " + i )
            wlanipaddr = i
    return lanipaddr, wlanipaddr


# 连接
def connectWIFI():
    os.popen('netsh wlan disconnect')
    print('connect AP ....')
    os.popen('netsh wlan connect AP')
    time.sleep(3)
    print('get IPaddress')
    global wiredipaddr
    global wirelessipaddr
    wiredipaddr, wirelessipaddr = getipaddr()

    count = 0
    while (count < 10):
        if wirelessipaddr.find("172.") != -1 and (wiredipaddr.find("10.75.") or wiredipaddr.find("192.168.1.")):
            print("set route")
            setLANroute(wiredipaddr)
            setWLANroute(wirelessipaddr)
            break
        else:
            time.sleep(2)
            count = count + 1
            print('Waiting IPaddress ...', count)
            wiredipaddr, wirelessipaddr = getipaddr()
    if(count == 10):
        print("ip not allocated !!! exit!!")
        sys.exit()

"""
print('check IPaddress')
if wirelessipaddr.find("172.31.") != -1 and wiredipaddr.find("10.75."):
    print("set route")
    setLANroute(wiredipaddr)
    setWLANroute(wirelessipaddr)
else:
    print("ip not allocated, wait 5 seconds")
    time.sleep(10)
    print('get IPaddress again')
    wiredipaddr, wirelessipaddr = getipaddr()
    print('check IPaddress again')
    if wirelessipaddr.find("172.31.") != -1 and wiredipaddr.find("10.75."):
        print("set route again")
        setLANroute(wiredipaddr)
        setWLANroute(wirelessipaddr)
    else:
        print("ip not allocated again")
        exit(-1)
"""
# 输入验证
def enterPassword():
    browser = webdriver.Chrome()
    #browser = webdriver.HtmlUnitDriver()
    r = browser.get('https://1.1.1.1/login.html') #像目标url地址发送get请求，返回一个response对象
    #print(browser.page_source)
    input_username = browser.find_element_by_name("username")
    input_username.clear()  #清空搜索框中的内容
    input_username.send_keys("user")  #在搜索框中输入**user**
    input_password = browser.find_element_by_name("password")
    input_password.clear()  #清空搜索框中的内容
    input_password.send_keys("pass")  #在搜索框中输入**pass**
    button_submit = browser.find_element_by_name("Submit")
    button_submit.click() #相当于回车键，提交
    #browser.close()
    browser.quit()
def reroute(len_0):
    print("rerouting....")
    os.popen('route delete 0.0.0.0')
    while(len_0 !=0 ):
        route_r = os.popen('route print 0.0.0.0 ')
        route_str=route_r.read()
        route_c=re.findall('0.0.0.0          0.0.0.0(.*)',route_str)
        len_0 = len(route_c)
        print("wait for zero....")
        time.sleep(1)
    global wirelessipaddr
    r = os.popen('route add 0.0.0.0 mask 0.0.0.0  '+ wirelessipaddr )
    info = r.readlines()
    print("len", len(info))
    print(info)
    while (len(info) != 1):
        r = os.popen('route add 0.0.0.0 mask 0.0.0.0  '+ wirelessipaddr )
        info = r.readlines()
        print("len", len(info))
        print(info)
        time.sleep(1)
def main_loop():
    global wlanipaddr
    while True:
        print(time.strftime('%Y-%m-%d %H:%M:%S----',time.localtime(time.time()))+wlanipaddr)
        time.sleep(30)
        exit_code = os.system('ping -n 1 -w 1000 www.baidu.com')
        if exit_code:
            route_r = os.popen('route print 0.0.0.0 ')
            route_str=route_r.read()
            route_c=re.findall('0.0.0.0          0.0.0.0(.*)',route_str)
            len_0 = len(route_c)
            if len_0 > 1 :
                reroute(len_0)
                continue
            print("Disconnected, reconnect....")
            try:
                connectWIFI()
                enterPassword()
            except Exception as err:
                print("Something went wrong!")
                print(err)
            finally:
                print("Next loop!")


connectWIFI()
enterPassword()
main_loop()
print("test run ok")

sys.exit()
