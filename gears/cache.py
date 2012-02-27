class Cache(dict):

    def set(self, asset):
        self[asset.absolute_path] = asset.to_dict()

    def get(self, asset):
        return super(Cache, self).get(asset.absolute_path)
