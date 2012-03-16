class Cache(dict):

    def set(self, key, value):
        self[key] = value

    def get(self, key):
        return super(Cache, self).get(key)
