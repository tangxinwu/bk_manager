from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from index.JsonModel import GenJSONBar, SeriesBar, GenJSONPie, SeriesPie
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from index import docker_check
from index import make_excel
from index import serviceinstall
from index import services
from index import Uploader
from index.models import *
import os
import json
import pymysql as MySQLdb
from abc import abstractmethod, ABC
import paramiko
import re
import index.create_snapshot_txw


MySQLdb.install_as_MySQLdb()
# Create your views here.

# 图列的缩放 测试用
zoom_option = {"dataZoom": [
    {
        "show": False,
        "start": 0,
        "end": 100,
        "xAxisIndex": [0],
        "filterMode": 'empty',
    },
    {
        "type": 'slider',
        "start": 0,
        "end": 50,
    },



]}


class LogCheck:
    """
    登陆验证
    """
    def __init__(self, request):
        self.request = request

    def _check_session(self):
        """
        检查session
        :return:
        """
        if not self.request.session.get("logged_user", ""):
            self._delete_session()
            return False
        else:
            return True

    def _delete_session(self):
        """
        删除session
        :return:
        """
        try:
            del self.request.session["logged_user"]
        except KeyError:
            pass

    def __call__(self, *args, **kwargs):
        return self._check_session()


class GenData:
    """
    获取x轴和y轴的刻度值
    """
    def __init__(self):
        self.xAsix = ""
        self.yAsix = []

    def _GenXAsix(self):
        """
        获取x轴的数据
        :return:
        """
        all_object = VoteOption.objects.all()
        self.xAsix = [i.OptionName for i in all_object]

    def _GenYAsix(self):
        """
        获取y轴数据
        :return:
        """
        if not self.xAsix:
            self._GenXAsix()
        for i in self.xAsix:
            count = VoteData.objects.filter(VoteOption_name__OptionName=i).count()
            self.yAsix.append(count)

    def __call__(self, *args, **kwargs):
        self._GenXAsix()
        self._GenYAsix()


class Duplication:
    """
    判断是否重复的投票的类
    """
    def __init__(self, request):
        self.request = request

    def process(self):
        """
        查找VoteData
        :return:
        找到ip对应的行 返回True
        没有找到ip对应的行 返回False
        """
        data_check = VoteData.objects.filter(voter_ip=self.request.META.get('REMOTE_ADDR'))
        if len(data_check) != 0:
            return True
        else:
            return False


@csrf_exempt
def get_vote_data(request):
    """
    获取投票数据的接口
    :param request:
    :return:
    """
    if request.POST:
        process = GenData()
        process()
        q = SeriesBar(name="投票量", data=process.yAsix, barWidth="30%")
        p1 = GenJSONBar(title="爱夫卡投票系统", legend=['销量'],
                        xAxis=process.xAsix, series=q)
        last_result = p1.gen()
        last_result['xAxis']['type'] = "category"
        last_result.update(zoom_option)
        return HttpResponse(json.dumps(last_result, ensure_ascii=False))
    return HttpResponse("没有输出")


@csrf_exempt
def index(request):
    """
    加载主页面的views
    :param request:
    :return:
    """
    login_check = LogCheck(request)()
    if not login_check:
        return HttpResponseRedirect("/login/")
    return HttpResponseRedirect("/service_status/")


@csrf_exempt
def install_service(request):
    """
    安装服务的界面
    """
    login_check = LogCheck(request)()
    if not login_check:
        return HttpResponseRedirect("/login/")
    valid_ips = IpInterface.objects.all()
    logged_user = request.session.get("logged_user")
    if request.POST:
        software_name = request.POST.get("software_name", "")
        ipaddr = request.POST.get("ipaddr", "")
        select_object = IpInterface.objects.get(ipaddr=ipaddr)
        username = select_object.username
        password = select_object.password
        try:
            p = getattr(serviceinstall, "Install" + software_name)(ipaddr, username, password)
            result = p.install_service()
        except paramiko.ssh_exception.AuthenticationException:
            result = "SSH连接失败，检查用户名和密码"
        except paramiko.ssh_exception.SSHException:
            result = "SSH 连接超时，稍后再试！"
        except paramiko.ssh_exception.NoValidConnectionsError:
            result = "目标机器可能是windows机器，现在只支持linux版本"
        return HttpResponse(result)
    return render(request, "install_service.html", locals())


