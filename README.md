# EtherWi-Fi

## Overal introduction
For Windows ONLY.
etherwifi.py connects Wi-Fi and Ethernet, periodically logging in.
Administrator needed to disable or enable interfaces.

## Configurations in code
- SSID_STR SSID string
- LAPSE_OK seconds for Wi-Fi check after a successful login
- LAPSE_NG seconds for Wi-Fi check after a failed login
- ETHER_ON default Ethernet on. True or False
- Wi-Fi_ON default Wi-Fi on. True or False
- URL_STR Wi-Fi portal address
- NAME_STR portal username
- PASSWD_STR portal password
- PING_ADDR address to ping

## Run time parameters
- no parameters to enable both and log in periodically
- -e to switch from Wi-Fi to Ethernet
- -w to switch from Ethernet to Wi-Fi

## Python->EXE
<p>etherwifi.py needs Python 3
<p>Run "pyinstaller etherwifi.py" to pack this to exe with a folder
<p>Run previous command with "-y", or "auto-py-to-exe" to pack a standalone exe
