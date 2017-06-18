# coding: utf-8
import telnetlib
import wx
from login import Login
from config.settings import *


class Application:
    def __init__(self):
        self.con = telnetlib.Telnet()
        self.con.open(Server.host, Server.port)

    def start(self):
        app = wx.App()
        frame = Login(connect=self.con)
        frame.Show()
        app.MainLoop()

if __name__ == '__main__':
    application = Application()
    application.start()