@csrf_exempt
def data_gui(request):
    """
    获取数据页面的views
    :param request:
    :return:
    """
    if request.POST:
        flag = request.POST.get("action", "")
        if flag == "shutdown":
            res = os.system("poweroff")
        if flag == "restart":
            res = os.system("reboot")
        return HttpResponse(res)
    logged_user = request.session.get("logged_user")
    return render(request, "data_GUI.html", locals())


@csrf_exempt
def service_status(request):
    """
    查看后台服务的状态，对服务进行操作
    :param request:
    :return:
    """
    login_check = LogCheck(request)()
    if not login_check:
        return HttpResponseRedirect("/login/")
    if request.POST:
        all_service_info = eval(request.POST.get("all_service_info", ""))
        port_status = []
        for i in all_service_info:
            host = i.split("/")[0].split(":")[0]
            port = i.split("/")[0].split(":")[1]
            status = services.PortCheck(host, port)
            port_status.append(str(status))
        return HttpResponse(str(port_status))
    all_service = MonitorService.objects.all()
    logged_user = request.session.get("logged_user")
    return render(request, "service_status.html", locals())


def ip_interface(request):
    """
    ip管理界面
    :param request:
    :return:
    """
    login_check = LogCheck(request)()
    if not login_check:
        return HttpResponseRedirect("/login/")
    all_normal_ip = IpInterface.objects.filter(especily=0).order_by("ipaddr")
    all_especily_ip = IpInterface.objects.filter(especily=1).order_by("ipaddr")
    logged_user = request.session.get("logged_user")
    return render(request, "ip_interface.html", locals())

"""
新的修改售机类型区域开始
"""


class SSHInit(ABC):
    def __init__(self):
        self.ssh_connect = ("yun1.szfcar.com", "root", "Szfcaryun1180129", '22')
        self._ssh = ""
        self._cmd = ""
        self._result = ""
        self._last_result = ""

    def _init_ssh(self):
        s1 = paramiko.SSHClient()
        s1.load_system_host_keys()
        s1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        s1.connect(hostname=self.ssh_connect[0], username=self.ssh_connect[1], \
                   password=self.ssh_connect[2], port=int(self.ssh_connect[3]), timeout=5)
        self._ssh = s1

    @abstractmethod
    def _set_sql(self):
        """
        设置不同的SQL语句来返回不同的结果
        :return:
        """

    def run_query(self):
        """
        运行查询语句返回结果
        :return:
        """
        if not self._cmd:
            self._set_sql()
        stdin,stdout,stderror = self._ssh.exec_command(self._cmd)
        self._result = (lambda x, y: x if x else y)(stdout.read().decode("utf8"), stderror.read().decode("utf8"))

    @abstractmethod
    def _process_result(self):
        """
        处理后面的数据 返回处理后的结果
        :return: self._last_result
        """

    def __call__(self, *args, **kwargs):
        self._init_ssh()
        self._set_sql()
        self.run_query()
        self._process_result()
        return self._last_result


class SNDetail(SSHInit):
    """
    查询序列号的详细信息
    """
    def __init__(self, sn):
        self.sn = sn
        super().__init__()

    def _set_sql(self):
        self._cmd = """ mysql -uroot -pfcar.8 www -e "SELECT downclass_id,lang_id,activetype,actives FROM \
                    www_tbsn WHERE trader_id=11 AND sn='{}' \G" """.format(self.sn)

    def _process_result(self):
        # temp_list = re.findall("\w+.*?[^\*]\n", self._result)
        temp_list = re.findall("\d+", self._result)[1:]  # 去除第一列的序列号
        self._last_result = temp_list


class DownClassDetail(SSHInit):
    """
    查找所有Downclass信息
    """
    def __init__(self):
        super().__init__()

    def _set_sql(self):
        """
        设置查询所有downclass的查询语句
        :return:
        """
        self._cmd = """mysql -uroot -pfcar.8 www -e "SELECT id,name FROM www_tbdownclass ORDER BY name\G" """

    def _process_result(self):
        """
        处理发送回来的数据
        :return: {'1': '（禁止）006', '2': '（禁止）002', '3': '（禁止）007', '4': 'F3-A 简体版',
                .....
               '65': 'F3-A 美国', '375': '（定制）F3 凯普特原厂-英文版', '68': 'F3-W 美国',
               '69': 'F3-D 台湾2 （非定制界面）', '201': 'F3-G 南非', '203': 'F3-G 内部使用',
                '893': 'F7S-Pro 越南区域', '895': 'F8S  汽油中文版'}

        """
        temp_list = re.findall("\w+.*?[^\*]\n", self._result)
        temp_id_list = []
        temp_downclass_list = []
        for i in range(len(temp_list)):
            if i%2:
                temp_id_list.append(temp_list[i].split(":")[1].strip(" ").rstrip("\n"))
            else:
                temp_downclass_list.append(temp_list[i].split(":")[1].strip(" ").rstrip("\n"))

        self._last_result = dict(tuple(zip(temp_downclass_list, temp_id_list)))


