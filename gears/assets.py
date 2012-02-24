from __future__ import with_statement

import codecs
import hashlib
import os

from .asset_attributes import AssetAttributes
from .utils import cached_property, unique


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
        return self._iter_unique()

    def __repr__(self):
        return '<Requirements before=%r after=%r>' % (self.before, self.after)

    @classmethod
    def from_dict(cls, asset, data):
        self = cls(asset)
        for absolute_path, logical_path in data['before']:
            self.add(self._asset_from_paths(absolute_path, logical_path))
        self.add(asset)
        for absolute_path, logical_path in data['after']:
            self.add(self._asset_from_paths(absolute_path, logical_path))
        return self

    @cached_property
    def expired(self):
        return (any(asset.bundle_expired for asset in self.before) or 
                any(asset.bundle_expired for asset in self.after))

    def add(self, asset):
        if asset is self.asset:
            self.current = self.after
        else:
            self.current.append(asset)

    def to_dict(self):
        return {'before': [self._paths_from_asset(asset) for asset in self.before],
                'after': [self._paths_from_asset(asset) for asset in self.after]}

    def _iter_requirements(self, assets):
        for asset in assets:
            for requirement in asset.requirements:
                yield requirement

    def _iter_all(self):
        for requirement in self._iter_requirements(self.before):
            yield requirement
        yield self.asset
        for requirement in self._iter_requirements(self.after):
            yield requirement

    def _iter_unique(self):
        return unique(self._iter_all(), key=lambda asset: asset.absolute_path)

    def _asset_from_paths(self, absolute_path, logical_path):
        attributes = AssetAttributes(self.asset.attributes.environment, logical_path)
        return Asset(attributes, absolute_path)

    def _paths_from_asset(self, asset):
        return (asset.absolute_path, asset.attributes.path)


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


class Asset(BaseAsset):

    def __init__(self, *args, **kwargs):
        super(Asset, self).__init__(*args, **kwargs)
        if self.expired:
            self.requirements = Requirements(self)
            self.processed_source = self.source
            for process in self.attributes.processors:
                process(self)
            self.attributes.environment.cache.set(self)
        else:
            self._init_from_cache()

    def __unicode__(self):
        return self.compressed_source

    def __str__(self):
        return unicode(self).encode('utf-8')

    @cached_property
    def source(self):
        with codecs.open(self.absolute_path, encoding='utf-8') as f:
            return f.read()

    @cached_property
    def bundled_source(self):
        data = self.attributes.environment.cache.get(self)
        if not self.bundle_expired and 'bundled_source' in data:
            return data['bundled_source']
        bundled_source = u'\n'.join(r.processed_source for r in self.requirements)
        data['bundled_source'] = bundled_source
        return bundled_source

    @cached_property
    def compressed_source(self):
        data = self.attributes.environment.cache.get(self)
        if not self.bundle_expired and 'compressed_source' in data:
            return data['compressed_source']
        compressed_source = self.bundled_source
        compress = self.attributes.compressor
        if compress:
            compressed_source = compress(self)
        data['compressed_source'] = compressed_source
        return compressed_source

    @cached_property
    def mtime(self):
        return os.stat(self.absolute_path).st_mtime

    @cached_property
    def hexdigest(self):
        return hashlib.sha1(self.source.encode('utf-8')).hexdigest()

    @cached_property
    def expired(self):
        data = self.attributes.environment.cache.get(self)
        return (data is None or
                self.mtime > data['mtime'] or
                self.hexdigest > data['hexdigest'])

    @cached_property
    def bundle_expired(self):
        return self.expired or self.requirements.expired

    def to_dict(self):
        return {'processed_source': self.processed_source,
                'requirements': self.requirements.to_dict(),
                'hexdigest': self.hexdigest,
                'mtime': self.mtime}

    def _init_from_cache(self):
        data = self.attributes.environment.cache.get(self)
        self.requirements = Requirements.from_dict(self, data['requirements'])
        self.processed_source = data['processed_source']



class StaticAsset(BaseAsset):

    @cached_property
    def source(self):
        with open(self.absolute_path, 'rb') as f:
            return f.read()


def build_asset(environment, path):
    asset_attributes = AssetAttributes(environment, path)
    asset_attributes, absolute_path = environment.find(asset_attributes, True)
    if not asset_attributes.processors:
        return StaticAsset(asset_attributes, absolute_path)
    return Asset(asset_attributes, absolute_path)
