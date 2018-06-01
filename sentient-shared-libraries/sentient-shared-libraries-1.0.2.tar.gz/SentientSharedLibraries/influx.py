from influxdb import InfluxDBClient


class InfluxWrapper:
    def __init__(self,
                 db,
                 host,
                 port,
                 user,
                 password):
        self.db = db
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def write_influx(self, key, value):
        formatted_data = [{
            "measurement": key,
            "tags": {
                "sensor": key
            },
            "fields": {
                "value": value
            }
        }]
        conn = InfluxDBClient(self.host,
                              self.port,
                              self.user,
                              self.password,
                              self.db)
        conn.write_points(formatted_data)

    def read_influxdb(self, query):
        conn = InfluxDBClient(self.host,
                              self.port,
                              self.user,
                              self.password,
                              self.db)
        result = conn.query(query)

        return result