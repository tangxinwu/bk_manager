#!coding=utf-8

"""
生成excel的类
"""
import pymysql
import openpyxl

f6s_machine_CHOICES = {
    0 : '爱夫卡合格',
    1 : '爱夫卡不合格',
    2 : '其他品牌合格',
    3 : '其他品牌不合格',
    }

f7s_machine_CHOICES = {
    0 : '爱夫卡合格',
    1 : '爱夫卡不合格',
    2 : '其他品牌合格',
    3 : '其他品牌不合格',
    4 : 'PC版合格',
    5 : 'PC版不合格',
    }


class MakeToExcel:
    def __init__(self, host_List, sql,type):
        self.host_list = host_List
        self.sql = sql
        self.type = type
        self.carclass_dict = ''
        self.cargroup_dict = ''

    def get_data(self):
        conn = pymysql.connect(self.host_list['hostname'], self.host_list['username'], self.host_list['password'],self.host_list['database'],charset='utf8')
        cur = conn.cursor()
        cur.execute(self.sql)
        self.data = cur.fetchall()
        cur.execute("""select id,cnname from www_tbcarclass""")
        self.carclass_dict = dict(cur.fetchall())
        cur.execute("""select id,cnname from www_tbcargroup""")
        self.cargroup_dict = dict(cur.fetchall())

    def to_execl(self, filename, data,title):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(title)
        for i in range(len(data)):
            if self.type == 'wenkong_zhuanjia':
                if not data[i][1]:continue
            if self.type == 'f6shuanji':
                modified_data = list(data[i])
                modified_data[9] = f6s_machine_CHOICES[modified_data[9]]
                ws.append(modified_data)
                continue
            if self.type == 'f7shuanji':
                modified_data = list(data[i])
                modified_data[9] = f7s_machine_CHOICES[modified_data[9]]
                ws.append(modified_data)
                continue
            if self.type == 'carlist':
                if not data[i][1]:continue
            if self.type == 'banbenfabu_list':
                modified_data = list(data[i])
                modified_data[4] = self.carclass_dict[modified_data[4]]
                modified_data[5] = self.cargroup_dict[modified_data[5]]
                if modified_data[0].endswith('0'):
                    modified_data.extend('是')
                else:
                    modified_data.extend('否')
                ws.append(modified_data)
                continue

            ws.append(data[i])
        wb.save(filename + '.xlsx')


if __name__ == '__main__':
    host_list = {
            'hostname': 'yun1.szfcar.com',
            'username': 'root',
            'password': 'fcar.8',
            'database' : 'www',

                }

    ## 文控倒版本用的
    #sql = """select (select name from www_tbmachine where id=machine_id),(select cnname from www_tbcarlist where id=carlist_id),(select cnname from www_tblang where id=lang_id),ver,chkdate from www_tbverlist where chkdate is not NULL ;"""

    ## f6s 换机
    #sql = """select * from sh_tbreplace"""
    #title = ('id','换机日期','快递名称','快递单号','发货人','发货人电话','发货人地址','区域','市场人员','机器属性','机器型号','机器序列号','发货日期','发货数量','单价','金额','回款','备注','创建时间','修改时间',)
    ## f7s 换机
    #sql = """select * from sh_tbreplacec"""
    #title = ('id', '换机日期', '快递名称', '快递单号', '发货人', '发货人电话', '发货人地址', '区域', '市场人员', '机器属性', '机器型号', '机器序列号', '发货日期', '发货数量', '单价','金额', '回款', '备注', '创建时间', '修改时间',)
    #sql = """select (select name from www_tbmachine where id=machine_id),(select cnname from www_tbcarlist where id=carlist_id and cnname like "%%专家%%"),(select cnname from www_tblang where id=lang_id),ver,chkdate from www_tbverlist where chkdate is NULL ;"""
    title = ('版本号','发布日期','车型名','语言','车系','车组','是否为大版本')
    sql = """select ver,datetime,(select cnname from www_tbcarlist where id=carlist_id),(select cnname from www_tblang where id=lang_id ),(select carclass_id from www_tbcarlist where id=carlist_id),(select cargroup_id from www_tbcarlist where id=carlist_id) from www_tbverlist where chkdate;"""
    p = MakeToExcel(host_list, sql,'banbenfabu_list')
    p.get_data()
    # for i in range(len(p.data)):
    #     if p.data[i][4] == 3:
    #         print(p.data[i])
    #print(sorted(p.carclass_dict))
    print(p.data)
    p.to_execl('ttt', p.data,title)

