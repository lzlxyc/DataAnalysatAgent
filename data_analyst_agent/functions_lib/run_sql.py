import json
import pymysql
import pandas as pd


SQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'passwd': 'root',
    'db': 'telco_db',  # 数据库名
    'charset': 'utf8'  # 字符集选择utf8
}

def extract_data(sql_query,df_name,g='globals()'):
    """
    借助pymysql将MySQL中的某张表读取并保存到本地Python环境中。
    :param sql_query: 字符串形式的SQL查询语句，用于提取MySQL中的某张表。
    :param df_name: 将MySQL数据库中提取的表格进行本地保存时的变量名，以字符串形式表示。
    :param g: g，字符串形式变量，表示环境变量，无需设置，保持默认参数即可
    :return：表格读取和保存结果
    """
    # connection = pymysql.connect(
    #         host='localhost',  # 数据库地址
    #         user='root',  # 数据库用户名
    #         passwd='root',  # 数据库密码
    #         db='telco_db',  # 数据库名
    #         charset='utf8'  # 字符集选择utf8
    #     )
    connection = pymysql.connect(**SQL_CONFIG)

    g[df_name] = pd.read_sql(sql_query, connection)

    connection.close()

    return "已成功完成%s变量创建" % df_name

def sql_inter(sql_query, **kargs):
    """
    用于执行一段SQL代码，并最终获取SQL代码执行结果，\
    核心功能是将输入的SQL代码传输至MySQL环境中进行运行，\
    并最终返回SQL代码运行结果。需要注意的是，本函数是借助pymysql来连接MySQL数据库。
    :param sql_query: 字符串形式的SQL查询语句，用于执行对MySQL中telco_db数据库中各张表进行查询，并获得各表中的各类相关信息
    :return：sql_query在MySQL中的运行结果。
    """
    connection = pymysql.connect(**SQL_CONFIG)

    try:
        with connection.cursor() as cursor:
            # SQL查询语句
            sql = sql_query
            cursor.execute(sql)

            # 获取查询结果
            results = cursor.fetchall()

    finally:
        connection.close()


    return json.dumps(results)


