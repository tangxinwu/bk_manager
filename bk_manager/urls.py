"""bk_manager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from index import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^index/', views.index),  # 主页面
    url(r'^install_service/', views.install_service),  # 安装服务界面
    url(r'^data_gui/', views.data_gui),  # 关机页面
    url(r'^service_status/', views.service_status),  # 获取tomcat服务状态以及对tomcat进行操作
    url(r'^ip_interface/', views.ip_interface),  # 获取tomcat服务状态以及对tomcat进行操作
    url(r'^GenExcelFile/', views.make_to_excel),  # 获取自助获取excel的链接
    url(r'^docker_service/', views.docker_service),  # 获取自助获取excel的链接
    url(r'^vote/', views.vote),  # 投票的链接
    url(r'^get_vote_data/', views.get_vote_data),  # 获取投票数据的链接
    url(r'^vote_action/', views.vote_action),  # 获取投票数据的链接
    url('filter_option/', views.filter_option),  # 投票中过滤不符合部门的投票选项
    url('^login/', views.login),  # 登陆界面
    url(r'change_login/', views.change_login),  # 新版修改样机售机类型的登陆
    url(r'change_type/', views.change_type),  # 新版修改样机售机类型的界面
    url(r'logout/', views.logout),  # 注销页面
    # 数据统计url
    url(r"^server_type_count/$", views.server_type_count),  # 获取虚拟机和物理机的数据
    url(r"^os_count/$", views.os_count),  # 获取虚拟机和物理机的数据
    url(r"^test_environment/", views.test_environment),  # 测试环境功能
    url(r"^timer_snapshot/", views.timer_snapshot),  # 虚拟机定时快照
    url(r"^snapshot_status", views.snapshot_status),  # 后台创建snapshot的守护进程
    url(r"^test", views.test),  # test 接口
]
