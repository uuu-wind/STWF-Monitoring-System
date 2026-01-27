from influxdb_client_3 import Point, InfluxDBClient3

class InfluxDBWriter:
    def __init__(self, host="https://localhost:8181", database="Wind", token=None):
        self.host = host
        self.database = database
        self.token = token
        self.client = self._create_client()

    def _create_client(self):
        return InfluxDBClient3(
            host = self.host,
            database = self.database,
            token = self.token
        )
    
    def write_data(self, measurement, tags=None, fields=None, time=None):
        try:
            point = Point(measurement)
            if tags:
                for key, value in tags.items():
                    point.tag(key, value)
            if fields:
                for key, value in fields.items():
                    point.field(key, value)
            if time:
                point.time(time)
            
            self.client.write(point)
            return True
        except Exception as e:
            print(f"Error writing data to InfluxDB: {e}")
            return False

    def close(self):
        if hasattr(self.client, 'close'):
            self.client.close()