class LangDetail(SSHInit):
    """
    查询所有语言的信息
    """
    def __init__(self):
        super().__init__()

    def _set_sql(self):
        """
        设置查询所有语言的的sql命令
        :return:
        """
        self._cmd = """mysql -uroot -pfcar.8 www -e "SELECT id,cnname FROM www_tblang \G" """

    def _process_result(self):
        """
        处理返回的sql语句查询结果
        :return:{'1': '中文', '2': '英文', '3': '俄文', '4': '日文', '5': '所有',....}
        """
        temp_list = re.findall("\w+.*?[^\*]\n", self._result)
        temp_id_list = []
        temp_lang_list = []
        for i in range(len(temp_list)):
            if i%2:
                temp_id_list.append(temp_list[i].split(":")[1].strip(" ").rstrip("\n"))
            else:
                temp_lang_list.append(temp_list[i].split(":")[1].strip(" ").rstrip("\n"))

        self._last_result = dict(tuple(zip(temp_lang_list, temp_id_list)))


class ModifyDownclass(SSHInit):
    """
    修改www_tbsn数据库内容
    """
    def __init__(self, sn, lang_id, downclass_id, actives, activetype):
        self.sn = sn
        self.lang = lang_id
        self.downclass = downclass_id
        self.actives = actives
        self.activetype = activetype
        super().__init__()

    def _set_sql(self):
        self._cmd = """mysql -uroot -pfcar.8 www -e "UPDATE www_tbsn SET lang_id={},downclass_id={},activetype={},actives={} WHERE sn='{}'" """\
                    .format(int(self.lang), int(self.downclass), self.activetype, int(self.actives), self.sn)

    def _process_result(self):
        """
        无需处理返回数据
        :return:
        """
        pass


@csrf_exempt
def change_type(request):
    """
    新版修改样机售机类型的页面
    :param request:
    :return:
    """
    if request.session.get("changetype", "") != "changetype@fcar.com":
        try:
            del request.session["changetype"]
        except:
            pass
        return HttpResponseRedirect("/change_login/")
    # 查询模式
    if request.POST.get("sn_query", ""):
        sn = request.POST.get("sn_query", "")
        sn_p = SNDetail(sn)
        sn_data = sn_p()
        if not sn_data:
            # 没有对应的序列号信息
            return HttpResponse("样机下没有此序列号!")
        downclass_p = DownClassDetail()
        downclass_data = downclass_p()
        lang_p = LangDetail()
        lang_data = lang_p()
        temp_locals = locals()  # 临时中间变量
        temp_dict = {}  # 临时中间变量
        for i in temp_locals:  # 把所有data的变量集合成一个变量{"sn":xxx, "downclass" : xxx, "lang":xxx}
            if i.endswith("_data"):
                temp_dict[i.split("_")[0]] = temp_locals.get(i)
        return HttpResponse(json.dumps(temp_dict, ensure_ascii=False))
    # 修改模式
    if request.POST.get("sn", ""):
        sn = request.POST.get("sn", "")
        lang = request.POST.get("lang", "")
        downclass = request.POST.get("downclass", "")
        activetype = request.POST.get("activetype", "")
        actives = request.POST.get("actives", "")

        p = ModifyDownclass(sn, lang, downclass, actives, activetype)()
        return HttpResponse("修改成功！")
    return render(request, "change_type.html", locals())


@csrf_exempt
def change_login(request):
    """
    新的更改售机类型的登陆界面
    :param request:
    :return:
    """
    if request.POST:
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        if email != "changetype@fcar.com" or password != "szfcar88":
            return HttpResponse(json.dumps({"login_flag": "failed"}))
        else:
            request.session.__setitem__("changetype", email)
            return HttpResponse(json.dumps({"login_flag": "successful"}))
    return render(request, "change_login.html", locals())


"""
新的修改售机类型区域结束
"""


