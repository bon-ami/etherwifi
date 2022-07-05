# EtherWi-Fi standalone

getwifi-haizhi.py is a standalone python from Haizhi. It integrates route setting and uses easier web page interaction, which probably supports non-Cisco AP's and is a better sulotion.
Change "user" and "pass" in the file to authenticate from AP.
No GUI, however.

# EtherWi-Fi classic

## Overal introduction
For Windows ONLY.
etherwifi.py connects Wi-Fi and Ethernet, periodically logging in. Different AP's require different portal. This method to handle web page based on Cisco probably does not work for you.
Administrator needed to disable or enable interfaces.
In GUI, choose to enable one of these networks, or both. When both used, routes should be configured on users' own.

## Configurations in code
Currently ewcust stores all these. To be stored in xml in the future.
- SSID_STR SSID string
- LAPSE_OK minutes for Wi-Fi check after a successful login
- LAPSE_NG minutes for Wi-Fi check after a failed login
- LAPSE_LP seconds between each loop to check for events
- ETHER_ON default Ethernet on. True or False
- Wi-Fi_ON default Wi-Fi on. True or False
- URL_STR Wi-Fi portal address
- NAME_STR portal username
- PASSWD_STR portal password
- PING_ADDR address to ping

## Run time parameters, obsolete
Since GUI is used, these parameters are not useful.
- no parameters to enable both and log in periodically
- -e to switch from Wi-Fi to Ethernet
- -w to switch from Ethernet to Wi-Fi

## Python->EXE
<p>etherwifi.py needs Python 3
<p>Run "pyinstaller etherwifi.py" to pack this to exe with a folder
<p>Run previous command with "-y", or "auto-py-to-exe" to pack a standalone exe
