#! coding=utf8
"""
安装服务的类
"""

import paramiko
from abc import ABC, abstractmethod


class InstallService(ABC):
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
    def install_service(self):
        """
        安装服务的抽象类
        :return:
        """


class InstallTomcat(InstallService):
    """
    安装tomcat
    """
    def __init__(self, host, username, password):
        """
        使用父类的初始化方法
        """
        super().__init__(host, username, password)

    def install_service(self):
        """
        安装tomcat服务
        :return: shell脚本运行的结果
        """
        tomcat_script_download_cmd = """wget http://192.168.3.216:8081/scripts/install_tomcat_8.0.48_jdk8.sh -O /tmp/install_tomcat_8.0.48_jdk8.sh && sh /tmp/install_tomcat_8.0.48_jdk8.sh"""
        temp_locals = locals()
        run_status = []
        for cmd in temp_locals:
            if cmd.endswith("_cmd"):
                stdin, stdout, stderror = self._connect.exec_command(temp_locals.get(cmd))
                run_status.append((lambda x,y:x if x.read().decode("utf8") else y.read().decode("utf8"))(stdout, stderror))
        return run_status


class InstallMysql(InstallService):
    """
    安装MYSQL5.5 rpm包
    """
    def __init__(self, host, username,password):
        """
        引用父类的初始化方法
        """
        super().__init__(host, username, password)

    def install_service(self):
        """
        安装JDK
        :return: 运行脚本运行的结果
        """
        mysql_install_cmd = """wget http://192.168.3.216:8081/scripts/install_Mysql5.5_rpm.sh -O /tmp/install_Mysql5.5_rpm.sh && sh /tmp/install_Mysql5.5_rpm.sh"""
        temp_locals = locals()
        run_status = []
        for cmd in temp_locals:
            if cmd.endswith("_cmd"):
                stdin, stdout, stderror = self._connect.exec_command(temp_locals.get(cmd))
                run_status.append((lambda x,y:x if x.read().decode("utf8") else y.read().decode("utf8"))(stdout, stderror))
        return run_status


class InstallNginx(InstallService):
    """
    源码编译安装nginx
    """
    def __init__(self, host, username, password):
        """
        引用父类的初始化
        :param host:
        :param username:
        :param password:
        """
        super().__init__(host, username, password)

    def install_service(self):
        """
        安装nginx
        :return:
        """
        JDK_install_cmd = """wget http://192.168.3.216:8081/scripts/install_nginx.sh -O /tmp/install_nginx.sh  && sh /tmp/install_nginx.sh"""
        temp_locals = locals()
        run_status = []
        for cmd in temp_locals:
            if cmd.endswith("_cmd"):
                stdin, stdout, stderror = self._connect.exec_command(temp_locals.get(cmd))
                run_status.append((lambda x, y: x if x.read().decode("utf8") else y.read().decode("utf8"))(stdout, stderror))
        return run_status


class InstallServiceJar(InstallService):
    """
    192.168.3.212上的jar包的重启
    """
    def __init__(self, host, username, password):
        """
        引用父类的初始化方法
        """
        super().__init__(host, username, password)

    def install_service(self):
        """
        重启jar包的服务
        :return:
        """
        restart_cmd = """wget http://192.168.3.216:8081/scripts/service_control/service_jar_control.sh -O /tmp/service_jar_control.sh \
                         && sh /tmp/service_jar_control.sh"""
        stdin, stdout, stderror = self._connect.exec_command(restart_cmd)
        if stderror.read():
            return "jar服务重启失败"
        return "jar服务已经重启"


class InstallServiceWar(InstallService):
    """
    192.168.3.213 tomcat重启
    """
    def __init__(self, host, username, password):
        """
        引用父类的初始化方法
        :param username:
        :param password:
        """
        super().__init__(host, username, password)

    def install_service(self):
        """
        重启tomcat
        :return:
        """
        restart_cmd = """wget http://192.168.3.216:8081/scripts/service_control/service_tomcat_control.sh \
                         -O /tmp/service_tomcat_control.sh && sh /tmp/service_tomcat_control.sh kill && \
                         sh /tmp/service_tomcat_control.sh restart """
        stdin, stdout, stderror = self._connect.exec_command(restart_cmd)
        if stderror.read():
            return "tomcat启动失败"
        return "tomcat 已经重启"


class InstallServiceSql(InstallService):
    """
    替换3.212上面的数据库内容
    """
    def __init__(self,host, username, password):
        """
        引用父类的初始化方法
        :param host:
        :param username:
        :param password:
        """
        super().__init__(host, username, password)

    def install_service(self):
        """
        执行命令替换数据库内容
        :return:
        """
        change_cmd = """sed -i "s/\'fcsp_account_db\'/fcsp_account_db/g" /tmp/fcsp_account_db.sql && \
                     mysql -uroot -p123456 fcsp_account_db -e 'source /tmp/fcsp_account_db.sql' """
        stdin, stdout, stderror = self._connect.exec_command(change_cmd)
        if stderror.read():
            return "数据库更新错误"
        return "sql替换完成"


