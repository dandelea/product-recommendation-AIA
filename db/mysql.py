
import mysql.connector

class Connection:

    def __init__(self, user, password, host, schema):
        self.user = user
        self.password = password
        self.host = host
        self.schema = schema
        self.connection = None
        self.connected = False

    def open(self):
        if not self.connected:
            self.connection = mysql.connector.connect(
                user=self.user, password=self.password,
                host=self.host, database=self.schema)
            self.connected = True
    connect = open

    def close(self):
        if self.connected:
            self.connection.close()
            self.connection = None
            self.connected = False
    disconnect = close

    def query(self, sql):
        cursor = self.connection.cursor()
        cursor.execute(sql)
        result = list(cursor)
        cursor.close()
        return result
