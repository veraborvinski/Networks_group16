import hexchat
import os
def main():
        print("hello")
        os.chdir("miniircd-master")
        os.system("python miniircd --ipv6 --debug")
        os.chdir("~")
        os.system("pwd")
        os.startfile("C:\ProgramData\Microsoft\Windows\Start Menu\Programs\HexChat\HexChat.exe")
main()
#https://www.geeksforgeeks.org/python-os-chdir-method/
#https://stackoverflow.com/questions/14894993/running-windows-shell-commands-with-python
#https://stackoverflow.com/questions/14831716/can-i-open-an-application-from-a-script-during-runtime