def make_to_excel(request):
    """
    从yun1拿数据导出excel
    :param request:
    :return:
    """
    # login_check = LogCheck(request)()
    # if not login_check:
    #     return HttpResponseRedirect("/login/")
    type = request.GET.get('type_name', '')
    start_time = request.GET.get('start_time', '')
    end_time = request.GET.get('end_time', '')
    host_list = {
            'hostname': 'yun1.szfcar.com',
            'username': 'root',
            'password': 'fcar.8',
            'database' : 'www',

                }
    sql_type = {
        'wenkong' : {'sql': """select (select name from www_tbmachine where id=machine_id), 
                                    (select cnname from www_tbcarlist where id=carlist_id),
                                    (select cnname from www_tblang where id=lang_id),
                                    ver,chkdate from www_tbverlist where chkdate is not NULL ;""",
                    'title':('售机类型','车型','语言','版本','过审日期',)},
        'f6shuanji' : {'sql' : """select * from sh_tbreplace""",'title' : ('id','换机日期','快递名称','快递单号','发货人','发货人电话','发货人地址','区域','市场人员','机器属性','机器型号','机器序列号','发货日期','发货数量','单价','金额','回款','备注','创建时间','修改时间',)},
        'f7shuanji' :{'sql': """select * from sh_tbreplacec""",'title':('id', '换机日期', '快递名称', '快递单号', '发货人', '发货人电话', '发货人地址', '区域', '市场人员', '机器属性', '机器型号', '机器序列号', '发货日期', '发货数量', '单价','金额', '回款', '备注', '创建时>间', '修改时间',)},
        'wenkong_zhuanjia' :{'sql':"""select (select name from www_tbmachine where id=machine_id),
                                      (select cnname from www_tbcarlist where id=carlist_id and cnname like "%%专家%%"), 
                                      (select cnname from www_tblang where id=lang_id),ver,datetime,chkdate from www_tbverlist ;""",
                            'title':('售机类型','车型','语言','版本','发布日期','过审日期',)},
        'carlist': {'sql':"""SELECT  (SELECT cnname FROM www_tbcarclass WHERE id = carclass_id), 
                                    (SELECT enname FROM www_tbcarclass WHERE id = carclass_id),
                                    (SELECT cnname FROM www_tbcargroup WHERE id = cargroup_id),
                                    (SELECT enname FROM www_tbcargroup WHERE id = cargroup_id),
                                    id, cnname, enname, path FROM www_tbcarlist;""",
                    'title':('中文车类','英文车类','中文车组', '英文车组','ID','中文名','英文名', '路径')},
        'banbenfabu_list' : {'sql' : """select ver,datetime,(select cnname from www_tbcarlist where id=carlist_id),(select cnname from www_tblang where id=lang_id ),(select carclass_id from www_tbcarlist where id=carlist_id),
                                        (select cargroup_id from www_tbcarlist where id=carlist_id) from www_tbverlist where chkdate and datetime BETWEEN "%s" AND  "%s";
        """ %(start_time,end_time),
                    'title' : ('版本号', '发布日期', '车型名', '语言', '车系', '车组', '是否为大版本')
        }
    }

    if type:
        p = make_excel.MakeToExcel(host_list, sql_type[type]['sql'],type)
        p.get_data()
        p.to_execl('ttt', p.data,sql_type[type]['title'])
        f = open('ttt.xlsx','rb')
        response = HttpResponse(f.read())
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename=%s.xlsx' %type
        return response
    logged_user = request.session.get("logged_user")
    return render(request, "GenExcelFile.html", locals())


