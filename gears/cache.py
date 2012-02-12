from __future__ import with_statement

from .asset_attributes import AssetAttributes
from .assets import Requirements, Asset


class CachedAsset(object):

    def __init__(self, asset):
        self.logical_path = asset.attributes.path
        self.absolute_path = asset.absolute_path

    def get_asset(self, environment):
        attributes = AssetAttributes(environment, self.logical_path)
        return Asset(attributes, self.absolute_path)


class CachedRequirements(object):

    def __init__(self, asset):
        self.before = [CachedAsset(r) for r in asset.requirements.before]
        self.after = [CachedAsset(r) for r in asset.requirements.after]

    def get_requirements(self, asset):
        environment = asset.attributes.environment
        requirements = Requirements(asset)
        requirements.before = [a.get_asset(environment) for a in self.before]
        requirements.after = [a.get_asset(environment) for a in self.after]
        return requirements


class Cache(dict):

    def expired(self, asset):
        return (asset.absolute_path not in self or
                asset.mtime > self[asset.absolute_path]['mtime'] or
                asset.hexdigest != self[asset.absolute_path]['hexdigest'])

    def set(self, asset):
        self[asset.absolute_path] = {
            'processed_source': asset.processed_source,
            'requirements': CachedRequirements(asset),
            'hexdigest': asset.hexdigest,
            'mtime': asset.mtime,
        }

    def get_processed_source(self, asset):
        return self[asset.absolute_path]['processed_source']

    def get_requirements(self, asset):
        cached_requirements = self[asset.absolute_path]['requirements']
        return cached_requirements.get_requirements(asset)
