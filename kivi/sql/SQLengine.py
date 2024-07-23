class __ConnectSQL__:

    def __init__(self, dataBase, ConnectInfo):
        self.dataBase = dataBase
        self.ConnectInfo = ConnectInfo
        self.ConnectInfo['dataBase'] = dataBase

    def __connectInfo__(self, dataBaseType, name, password, host, prot, dataBase):
        if dataBaseType == 'MySql':
            CONNECT = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=UTF8MB4'.format(
                name, password, host, prot, dataBase)
            return CONNECT
        if dataBaseType == 'Oracle':
            CONNECT = 'oracle+cx_oracle://{}:{}@{}:{}/{}'.format(
                name, password, host, prot, dataBase)
            return CONNECT

    def engine(self, ):
        from sqlalchemy import create_engine
        CONNECT = self.__connectInfo__(**self.ConnectInfo)
        engin = create_engine(CONNECT)
        print('Connect to {} success!'.format(CONNECT))
        return engin


class ShowDataBase:

    def __init__(self, engin):
        from sqlalchemy import inspect
        self.inspector = inspect(engin)

    def showTable(self, ):
        tablesName = self.inspector.get_table_names()
        return tablesName

    def showColumns(self, tableName):
        columns = [
            col['name'] for col in self.inspector.get_columns(tableName)
        ]
        return columns


def GetSqlEngine(dataBaseName, connectInfo):
    """
    :param dataBaseName: dataBaseName
    :param connectInfo: e.g.
        connectInfo = {
            'dataBaseType': 'MySql' or 'Oracle',
            'name': 'root',
            'password': '********',
            'host': 'localhost',
            'prot': '3306',
        }
    :return: engine
    """
    connectSql = __ConnectSQL__(dataBaseName, connectInfo)
    return connectSql.engine()


class MySql:
    def __init__(self, host='localhost', port='3306', user='root', password='1702', spark=None):
        self.host = host
        self.port = port
        self.spark = spark
        self.prop = {
            'user': user,
            'password': password,
        }
        
    def getPyUrl(self, db):
        """
        获取Pandas URL
        """
        url = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=UTF8MB4'.format(
            self.prop.get('user'), self.prop.get('password'), 
            self.host, self.port, db)
        return url
    
    def getEngin(self, db):
        """
        获取Pandas URL链接引擎
        """
        from sqlalchemy import create_engine
        return create_engine(self.getPyUrl(db))
        
    def getSparkUrl(self, db):
        """
        获取PySpark DataFrame URL链接引擎
        """
        url = f'jdbc:mysql://{self.host}:{self.port}/{db}'
        return url
    
    def readMySql(self, db, table):
        """
        读取MySQL至PySpark DataFrame
        """
        url = self.getSparkUrl(db)
        df = self.spark.read.jdbc(url=url, table=table, properties=self.prop)
        return df
    
    def writeTable(self, df, db, table_name, mode='error'):
        """
        描述：保存PySpark DataFrame到MySQL
        
        参数：
        :param df:
        :param db:
        :param table_name:
        :param mode:
            * ``append``: Append contents of this :class:`DataFrame` to existing data.
            * ``overwrite``: Overwrite existing data.
            * ``ignore``: Silently ignore this operation if data already exists.
            * ``error`` or ``errorifexists`` (default case): Throw an exception if data already   
        """
        url = self.getSparkUrl(db)
        df.write.jdbc(url=url, table=table_name, mode=mode, properties=self.prop)
        return None
    

    
def dropTable(table_name, con):
    """
    删除表
    """
    from sqlalchemy.orm import sessionmaker
    session = sessionmaker(con)
    tables = ShowDataBase(con).showTable()
    if table_name in tables:
        print("查询到表：{}。".format(table_name))
        confirm = input('确认删除请输入‘y’: ')
    else:
        print("查询到表：{} 不存在。".format(table_name))
    if confirm == 'y':
        with con.connect() as connection:
            with session(bind=connection) as sess:
                sess.execute("DROP TABLE IF EXISTS {}".format(table_name))
        print('Droped Table: {}'.format(table_name))
    return None


def checkTableExists():
    """
    描述：检查表是否存在
    """
    return None

def renameTable():
    """
    描述：对表进行重命名
    """
    return None

