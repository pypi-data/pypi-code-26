import MySQLdb
import MySQLdb.cursors
from testosterone.runner import TestosteroneRunner

DB_REGISTRY = {}


class DBWrapper(object):
    def __init__(self, name, **config):
        self.name = name
        self.config = config
        self.ssh_tunnel = None
        self._connection = None
        self._cursor = None

    @property
    def connection(self):
        """

        @return: Connection
        """
        if not self._connection:
            if "ssh_tunnel" in self.config and self.config["ssh_tunnel"]:
                from sshtunnel import SSHTunnelForwarder
                tunnel_config = self.config["ssh_tunnel"]
                self.ssh_tunnel = SSHTunnelForwarder(
                    tunnel_config["host"],
                    remote_bind_address=('127.0.0.1', self.config.get("port", 3306))
                )

                self.ssh_tunnel.start()

                self.config["host"] = "127.0.0.1"
                self.config["port"] = self.ssh_tunnel.local_bind_port

            connect_params = dict(
                host=self.config["host"], user=self.config.get("user", "root"),
                passwd=self.config["password"], db=self.config["dbname"], port=self.config["port"],
                cursorclass=MySQLdb.cursors.DictCursor)

            self._connection = MySQLdb.connect(**connect_params)

        return self._connection

    @property
    def cursor(self):
        if not self._cursor:
            self._cursor = self.connection.cursor()
        return self._cursor

    def get(self, table_name, query):
        where_clause = " AND ".join(["%s = '%s'" % (k, v) for k, v in query.items()])
        sql = "SELECT * FROM %s where %s" % (table_name, where_clause)
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def shutdown(self):
        if self.ssh_tunnel:
            self.ssh_tunnel.stop()

    def sql(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()


def DB(name="default"):
    """
    @type name: str
    @rtype: DBWrapper
    """
    if name in DB_REGISTRY:
        return DB_REGISTRY[name]

    try:
        db_config = TestosteroneRunner.get_instance().config["db"][name]
    except KeyError:
        print("Web '%s' is not configured" % name)
        exit(3)
        return

    db = DBWrapper(name, **db_config)

    DB_REGISTRY[name] = db
    return db

