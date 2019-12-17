# -*- coding: utf-8 -*-
import pymysql
from setting import MYSQL


class MysqlClass(object):

    def __init__(self):
        self.conn = pymysql.connect(**MYSQL)
        self.cursor = self.conn.cursor()
        self._sql = None

    def my_insert(self, table_name, artobj):
        # 通过title查询，是否已有数据
        sql_sele_str = 'select * from %s where title="%s"' % (table_name, artobj.art_dict['title'])
        result = self.cursor.execute(sql_sele_str)
        # 结果为0,新插入数据
        if result == 0:
            ls = [(k, v) for k, v in artobj.art_dict.items() if v is not None and v != '' and v != 'None']
            sql_ist_str = 'INSERT %s (' % table_name + ','.join([i[0] for i in ls]) + \
                          ') VALUES (' + ','.join(repr(i[1]) for i in ls) + ');'
            self.cursor.execute(sql_ist_str)
            self.conn.commit()
            print('保存数据成功：' + artobj.art_dict['title'])

    def close(self):
        self.cursor.close()
        self.conn.close()
