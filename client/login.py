# coding: utf-8
import wx
from wx import adv
import telnetlib
import re
from config.settings import *
from chatroom import ChatRoom

r = re.compile('^[A-Za-z0-9-_]+$')


class Login(wx.Frame):
    def __init__(self, connect, splash_screen=True):
        wx.Frame.__init__(self, parent=None, id=-1,
                          title=u'帐号登录', size=(300, 450))
        self.con = connect
        self.initialize(splash_screen)
        self.Show()

    def initialize(self, splash_screen):
        """ hook for class initialization """
        self.set_splash_screen(splash_screen)
        self.panel = wx.Panel(self, -1)
        self.Centre()
        head_img = wx.Image(IMG.head_img, wx.BITMAP_TYPE_ANY).Scale(180, 140)
        wx.StaticBitmap(self.panel, -1, wx.Bitmap(head_img), pos=(50, 30))
        wx.StaticText(self.panel, -1, u'账号', pos=(70, 182))
        wx.StaticText(self.panel, -1, u'密码', pos=(70, 222))
        # 设置账号输入文本框以及密码输入文本框
        self.user = wx.TextCtrl(self.panel, -1, u'', pos=(100, 180))
        self.password = wx.TextCtrl(self.panel, -1, u'', style=wx.TE_PASSWORD, pos=(100, 220))
        self.set_button()

    @classmethod
    def set_splash_screen(cls, splash_screen):
        """ 设置启动画面 """
        if splash_screen:
            # 设置启动画面
            start_img = wx.Image(IMG.start_img, wx.BITMAP_TYPE_ANY).\
                Scale(350, 450)
            adv.SplashScreen(
                wx.Bitmap(start_img),
                adv.SPLASH_CENTRE_ON_SCREEN | adv.SPLASH_TIMEOUT,
                1500, None, -1)
            wx.Yield()

    def set_button(self):
        """ 设置并绑定登录按钮和注册按钮 """
        # 登录按钮
        self.btn_login = wx.Button(self.panel, label=u'登录',
                                   pos=(75, 260), size=(60, 30))
        # 注册按钮
        self.btn_register = wx.Button(self.panel, label=u'注册',
                                      pos=(175, 260), size=(60, 30))
        # 绑定单击事件
        self.Bind(wx.EVT_BUTTON, self.login, self.btn_login)
        self.Bind(wx.EVT_BUTTON, self.register, self.btn_register)
        self.Bind(wx.EVT_CLOSE, self.close)

    # 登录按钮：连接服务器，登录
    def login(self, event):
        if len((self.user.GetValue()).strip()) > 0 and len((self.password.GetValue()).strip()) > 0:
            login = 'login:{0}:{1}\n'.format(self.user.GetValue(), self.password.GetValue())
            login = login.encode('gbk')
            self.con.write(login)
            response = self.con.read_some()
            response = response.decode('gbk')
            if response == 'Success':
                # 跳转到聊天界面
                ChatRoom(self.user.GetValue(), self.con)
                self.Destroy()
            elif response == 'Error':
                self.msg_dialog(message=u'密码不正确')
            else:
                self.msg_dialog(message=u'用户不存在')
        else:
            self.msg_dialog(message=u'账号密码不能为空')

    # 跳转到注册界面
    def register(self, event):
        Register(connect=self.con)
        self.Destroy()

    # 信息提示对话框
    def msg_dialog(self, message):
        dlg = wx.MessageDialog(self, message, '提示',
                               wx.OK | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()

    def close(self, event):
        """ 关闭窗口，断开连接 """
        self.con.close()
        exit()


# 注册界面
class Register(wx.Frame):
    def __init__(self, connect):
        wx.Frame.__init__(self, parent=None, id=-1, title=u'帐号注册',
                          size=(300, 450))
        self.con = connect
        self.initialize()
        self.Show()

    def initialize(self):
        """ hook for class initialization """
        self.panel = wx.Panel(self, -1)
        self.Centre()
        head_img = wx.Image(IMG.head_img, wx.BITMAP_TYPE_ANY).Scale(180, 140)
        wx.StaticBitmap(self.panel, -1, wx.Bitmap(head_img), pos=(50, 30))
        wx.StaticText(self.panel, -1, u'账号', pos=(70, 182))
        wx.StaticText(self.panel, -1, u'密码', pos=(70, 222))
        # 账号输入文本框和密码输入文本框
        self.user = wx.TextCtrl(self.panel, -1, u'', pos=(100, 180))
        self.password = wx.TextCtrl(self.panel, -1, u'',
                                    style=wx.TE_PASSWORD, pos=(100, 220))
        self.set_button()

    def set_button(self):
        """ 设置并绑定返回按钮和注册按钮 """
        # 返回按钮
        self.btn_back = wx.Button(self.panel, label=u'返回',
                                 pos=(75, 260), size=(60, 30))
        # 注册按钮
        self.btn_register = wx.Button(self.panel, label=u'注册',
                                     pos=(175, 260), size=(60, 30))
        self.Bind(wx.EVT_BUTTON, self.back, self.btn_back)
        self.Bind(wx.EVT_BUTTON, self.register, self.btn_register)
        self.Bind(wx.EVT_CLOSE, self.close)

    # 销毁当前界面，返回登录界面
    def back(self, event):
        Login(connect=self.con, splash_screen=False)
        self.Destroy()

    # 注册按钮要实现的事件，连接服务器注册
    def register(self, event):
        # 输入的账号
        user_in = self.user.GetValue()
        # 输入的密码
        password_in = self.password.GetValue().strip()
        if not r.match(user_in):
            self.msg_dialog(message=u'账号只能由字母、数字、-和_组成')
        else:
            if len(user_in) > 0 and len(password_in) > 0:
                # self.Res_MesDialog(message=u'注册成功')
                register = 'register:{0}:{1}\n'.format(self.user.GetValue(), self.password.GetValue())
                register = register.encode('utf-8')
                self.con.write(register)
                response = self.con.read_some()
                response = response.decode('utf-8')
                if response == 'Existed':
                    self.msg_dialog(message=u'用户已存在')
                else:
                    self.msg_dialog(message=u'注册成功')
                    Login(connect=self.con, splash_screen=False)
                    self.Destroy()
            else:
                self.msg_dialog(message=u'账号密码不能为空')

    def msg_dialog(self, message):
        dlg = wx.MessageDialog(self, message, '提示',
                               wx.OK | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()

    def close(self, event):
        """ 关闭窗口，断开连接 """
        self.con.close()
        exit()
