
import redis

class RedisInterface(object):
    
    def __init__(self, ip, port = 6379, password = None, db = 0, redis_interface = None):

        self.ip   = ip
        self.port = port
        self.db = db
        self.password = password
        
        self._connection = None
        
        
    def get(self, key):
        '''Retrieve a Key from redis'''
        return self.connection.get(key)
    
    
    def set(self, key, value, ttl = None):
        '''TTL is in seconds, if None will never expire'''
        
        return self.connection.set(name = key, value = value, ex = ttl)
        
    def delete(self, key):
        return self.connection.delete(key = key)
    
    @property
    def connection(self):
        
        if self._connection == None:
            self._connection = redis.StrictRedis(host=self.ip, port=self.port, db=self.db)
        return self._connection
    
if __name__ == '__main__':
    a = RedisInterface('localhost', port = 6379)
