#! coding=utf-8

"""
上传文件的类
"""

from abc import ABC, abstractmethod
import os
import paramiko
from index.models import IpInterface


class Uploader(ABC):
    """
    上传文件的基类
    """
    def __init__(self, local_path):
        """
        基类构造函数
        :param local_path: 文件上传到服务器的目录
        :属性 self.loca_file: 文件上传到本地服务器的绝对路径包含文件名
        :属性 self.file_name : 上传的文件的文件名
        :属性 self.user_name : 从数据库中获取的远程端的用户名
        :属性 self.user_name : 从数据库中获取的远程端的密码
        ;属性 self.des_file : 远程服务器的文件路径 默认为和local_file 一样
        """
        self.file_name = ""
        self.local_path = local_path
        self.local_file = ""
        self.des_file = ""

    @abstractmethod
    def _file_name_check(self):
        """
        校验文件名合法
        :return: 合法返回true，不合法返回fasle
        """

    def run_upload(self, file_comment):
        """
        开始上传文件
        :param file_comment: 前段传入的文件类<class 'django.core.files.uploadedfile.InMemoryUploadedFile'>
        :return: 上传成功返回true，失败返回false
        """
        self.file_name = file_comment.name
        if not self._file_name_check():
            return False
        if not os.path.isdir(self.local_path):
            os.system("""mkdir -p {}""".format(self.local_path))
        self.local_file = os.path.join(self.local_path, self.file_name)
        with open(self.local_file, "wb") as f:
            try:
                f.write(file_comment.read())
            except:
                return False
        return True

    def transport_to_des(self, host, des_file=None):
        """
        这个功能可以单独使用 也可以不使用
        通过paramiko模块的sftp功能传输到目标机器
        :param host: 从本机传送到的目标端ip地址
        :param des_file: 传入远程端的文件路径
        :return: 连接异常返回fasle 正常返回true
        """
        try:
            with paramiko.Transport((host, 22)) as t:
                username = IpInterface.objects.get(ipaddr=host).username
                password = IpInterface.objects.get(ipaddr=host).password
                t.connect(username=username, password=password)
                sftp = paramiko.SFTPClient.from_transport(t)
                # 把本地的位置 放到目标机器的同一位置 实际上两个路径是一样的 可传入额外的参数覆盖原来的参数
                if des_file:
                    self.des_file = des_file
                else:
                    self.des_file = self.local_file
                sftp.put(self.local_file, self.des_file)
        except:
            return False
        return True


class ServiceJarUploader(Uploader):
    """
    发布服务jar包上传
    """
    def __init__(self, local_path):
        """
        使用基类的初始化方法
        :param file_name:
        :param local_path:
        """
        super().__init__(local_path)

    def _file_name_check(self):
        """
        确保上传的文件的名字为AccountService.jar
        :return: 检测合法返回True 不合法返回False
        """
        if self.file_name != "AccountService.jar":
            return False
        else:
            return True


class ServiceWarUploader(Uploader):
    """
    发布war包，上传
    """
    def __init__(self, local_path):
        """
        以引用父类的初始化的方法
        :param local_path: 本地保存war的路径
        """
        super().__init__(local_path)

    def _file_name_check(self):
        """
        上传文件名合法性检测
        :return: 检测合法返回True 不合法返回False
        """
        if self.file_name != "FcarBackendWeb.war":
            return False
        else:
            return True


class ServiceSqlUploader(Uploader):
    """
    sql，上传
    """
    def __init__(self, local_path):
        """
        以引用父类的初始化的方法
        :param local_path: 本地保存war的路径
        """
        super().__init__(local_path)

    def _file_name_check(self):
        """
        上传文件名合法性检测
        :return: 检测合法返回True 不合法返回False
        """
        if self.file_name != "fcsp_account_db.sql":
            return False
        else:
            return True
