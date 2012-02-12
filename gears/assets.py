from __future__ import with_statement

from .asset_attributes import AssetAttributes
from .utils import cached_property


class CircularDependencyError(Exception):

    def __init__(self, absolute_path):
        self.absolute_path = absolute_path

    def __str__(self):
        return '%s has already been required' % self.absolute_path


class Requirements(object):

    def __init__(self, asset):
        self.current = self.before = []
        self.after = []
        self.asset = asset

    def __iter__(self):
        yielded = set()
        for asset in self.before:
            for requirement in asset.requirements:
                if requirement.absolute_path not in yielded:
                    yield requirement
                    yielded.add(requirement.absolute_path)
        yield self.asset
        yielded.add(self.asset.absolute_path)
        for asset in self.after:
            for requirement in asset.requirements:
                if requirement.absolute_path not in yielded:
                    yield requirement
                    yielded.add(requirement.absolute_path)

    def __repr__(self):
        return '<Requirements before=%r after=%r>' % (self.before, self.after)

    def add(self, asset):
        if asset is self.asset:
            self.current = self.after
        else:
            self.current.append(asset)


class BaseAsset(object):

    def __init__(self, attributes, absolute_path, calls=None):
        self.attributes = attributes
        self.absolute_path = absolute_path

        self.calls = calls.copy() if calls else set()
        if self.absolute_path in self.calls:
            raise CircularDependencyError(self.absolute_path)
        self.calls.add(self.absolute_path)

    def __str__(self):
        return self.source

    def __repr__(self):
        return '<%s absolute_path=%s>' % (self.__class__.__name__, self.absolute_path)

    @cached_property
    def source(self):
        return self.attributes.environment.read(self.absolute_path)


class Asset(BaseAsset):

    def __init__(self, *args, **kwargs):
        super(Asset, self).__init__(*args, **kwargs)
        self.requirements = Requirements(self)
        self.processed_source = self.source
        for process in self.attributes.processors:
            process(self)


class StaticAsset(BaseAsset):

    def get_source(self):
        with open(self.absolute_path, 'rb') as f:
            return f.read()


def build_asset(environment, path):
    asset_attributes = AssetAttributes(environment, path)
    asset_attributes, absolute_path = environment.find(asset_attributes, True)
    if not asset_attributes.processors:
        return StaticAsset(asset_attributes, absolute_path)
    return Asset(asset_attributes, absolute_path)
