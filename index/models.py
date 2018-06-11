from django.db import models

# Create your models here.


class OStype(models.Model):
    """
    记录现有的操作系统的类型
    """
    OS_name = models.CharField("操作系统名字", max_length=150, blank=True, null=True)

    class Meta:
        ordering = ["-OS_name"]
        verbose_name_plural = "操作系统名"

    def __str__(self):
        return self.OS_name


class Hardware(models.Model):
    """
    记录硬件类型，虚拟机还是物理机
    """
    hardware_type = models.CharField("硬件类型", max_length=50, blank=True, null=True)

    class Meta:
        verbose_name_plural = "硬件类型"
        ordering = ["-hardware_type"]

    def __str__(self):
        return self.hardware_type


class IpInterface(models.Model):
    """
    显示ip分配的结果
    """
    ipaddr = models.GenericIPAddressField("分配的ip地址")
    function = models.CharField("ip对应的功能", max_length=20, blank=True, null=True)
    username = models.CharField("用户名", max_length=100, blank=True, null=True)
    password = models.CharField("对应的密码", max_length=20, blank=True, null=True)
    comment = models.CharField("备注", max_length=50, blank=True, null=True)
    domain_name = models.CharField("域名", max_length=100, blank=True, null=True)
    OS_type = models.ForeignKey("OStype", on_delete=models.CASCADE, default=1)
    especily = models.BooleanField("是否是特殊IP", default=0)
    hardware_type = models.ForeignKey("Hardware", on_delete=models.CASCADE, default=1)

    class Meta:
        ordering = ["-ipaddr"]
        verbose_name_plural = "ip分配结果"

    def __str__(self):
        return self.ipaddr


class DockerServiceList(models.Model):
    """
    Docker服务状态
    """
    serviceName = models.CharField("docker下的服务名字", max_length=100)
    mappedPort = models.CharField("映射的端口名字", max_length=200, blank=True, null=True)
    serviceStatus = models.CharField("服务运行的状态", max_length=100, blank=True, null=True)
    isInSwarm = models.BooleanField("是否存在于swarm集群中", blank=True,default=False)
    comment = models.CharField("备注", max_length=100, blank=True, null=True)

    class Meta:
        ordering = ["serviceName"]
        verbose_name_plural = "docker 服务状态"

    def __str__(self):
        return self.serviceName


class Department(models.Model):
    """
    所有部门名
    """
    department_name = models.CharField("部门名字", max_length=50)

    class Meta:
        ordering = ["department_name"]
        verbose_name_plural = "部门名字"

    def __str__(self):
        return self.department_name


class VoteOption(models.Model):
    """
    投票选项
    """
    OptionName = models.CharField("投票选项", max_length=100)
    belongToDepartment = models.ForeignKey("Department", on_delete=models.CASCADE)

    class Meta:
        ordering = ["OptionName"]
        verbose_name_plural = "投票选项"

    def __str__(self):
        return self.OptionName


class VoteData(models.Model):
    """
    投票所有的数据
    """
    voter = models.CharField("投票人的名字", max_length=30)
    voter_ip = models.GenericIPAddressField("投票者的IP")
    department_name = models.ForeignKey("Department", on_delete=models.CASCADE)
    VoteOption_name = models.ForeignKey("VoteOption", on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        ordering = ["voter"]
        verbose_name_plural = "投票数据"

    def __str__(self):
        return self.voter


class LogAccount(models.Model):
    """
    登陆页面的账号和密码
    """
    email = models.CharField("邮箱地址", max_length=50)
    password = models.CharField("密码", max_length=50)

    class Meta:
        ordering = ["-email"]
        verbose_name_plural = "登陆名和密码"

    def __str__(self):
        return self.email


class MonitorService(models.Model):
    """
    监控的程序ip
    """
    MonitorIP = models.ForeignKey("IpInterface", on_delete=models.CASCADE)
    port = models.CharField("监控端口", max_length=20)
    service_name = models.CharField("监控的服务名", max_length=200)

    class Meta:
        ordering = ["-service_name"]
        verbose_name_plural = "监控的服务"

    def __str__(self):
        return str(self.MonitorIP) + "--" + self.service_name


class SnapshotTask(models.Model):
    """
    保存创建的VM虚拟机定时快照设置
    注意具体任务的时间是用的charfield不是用的datatimefield
    """

    applicationIp = models.GenericIPAddressField("对应的虚拟机的ip")
    interval = models.IntegerField("间隔时间每x", blank=True, null=True)
    week_day = models.CharField("在每个星期几", max_length=10, blank=True, null=True)
    snap_date = models.CharField("在每个具体任务的时间", max_length=10, blank=True, null=True)
    timing_unit = models.CharField("计时单位", max_length=10, blank=True, null=True)

    class Meta:
        ordering = ["-applicationIp"]
        verbose_name_plural = "定时的快照"

    def __str__(self):
        return str(self.applicationIp)


