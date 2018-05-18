from django.contrib import admin
from index.models import *

# Register your models here.


class OStype_admin(admin.ModelAdmin):
    list_display = ("OS_name",)
    search_fields = ("OS_name",)


admin.site.register(OStype, OStype_admin)


class Hardware_admin(admin.ModelAdmin):
    list_display = ("hardware_type",)
    search_fields = ("hardware_type",)


admin.site.register(Hardware, Hardware_admin)


class IpInterface_admin(admin.ModelAdmin):
    list_display = ("ipaddr", "function", "username", "password", "comment", "domain_name", "OS_type", "especily", "hardware_type")
    search_fields = ("ipaddr", "function")


admin.site.register(IpInterface, IpInterface_admin)


class DockerServiceList_admin(admin.ModelAdmin):
    list_display = ("serviceName", "mappedPort", "serviceStatus", "isInSwarm","comment")
    search_fields = ("serviceName",)


admin.site.register(DockerServiceList, DockerServiceList_admin)


class Department_admin(admin.ModelAdmin):
    list_display = ["department_name"]
    list_filter = ["department_name"]


class VoteData_admin(admin.ModelAdmin):
    list_display = ["voter", "voter_ip", "department_name"]
    list_filter = ["voter"]


class VoteOption_admin(admin.ModelAdmin):
    list_display = ["OptionName", "belongToDepartment"]
    list_filter = ["OptionName"]


admin.site.register(Department, Department_admin)
admin.site.register(VoteData, VoteData_admin)
admin.site.register(VoteOption, VoteOption_admin)


class LogAccount_admin(admin.ModelAdmin):
    list_display = ["email", "password"]
    search_fields = ["email"]


admin.site.register(LogAccount, LogAccount_admin)


class MonitorService_admin(admin.ModelAdmin):
    list_display = ["MonitorIP", "port", "service_name",]
    search_fields = ["service_name",]


admin.site.register(MonitorService, MonitorService_admin)
