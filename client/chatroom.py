# coding: utf-8
import wx
import _thread
from time import sleep


class ChatRoom(wx.Frame):
    def __init__(self, user, connect):
        wx.Frame.__init__(self, parent=None, id=-1, title=u'多人聊天室',
                          size=(500, 600))
        self.user = user
        self.con = connect
        self.initialize()
        _thread.start_new_thread(self.receive_msg, ())
        self.Show()

    def initialize(self):
        """ hook for class initialization"""
        # 连接服务器所读到的成员列表
        self.members = []
        # 在线总人数提示消息
        self.panel = wx.Panel(self, -1)
        self.Centre()
        # 聊天发送窗口
        self.msg_send_text = wx.TextCtrl(
            self.panel, -1, u'', style=wx.TE_MULTILINE,
            size=(438, 120))
        # 接收窗口
        self.showtext = wx.TextCtrl(
            self.panel, -1, u'',
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH,
            size=(438, 280))
        # 显示广播的用户登录或退出聊天室信息
        self.member_status = wx.TextCtrl(
            self.panel, -1, u'',
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH,
            size=(195, 205))
        # 在线成员展示窗口
        self.members_box = wx.ListBox(self.panel, -1, choices=self.members,
                                      style=wx.LB_SINGLE | wx.LB_SORT,
                                      size=(195, 200))
        self.online = u' 当前在线成员 : {0}'.format(self.members_box.GetCount())
        self.online_text = wx.StaticText(self.panel, -1, self.online)

        self.set_button()
        self.set_layout()

    def set_button(self):
        """ 设置并绑定发送消息按钮和关闭窗口按钮 """
        # 发送按钮
        self.btn_send = wx.Button(self.panel, label=u'发   送',
                                     size=(70, 27))
        # 关闭按钮
        self.btn_close = wx.Button(self.panel, label=u'退   出',
                                      size=(70, 27))
        # 绑定按钮
        self.Bind(wx.EVT_BUTTON, self.send_msg, self.btn_send)
        self.Bind(wx.EVT_BUTTON, self.exit_room, self.btn_close)
        self.Bind(wx.EVT_CLOSE, self.exit_room)

    def set_layout(self):
        """ 基于GridBagSizer布局，一些窗口缩放比例相关的 """
        gridBagSizerAll = wx.GridBagSizer(hgap=0, vgap=5)
        gridBagSizerAll.Add(self.showtext, pos=(0, 0),
                            flag=wx.ALL | wx.EXPAND, span=(11, 12), border=0)
        gridBagSizerAll.Add(self.msg_send_text, pos=(12, 0),
                            flag=wx.ALL | wx.EXPAND, span=(4, 12), border=0)
        gridBagSizerAll.Add(self.btn_send, pos=(16, 8),
                            flag=wx.ALL | wx.EXPAND, span=(1, 1), border=5)
        gridBagSizerAll.Add(self.btn_close, pos=(16, 9),
                            flag=wx.ALL | wx.EXPAND, span=(1, 1), border=5)
        gridBagSizerAll.Add(self.member_status, pos=(0, 12),
                            flag=wx.ALL | wx.EXPAND, span=(8, 4), border=0)
        gridBagSizerAll.Add(self.online_text, pos=(8, 12),
                            flag=wx.ALL | wx.EXPAND, span=(1, 4), border=0)
        gridBagSizerAll.Add(self.members_box, pos=(9, 12),
                            flag=wx.ALL | wx.EXPAND, span=(8, 4), border=5)
        self.panel.SetSizer(gridBagSizerAll)
        for i in range(16):
            gridBagSizerAll.AddGrowableCol(i, 1)
        for i in range(16):
            gridBagSizerAll.AddGrowableRow(i, 1)
        gridBagSizerAll.Fit(self)

    def exit_room(self, event):
        dlg = wx.MessageDialog(
            None, u"确定要退出聊天室吗", 'MessageDialog',
            wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        if result == wx.ID_YES:
            self.con.close()
            exit()
        dlg.Destroy()

    # 发送消息函数
    def send_msg(self, event):
        message = (self.msg_send_text.GetValue()).strip()
        if len(message) > 0:
            message = 'say:' + message + '\n'
            message = message.encode('gbk')
            self.con.write(message)
            self.msg_send_text.SetValue('')
        else:
            dlg = wx.MessageDialog(self, u'不能发送空消息', 'Caution',
                                   wx.OK | wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_OK:
                dlg.Destroy()

    def receive_msg(self):
        while True:
            sleep(0.6)
            result = self.con.read_very_eager()
            result = result.decode('gbk')
            if result != '':
                if 'login:' in result:
                    temp = result.strip('login:')
                    self.member_status.SetDefaultStyle(wx.TextAttr(wx.BLUE))
                    self.member_status.AppendText(temp)
                elif 'user_list:[' in result:
                    temp = result.strip('user_list:')
                    self.members = eval(temp)
                    print(self.members)
                    self.members_box.Set(self.members)
                    self.online = u' 当前在线成员 : {0}'.\
                        format(self.members_box.GetCount())
                    self.online_text.SetLabel(self.online)
                elif ':' not in result:
                    if 'has left the room.\n' in result:
                        self.member_status.SetDefaultStyle(
                            wx.TextAttr(wx.BLUE))
                        self.member_status.AppendText(result)
                        temp = result.replace(' has left the room.\n', '')
                        self.members.remove(temp)
                        self.members_box.Set(self.members)
                        self.online = u' 当前在线成员 : {0}'.format(
                            self.members_box.GetCount())
                        self.online_text.SetLabel(self.online)
                    else:
                        self.member_status.SetDefaultStyle(wx.TextAttr(wx.BLUE))
                        self.member_status.AppendText(result)
                else:
                    temp = result.split(':', 1)
                    if temp[0] == self.user:
                        temp[0] += ':\n'
                        self.showtext.SetDefaultStyle(wx.TextAttr(wx.RED))
                        self.showtext.AppendText(temp[0])
                    else:
                        temp[0] += ':\n'
                        self.showtext.SetDefaultStyle(wx.TextAttr(wx.BLUE))
                        self.showtext.AppendText(temp[0])
                    self.showtext.SetDefaultStyle(wx.TextAttr("BLACK"))
                    self.showtext.AppendText(temp[1])
