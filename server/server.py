#-*-coding:utf8-*-  
from asyncore import dispatcher
from asynchat import async_chat
import socket, asyncore
import time

PORT = 10000 #端口 

#命令处理类
class Handler:  
    def unknown(self, session, cmd):  #响应未知命令
        session.push('Unknown command: %s\n' % cmd)  
    def handle(self, session, line): #命令处理
        line = line.decode('gbk')
        line = line.strip()
        if not line:
            return
        parts = line.split(':',1)
        cmd = parts[0]
        try:
            line = parts[1].strip()
        except IndexError:
            line = ''
        function = getattr(self, 'do_' + cmd, None)
        try:
            function(session, line)
        except TypeError:
            self.unknown(session, cmd)

#自定义会话结束时的异常
class EndSession(Exception):
    pass  


#包含多个用户的环境，负责基本的命令处理和广播
class Room(Handler): 
    def __init__(self, server):
        self.server = server
        self.sessions = []  
    def add(self, session):  #一个用户进入房间
        self.sessions.append(session) 
    def remove(self, session):         #一个用户离开房间
        self.sessions.remove(session)  
    def broadcast(self, line):      #向所有的用户发送指定消息
        for session in self.sessions:
            session.push(line.encode('gbk'))  
    def do_logout(self, session, line):  #退出房间
        raise EndSession



class LoginRoom(Room):   #刚登录的用户的房间  
    def add(self, session):
        Room.add(self, session)  
    def do_login(self, session, line):  #登录处理
        l = line.split(':',1)
        print(l)
        with open("Users.txt",'r') as f:
            users = f.readlines()
            username = []
            pswd = dict()
            for i in users:
                i = i.strip()
                k,v = i.split(':',1)
                username.append(k)
                pswd.setdefault(k,v)
            if l[0] not in username:
                     session.push(('Inexistence').encode('gbk'))
            
            elif pswd[l[0]] != l[1]:
                     session.push(('Error').encode('gbk'))            
            else:
                session.push(('Success').encode('gbk'))
                session.name = l[0]
                session.enter(self.server.main_room)
                
    def do_register(self,session,line):   #注册处理
        print('register：',line)
        l = line.split(':',1)
        with open("Users.txt",'r') as f:
            users = f.readlines()
            for i in users:
                index = users.index(i)
                i = i.split(':',1)[0]
                users[index] = i
            if l[0] in users:
                session.push(('Existed').encode('gbk'))
                return
        with open('Users.txt','a+') as f:
            f.write("{0}\n".format(line))
            session.push(('Success').encode('gbk'))


#聊天房间    
class ChatRoom(Room):
     
    def add(self, session):
        message = 'login:Login successfully\n'    #广播新用户进入以及当前用户在线名单
        message = message.encode('gbk')
        session.push(message)
        self.broadcast(session.name + ' has entered the room.\n') 
        self.server.users[session.name] = session
        Room.add(self, session)
        user_list = list(self.server.users.keys())
        m = 'user_list:{0}'.format(user_list)
        time.sleep(2)
        self.broadcast(m)
    def remove(self, session):  #广播用户离开
        Room.remove(self, session)
        self.broadcast(session.name + ' has left the room.\n')
    def do_say(self, session, line):  #客户端发送消息
        self.broadcast(session.name + ': ' + line + '\n')  

class LogoutRoom(Room):
    """     用户退出时的房间     """  
    def add(self, session):
        '''从服务器中移除'''
        try:
            del self.server.users[session.name]
        except KeyError:
            pass  


#负责服务器和单用户间的相关通信
class ChatSession(async_chat):  
    def __init__(self, server, sock):
        async_chat.__init__(self, sock)
        self.server = server
        self.set_terminator('\n')
        self.data = []
        self.name = None
        self.enter(LoginRoom(server))  
    def enter(self, room):  #从当前房间移除自身，然后添加到指定房间
        try:
            cur = self.room
        except AttributeError:
            pass
        else:
            cur.remove(self)
        self.room = room
        room.add(self)  
    def collect_incoming_data(self, data):   #接受客户端的数据
        self.data.append(data)  

    def found_terminator(self):  #当客户端的一条数据结束时的处理
        line = ''.join(self.data)
        self.data = []
        try:
            self.room.handle(self, line)
        except EndSession:
            self.handle_close()  
    def handle_close(self):
        async_chat.handle_close(self)
        self.enter(LogoutRoom(self.server))

# 服务器类
class ChatServer(dispatcher):
    def __init__(self, port):
        dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        #self.bind(('169.254.47.92', port))
        #self.bind(('192.168.0.182', port))
        #self.bind(('192.168.1.113', port))
        self.bind(('127.0.0.1', port))
        self.listen(20)
        self.users = {}
        self.main_room = ChatRoom(self)
        print("等待客户端连接...")
    def handle_accept(self):
        conn, addr = self.accept()
        ChatSession(self, conn) 
if __name__ == '__main__':
     s = ChatServer(PORT)
     asyncore.loop()
     
