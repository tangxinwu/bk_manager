import datetime


class MakeLog:
    """
    写日志类
    """
    def __init__(self, log_path):
        """
        初始化MakeLog
        :param log_path:
        """
        self.log_path = log_path
        self._file = open(self.log_path, "a+")

    def write(self, log):
        """
        写入日志文件自动分行
        :return:
        """
        log_date = str(datetime.datetime.now()).split(".")[0]
        log_content = log_date + " " + log
        print(log_content, file=self._file)

    def close(self):
        """
        关闭文件
        :return:
        """
        self._file.close()
