#! coding=utf8
"""
操作docker的类
"""
from index.models import IpInterface
import paramiko
import re


class DockerNotFound(Exception):
    def __str__(self):
        return "没有找到相应的docker管理节点"


class DockerCheck:
    """
    检测Docker状态的类
    """
    def __init__(self):
        self._connection = ""
        self._result = ""
        self._find_docker()
        self._init_sshclient()

    def _find_docker(self):
        """
        找到数据库中docker节点的querySet
        :return: 实例属性
        """
        docker_object = IpInterface.objects.filter(comment__icontains="docker管理节点")
        if not docker_object:
            raise DockerNotFound
        self._docker_object = docker_object[0]

    def _init_sshclient(self):
        """
        初始化ssh连接
        :return:
        """
        s1 = paramiko.SSHClient()
        s1.load_system_host_keys()
        s1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        s1.connect(hostname=self._docker_object.ipaddr, username=self._docker_object.username, password=self._docker_object.password, port=22, timeout=5)
        self._connection = s1

    def _connect_host(self, cmd):
        """
        连接主机后运行命令
        :param cmd: 输入运行的命令
        :return: 返回命令的输出和报错信息到self._result（命令被正常运行的时候错误信息为空）
        """
        stdin, stdout, stderror = self._connection.exec_command(cmd)
        temp_result = stdout.read().decode("utf8"), stderror.read().decode("utf8")
        self._result = (lambda x: x[0] if not x[1] else x[1])(temp_result)

    def get_container_list(self):
        """
        获取docker上起的容器列表名字（即提供的服务）
        :return:返回一个结果的元祖，元祖的第一位是正常输出信息，第二位是错误信息
                正常的输出结果已换行符隔离开来
        """
        cmd = """docker ps -a | sed '1d' | awk -F ' ' '{print $NF}'"""
        self._connect_host(cmd)
        return self._result

    def get_container_status(self, container_name):
        """
        通过某个容器名字获取其对应的端口映射信息和状态
        :param container_name: 查找的容器名字
        :return:返回一个结果的列表， 列表里面的内容的顺序是(端口信息,状态信息)
        """
        query_cmd = """docker container inspect {}""".format(container_name)
        self._connect_host(query_cmd)
        status = re.findall("Status.*?,", self._result)[0][:-1].split(":")[1].replace("\"", "").replace(" ", "")

        port_tmp1 = re.findall('PortBindings.*?"Rest', self._result.replace("\n", ""))[0].replace(" ", "")  # 初步处理数据
        port_tmp2 = eval(re.findall("{.*}", port_tmp1)[0])  # port_tmp2 生成了映射的端口的字典
        port = ""  # 开始拼接字符串
        for k, v in port_tmp2.items():
            port += v[0].get("HostPort") + "->" + k + ";"
        return status, port

    def get_swarm_service(self):
        """
        获取swarm下的服务
        :return:
        返回运行docker service ls 下的每一行6个元素为一组
        ['ezeezth45dpg', 'yum_service', 'replicated', '2/2', 'docker-manager1:5000/yum_service:v4', '*:8081->80/tcp']
        类似于这种
        """
        query_cmd = """docker service ls | sed '1d' """
        self._connect_host(query_cmd)
        last_result = []
        for i in self._result.split("\n"):  # 有多个service是需要分开处理:
            temp_status = re.findall("[0-9a-zA-z:_/*->]+.*?|", i.replace(" ", "|"))
            temp_result = [i for i in temp_status if i]
            if len(temp_result) == 5:
                temp_result.append("service未启动")
            last_result.append(temp_result)
        return last_result




