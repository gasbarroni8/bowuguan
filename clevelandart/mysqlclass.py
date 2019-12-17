# -*- coding: utf-8 -*-
import pymysql
from setting import MYSQL


class MysqlClass(object):

    def __init__(self):
        self.conn = pymysql.connect(**MYSQL)
        self.cursor = self.conn.cursor()
        self._sql = None

    def my_insert(self, artworkobj):
        query = ('insert into clevelandart values(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)')
        velues = (artworkobj.home_url.replace('"', '\''), artworkobj.data_url.replace('"', '\''),
                  artworkobj.img_min_url.replace('"', '\''), artworkobj.img_path.replace('"', '\''),
                  artworkobj.primary_title.replace('"', '\''), artworkobj.translated.replace('"', '\''),
                  artworkobj.creation_time.replace('"', '\''), artworkobj.artists.replace('"', '\''),
                  artworkobj.creation_year.replace('"', '\''), artworkobj.year_time.replace('"', '\''),
                  artworkobj.medium.replace('"', '\''), artworkobj.dimensions.replace('"', '\''),
                  artworkobj.credit_line.replace('"', '\''), artworkobj.accession_number.replace('"', '\''),
                  artworkobj.location.replace('"', '\''), artworkobj.description.replace('"', '\''),
                  artworkobj.artist_biography.replace('"', '\''), artworkobj.inscriptions.replace('"', '\''),
                  artworkobj.provenance.replace('"', '\''), artworkobj.classification.replace('"', '\''),
                  str(artworkobj.imgurl_list).replace('"', '\''))
        self.cursor.execute(query, velues)
        self.conn.commit()
        print('保存成功：' + artworkobj.primary_title)

    def close(self):
        self.cursor.close()
        self.conn.close()
