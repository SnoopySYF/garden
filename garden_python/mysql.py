import MySQLdb

class GMysql:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = "root"
        self.databases = "garden"
    
    def connection_garden(self):
        db = MySQLdb.connect(self.host, self.user, self.password, self.databases, charset='utf8')
        return db

    """
    查询所有的品牌名
    返回集合：
    b_id: 品牌id
    b_name: 品牌名
    """
    def select_brands(self):
        db = self.connection_garden()
        cursor = db.cursor()
        # SQL 查询语句
        sql = "SELECT * FROM brands"
        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 获取所有记录列表
            results = cursor.fetchall()
        except:
            print("Error: unable to fecth data")

        # 关闭数据库连接
        db.close()
        return results

    """
    查询某个品牌名下的所有系列
    输入：
    b_id: 品牌id
    返回集合：
    s_id: 系列id
    s_name: 系列名
    b_id: 品牌id
    """
    def select_series(self, b_id):
        db = self.connection_garden()
        cursor = db.cursor()
        # SQL 查询语句
        sql = "SELECT * FROM series WHERE b_id = %d" % (b_id)
        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 获取所有记录列表
            results = cursor.fetchall()
        except:
            print("Error: unable to fecth data")

        # 关闭数据库连接
        db.close()
        return results

    """
    查询某个品牌名下某个系列的所有色号
    输入：
    s_id: 系列id
    返回集合：
    l_id: 色号id
    color: 色号RGB
    id: 该色号id信息
    l_name: 该色号名字
    s_id: 系列id
    """
    def select_lipsticks(self, s_id):
        db = self.connection_garden()
        cursor = db.cursor()
        # SQL 查询语句
        sql = "SELECT * FROM lipsticks WHERE s_id = %d" % (s_id)
        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 获取所有记录列表
            results = cursor.fetchall()
        except:
            print("Error: unable to fecth data")

        # 关闭数据库连接
        db.close()
        return results

