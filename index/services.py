#! coding=utf-8
"""
操作服务的类
"""
from abc import ABC, abstractmethod
import os
import socket
import paramiko
try:
    import serviceinstall
except ImportError:
    from index import serviceinstall


class Service(ABC):
    """
    操作服务的抽象类接口
    """
    def __init__(self, host, username, password):
        """
        实例化的参数
        :param host: 主机名
        :param username: 用户名
        :param password: 密码
        """
        self.host = host
        self.username = username
        self.password = password
        self._connect = ""
        self._init_sshclient()

    def _init_sshclient(self):
        """
        初始化ssh链接
        :return:
        """
        s1 = paramiko.SSHClient()
        s1.load_system_host_keys()
        s1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        s1.connect(hostname=self.host, username=self.username, password=self.password, port=22, timeout=10)
        self._connect = s1

    @abstractmethod
    def start(self):
        """
        定义服务启动的接口
        :return:
        """

    @abstractmethod
    def stop(self):
        """
        定义服务停止的接口
        :return:
        """

    def restart(self):
        """
        定义重启的接口
        :return:
        """
        self.stop()
        self.start()
        return self.start()

    @abstractmethod
    def status(self):
        """
        定义查看服务的抽象类接口
        :return:
        """


class TomcatService(Service):
    def start(self):
        """
        tomcat启动的脚本
        :return:
            0 命令没有报错，服务已经启动
            其他 命令运行报错，或者服务启动失败
        """
        start_cmd = """service tomcat start"""
        flag = os.system(start_cmd)
        return flag

    def stop(self):
        """
        tomcat停止脚本
        :return:
            0 命令没有报错运行完成，服务已经停止
            其他 命令运行报错 或者服务停止失败
        """
        stop_cmd = """service tomcat stop"""
        flag = os.system(stop_cmd)
        return flag

    def status(self):
        """
        查看tomcat的服务状态
        :return:
            0 服务未起来
            1 服务已经起来
        """
        sk = socket.socket()
        params = ("127.0.0.1", 8080)
        try:
            sk.connect(params)
        except ConnectionRefusedError:
            return 0
        return 1


class SnapshotService(Service):
    def __init__(self, host, username, password):
        """
        引用父类的初始化方法
        """
        super().__init__(host, username, password)

    def status(self):
        status_cmd = """ps -ef | grep Daemon_server | grep -v grep"""
        stdin, stdout, stderror = self._connect.exec_command(status_cmd)
        flag = stdout.read()
        print(flag)
        if flag:
            return "Running"
        return "Exited"

    def start(self):
        pass

    def stop(self):
        pass






"""
端口开放检测
"""


class PortCheckFail(BaseException):
    def __str__(self):
        return "端口检测失败"


def PortCheck(host, port):
    """
    检测端口是否开放
    """
    sk = socket.socket()
    params = (host, int(port))
    try:
        sk.settimeout(2)
        sk.connect(params)
        return "端口使用正常"
    except ConnectionRefusedError:
        return PortCheckFail()
    except TimeoutError:
        return PortCheckFail()
    except socket.timeout:
        return PortCheckFail()
    finally:
        sk.close()


"""
端口检测结束
"""