@csrf_exempt
def docker_service(request):
    """
    检测docker以及其集群上有的服务
    :param request:
    :return:
    """
    login_check = LogCheck(request)()
    if not login_check:
        return HttpResponseRedirect("/login/")
    if request.POST:
        flag = request.POST.get("action", "")
        if flag == "refresh_service":
            try:
                p = docker_check.DockerCheck()
                normal_service = p.get_container_list()
                swarm_service = p.get_swarm_service()
                # 移除无效的数据库中service_name 开始
                exsited_normal_service_name = set([i.serviceName for i in DockerServiceList.objects.filter(isInSwarm=0)])
                refeshed_normal_service_name = set([i for i in normal_service.split("\n") if i])
                [DockerServiceList.objects.filter(serviceName=i).delete() for i in exsited_normal_service_name - refeshed_normal_service_name]
                # 移除无效的数据库中service_name 结束

                # 移除无效的数据库中swarm_service_name 开始

                exsited_swarm_service_name = set([i.serviceName for i in DockerServiceList.objects.filter(isInSwarm=1)])
                refeshed_swarm_service_name = set([i[1] for i in swarm_service if i])
                [DockerServiceList.objects.filter(serviceName=i).delete() for i in exsited_swarm_service_name - refeshed_swarm_service_name]
                # 移除无效的数据库中swarm_service_name 结束

                # 开始更新普通服务到数据库
                for service_name in refeshed_normal_service_name:
                    if re.findall("\w+\.\w+\.\w+", service_name):continue  # 过滤warm子服务
                    status_result = p.get_container_status(service_name) # 获取服务详细的信息
                    DockerServiceList.objects.update_or_create(serviceName=service_name,isInSwarm=0,\
                                                               defaults={"mappedPort": status_result[1],\
                                                                         "serviceStatus": status_result[0]})
                # 结束更新普通服务到数据库

                # 开始更新swarm服务到数据库
                for service_name in swarm_service:
                    if service_name:
                        DockerServiceList.objects.update_or_create(serviceName=service_name[1], isInSwarm=1,\
                                                                   defaults={"mappedPort": service_name[5],\
                                                                             "serviceStatus": service_name[2] + " " + service_name[3]})
                # 结束更新swarm服务到数据库
                return HttpResponse("已经刷新")
            except docker_check.DockerNotFound:
                return HttpResponse("没有找到docker的管理节点")

    all_normal_service = DockerServiceList.objects.filter(isInSwarm=0)
    all_swarm_service = DockerServiceList.objects.filter(isInSwarm=1)
    logged_user = request.session.get("logged_user")
    return render(request, "docker_service.html", locals())


@csrf_exempt
def vote(request):
    """
    投票界面
    :param request:
    :return:
    """
    login_check = LogCheck(request)()
    if not login_check:
        return HttpResponseRedirect("/login/")
    all_option = VoteOption.objects.all()
    all_department = Department.objects.all()
    logged_user = request.session.get("logged_user")
    return render(request, "vote.html", locals())


@csrf_exempt
def vote_action(request):
    """
    提交投票的时候的行为
    :param request:
    :return:
    """
    if request.POST:
        check_duplicate_vote_flag = Duplication(request).process()
        if check_duplicate_vote_flag:
            return HttpResponse("您已经投过票了！")
        option_ids = request.POST.get("option_ids", "")
        logged_name = request.POST.get("logged_name", "")
        department = request.POST.get("department", "")
        option_ids_list = option_ids.split("-")
        vote_ip = request.META.get('REMOTE_ADDR')
        for option_id in option_ids_list:
            department_object = Department.objects.get(department_name=department)
            VoteOption_object = VoteOption.objects.get(id=int(option_id))
            VoteData.objects.create(voter=logged_name, voter_ip=vote_ip, department_name=department_object, \
                                    VoteOption_name=VoteOption_object)
        return HttpResponse("投票成功！感谢您的参与！")
    return HttpResponse("NO OPTIONS")


@csrf_exempt
def filter_option(request):
    """
    过滤选项，本部门的人只能看到自己的部门的选票
    :param request:
    :return:
    """
    if request.POST:
        department_name = request.POST.get("department_name", "")
        matched_option_objects = VoteOption.objects.filter(belongToDepartment__department_name=department_name)
        return HttpResponse(serializers.serialize("json", matched_option_objects))
    return HttpResponse("NO OPTIONS")


@csrf_exempt
def login(request):
    """
    登陆界面
    :param request:
    :return:
    """
    if request.POST:
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        user_check = LogAccount.objects.filter(email=email, password=password)
        if user_check:
            request.session.__setitem__("logged_user", email)
            return HttpResponse(json.dumps({"login_flag": "successful"}))
        else:
            try:
                del request.session["logged_user"]
            except KeyError:
                pass
            return HttpResponse(json.dumps({"login_flag": "failed"}))
    return render(request, "login.html", locals())


def logout(request):
    """
    注销事件views
    :param request:
    :return:
    """

    try:
        del request.session["logged_user"]
    except KeyError:
        pass
    return HttpResponseRedirect("/login/")


@csrf_exempt
def server_type_count(request):
    """
    统计服务器虚拟机和实体机的数量
    :param request:
    :return:
    """
    if request.POST:
        hardware_type = [str(i) for i in Hardware.objects.all()]
        hardware_count = [IpInterface.objects.filter(hardware_type__hardware_type=i).count() for i in hardware_type]
        q = SeriesPie(data=list(zip(hardware_count, hardware_type)), radius="50%", roseType="angle", name="现有的服务器")
        p = GenJSONPie(series=q, title="虚拟机和物理机比例", tooltip=True, legend=hardware_type)
        data = p.gen()
        return HttpResponse(json.dumps(data, ensure_ascii=False))
    return HttpResponse("没有输出!")


