# -*- encoding: utf-8 -*- 
''' 
@File : Sql_connect.py 
@Description: None
@Contact : goaza123@sina.com
<<<<<<< HEAD
@Created info: Susie 2019-11-26 16:35
=======
@Created info: Susie 2019-11-26 16:35
>>>>>>> b50fc0789fea87eab8d21eb0da2d398abe079ae4
''' 


from sqlalchemy import create_engine
import pandas as pd
import io
import datetime
from string import Template

class Connect(object):
    def __init__(self,database):
        self.database=database
        self.pg_username="postgres"
        self.pg_password='******'
        self.pg_port="5432"
        self.pg_host="localhost"
        self.engine = create_engine('postgresql+psycopg2://' + self.pg_username + ':' + self.pg_password + '@' + self.pg_host + ':' + str(
            self.pg_port) + '/' + database)
        print('连接数据库成功')
# query_sql = 'select * from $arg1'
# query_sql = Template(query_sql) # template方法
    def load(self,file):
        query_sql = Template('select * from $arg1')
        df = pd.read_sql_query(query_sql.substitute(arg1=file),self.engine) # 配合pandas的方法读取数据库值
        return df
# 配合pandas的to_sql方法使用十分方便（dataframe对象直接入库）
    def upload(self,file,table_name, if_exists='fail'):
        if type(file)==str:
            df=pd.read_excel(file)
            print('获取本地表完成')
        else:
            df=file
        df['update_time']=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        string_data_io = io.StringIO()
        df.to_csv(string_data_io, sep='|', index=False)
        pd_sql_engine = pd.io.sql.pandasSQL_builder(self.engine)
        table = pd.io.sql.SQLTable(table_name, pd_sql_engine, frame=df,
                                   index=False, if_exists=if_exists)
        table.create()
        string_data_io.seek(0)
        # string_data_io.readline()  # remove header
        with self.engine.connect() as connection:
            with connection.connection.cursor() as cursor:
                copy_cmd = "COPY %s FROM STDIN HEADER DELIMITER '|' CSV" % table_name
                cursor.copy_expert(copy_cmd, string_data_io)
            connection.connection.commit()
        print('数据上传完成')
