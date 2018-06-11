#! coding=utf-8
"""
处理定时快照的守护进程
"""

import sqlite3
import time
import datetime
import threading
import schedule


try:
    import index.create_snapshot_txw as CSST
except ImportError:
    import create_snapshot_txw as CSST


class MakeSnapshotThreading:
    """
    把创建快照的方法 封装成一个可调用的类

    """
    def __init__(self, ip):
        self.ip = ip

    def _snapshot(self):
        """
        封装的创建快照的内置方法
        :return:
        """
        p = CSST.CreateSnapshot(SSL=False)
        p.build_arg_parser()
        p.add_argument(host=self.ip,
                       name=str(datetime.datetime.now()),
                       description="Created by Daemon server!",
                       memory=True,
                       quiesce=False)
        p.handler()

    def _transfor_to_threading(self):
        """
        创建快照转成线程模式启动
        :return:
        """

        threading.Thread(target=self._snapshot).start()

    def __call__(self, *args, **kwargs):
        """
        使得类的实例可以被调用
        :param args:
        :param kwargs:
        :return:
        """
        self._transfor_to_threading()


class MakeSnapshotMethod:
    """
    根据参数返回对应创建snapshot的方法
    schedule 方法使用样例
    schedule.every(10).minutes.do(job)
    schedule.every().hour.do(job)
    schedule.every().day.at("10:30").do(job)
    schedule.every(5).to(10).days.do(job)
    schedule.every().monday.do(job)
    schedule.every().wednesday.at("13:15").do(job)
    """
    def __init__(self, params):
        self._params = params
        self._interval = self._params.get("interval")
        self._week_day = self._params.get("week_day")
        self._timing_unit = self._params.get("timing_unit")
        self._snap_date = self._params.get("snap_date")

    def make_process(self):
        if self._interval:
            return getattr(getattr(getattr(schedule, "every")(self._interval), self._timing_unit), "do")
        else:
            if self._week_day and self._snap_date:
                return getattr(getattr(getattr(getattr(schedule, "every")(), self._week_day), "at")(self._snap_date), "do")
            if self._week_day and not self._snap_date:
                return getattr(getattr(getattr(schedule, "every")(), self._week_day), "do")
            if not self._week_day and self._snap_date:
                return getattr(getattr(getattr(getattr(schedule, "every")(), "day"), "at")(self._snap_date), "do")
        return "Error"


def timer_task():
    """
    定时任务函数,收集所有定时任务
    :var schedule_list:保存由类MakeThreading创建实例，用于定时任务(schedule)的调用,因为不能传参数
    :var connection: 保存sqlite3 连接
    :var cur: 指针游标
    :var data: 数据库中查到的所有定时任务
    :return:
    """
    schedule_list = list()
    task_list = list()
    params = dict()
    connection = sqlite3.connect("/home/tang/Desktop/old_backup/bk_manager/db.sqlite3")
    cur = connection.cursor()
    cur.execute("""SELECT * FROM index_snapshottask""")
    data = cur.fetchall()

    for task in data:
        params["ip"] = task[1]
        params["interval"] = task[2]
        params["week_day"] = task[3]
        params["timing_unit"] = task[4]
        params["snap_date"] = task[5]
        task_list.append(MakeSnapshotMethod(params))
        schedule_list.append(MakeSnapshotThreading(params["ip"]))
        # 为什么要重置下 不是可以替换属性的吗？ 这里不重置的话 params 的值不会被覆盖....
        params = dict()

    for threading_task in zip(task_list, schedule_list):
        threading_task[0].make_process()(threading_task[1])

    while True:
        schedule.run_pending()
        time.sleep(1)g



if __name__ == "__main__":
    timer_task()