@csrf_exempt
def os_count(request):
    """
    统计操作系统的类型数量
    :param request:
    :return:
    """
    if request.POST:
        os_type = [str(i) for i in OStype.objects.all()]
        os_count = [IpInterface.objects.filter(OS_type__OS_name=i).count() for i in os_type]
        q = SeriesPie(data=list(zip(os_count, os_type)), radius="50%", roseType="angle", name="现有的操作系统")
        p = GenJSONPie(series=q, title="操作系统分布比例", tooltip=True, legend=os_type)
        data = p.gen()
        return HttpResponse(json.dumps(data, ensure_ascii=False))
    return HttpResponse("没有输出!")


@csrf_exempt
def test_environment(request):
    """
    测试环境功能的views
    :param request:
    属性jar 设置service jar包的在服务器的位置
    POST 上传jar文件 get 替换文件
    :return:
    """
    upload_params = {
        "jar": {"path": r"/tmp/accountservice", "host": "192.168.3.212"},
        "war": {"path": r"/usr/local/tomcat/webapps/", "host": "192.168.3.213"},
        "sql": {"path": r"/tmp", "host": "192.168.3.212"}
    }
    if request.method == "POST":
        """
            属性 file_comment: 保存前端传入的文件的内容
            属性 path : 保存在本地服务器的路径
            属性 p        : 替换服务的实例
            属性 upload_status : 上传到本地后的状态 上传正常返回true 上传错误返回false
        """
        # 上传文件
        # 判断上传的文件类型
        input_check = [(request.FILES.get(i+"_name"), i) for i in upload_params if request.FILES.get(i+"_name")]
        if input_check:
            file_comment = input_check[0][0]
            upload_type = input_check[0][1]
            path = upload_params.get(upload_type).get("path")
            print(upload_type)
            p = getattr(Uploader, "Service" + upload_type.capitalize() + "Uploader")(path)
            upload_status = p.run_upload(file_comment)
            if upload_status:
                # 从中间服务器传输到服务器
                host = upload_params.get(upload_type).get("host")
                transport_flag = p.transport_to_des(host)
                if transport_flag:
                    return HttpResponse("传输成功")
                else:
                    return HttpResponse("传送失败")
            else:
                return HttpResponse("上传文件名不合法")
        else:
            return HttpResponse("上传的文件不能为空！")
    if request.GET:
        # 替换包
        action = request.GET.get("action", "")
        host = upload_params.get(action).get("host")
        username = IpInterface.objects.get(ipaddr=host).username
        password = IpInterface.objects.get(ipaddr=host).password
        p = getattr(serviceinstall, "InstallService" + action.capitalize())(host, username, password)
        result = p.install_service()
        return HttpResponse(result)
    return render(request, "test_environment.html", locals())


@csrf_exempt
def soft_list(request):
    """
    常用软件下载列表
    :param request:
    :return:
    """
    pass


@csrf_exempt
def timer_snapshot(request):
    """
    定时创建vmware虚拟机快照
    :param request:
    :return:
    """
    task_list = SnapshotTask.objects.all()
    all_vm_list = IpInterface.objects.filter(hardware_type__hardware_type="虚拟机")
    if request.POST:
        ip = request.POST.get("ip", "")
        interval = (lambda x: 0 if not x else int(x))(request.POST.get("interval", ""))
        timing_unit = request.POST.get("timing_unit", "")
        week_day = request.POST.get("week_day", "")
        snap_date = (lambda x: x if not x else x.split("T")[1])(request.POST.get("detail_time", ""))
        try:
            if ip:
                SnapshotTask.objects.update_or_create(applicationIp=ip,
                                                      defaults={"interval": interval, \
                                                                "timing_unit": timing_unit, \
                                                                "week_day": week_day,\
                                                                "snap_date": snap_date})
            return HttpResponse("变更成功")
        except:
            return HttpResponse("变更失败！")
    return render(request, "timer_snapshot.html", locals())


@csrf_exempt
def snapshot_status(request):
    """
    检测后台控制定时的后台进程Daemon_server是否存在
    :param request:
    :return:
    """
    if request.POST:
        action = request.POST.get("action")
        p = services.SnapshotService("127.0.0.1", "tang", "sakamotomaaya1")
        try:
            return HttpResponse(getattr(p, action)())
        except AttributeError:
            return HttpResponse("POST ERROR")
    return HttpResponse("no input")
