#! coding=utf-8

"""
初始化vc连接，设置默认的用户名和密码
vmware虚拟机的操作
"""
from pyVim.connect import SmartConnect,SmartConnectNoSSL
from abc import abstractmethod, ABC

# 异常处理类


class CreateSnapshotParamError(Exception):
    """
    创建快照抛出的异常
    """
    def __str__(self):
        return "创建快照的参数不正确！"


# ##############


class Vmware(ABC):
    """
    初始化连接类
    :param self._args : 清洗过滤完成的参数由_args_list中的值作为key
    :param self._args_list : 用户原始传入的值
    """
    def __init__(self, SSL=True):
        """
        :param SSL: 是否采用安全的连接，一般我们使用的是不安全的连接
        """
        self._set_host()
        self._set_password()
        self.SSL = SSL
        self._set_port()
        self._set_user()
        self._args = {}
        self._args_list = ""
        self._init_connect()

    def _set_host(self):
        """
        设置默认的vcenter ip
        :return:
        """
        self.host = "192.168.3.229"

    def _set_password(self):
        """
        设置默认的vcenter密码
        :return:
        """
        self.password = "1qaz@WSX"

    def _set_user(self):
        """
        设置默认的user名字
        :return:
        """
        self.user = "administrator@vsphere.local"

    def _set_port(self):
        """
        设置默认的连接端口
        :return:
        """
        if self.SSL:
            self.port = "8443"
        else:
            self.port = "443"

    def _init_connect(self):
        """
        初始化连接到VC
        :return:
        """
        if not self.SSL:
            print(int(self.port), self.host, self.user, self.password)
            si = SmartConnectNoSSL(host=self.host,
                                   user=self.user,
                                   pwd=self.password,
                                   port=int(self.port))
        else:
            si = SmartConnect(host=self.host,
                              user=self.user,
                              pwd=self.password,
                              port=int(self.port))
        self._connection = si

    @abstractmethod
    def build_arg_parser(self):
        """
        初始化handler参数列表
        :return:
        """

    @abstractmethod
    def add_argument(self):
        """
            添加自定义参数
        """

    @abstractmethod
    def handler(self):
        """
        处理请求
        :return:
        """


class CreateSnapshot(Vmware):
    """
    创建快照
    """
    def __init__(self, SSL):
        """
        父类的初始化方法
        :param SSL:
        """
        super().__init__(SSL=SSL)

    def add_argument(self, **kwargs):
        """
        添加创建快照参数
        :return:
        """
        [self._args.__setitem__(arg, kwargs.get(arg)) for arg in self._args_list]

    def handler(self):
        """
        处理创建快照
        :return:
        """
        print(self._args)
        vm = self._connection.content.searchIndex.FindByIp(None, self._args.get("host"), True)
        self.clear_snapshot(vm)  # 清理快照
        vm.CreateSnapshot_Task(name=self._args.get("name"),
                               description=self._args.get("description"),
                               memory=self._args.get("memory"),
                               quiesce=self._args.get("quiesce"))

    def build_arg_parser(self):
        """
        初始化传入参数的列表，创建快照只支持下面
        列表中的参数
        : param host:从ip获取到vm的对象
        : param name: 创建的快照的名字
        : param description: 描述
        : param memory : 是否快照内存
        : param quiesce: 是否是静默
        :return:
        """
        self._args_list = [
                    "host",
                    "name",
                    "description",
                    "memory",
                    "quiesce",
                    ]

    @staticmethod
    def clear_snapshot(vm):
        """
         清理过期的快照
         :param vm :传入获取的虚拟机对象
        :return:
        """
        snap_info = vm.snapshot
        if snap_info:
            for i in snap_info.rootSnapshotList:
                i.snapshot.RemoveSnapshot_Task(True)


# 自测试
if __name__ == "__main__":
    p = CreateSnapshot(SSL=False)
    p.build_arg_parser()
    p.add_argument(host="192.168.3.228",
                   name="test2",
                   description="test desc",
                   memory=True,
                   quiesce=False)
    p.handler()
