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


class Asset(BaseAsset):

    def __init__(self, *args, **kwargs):
        super(Asset, self).__init__(*args, **kwargs)
        cache = self.attributes.environment.cache
        if cache.expired(self):
            self.requirements = Requirements(self)
            self.processed_source = self.source
            for process in self.attributes.processors:
                process(self)
            cache.set(self)
        else:
            self.requirements = cache.get_requirements(self)
            self.processed_source = cache.get_processed_source(self)

    def __unicode__(self):
        return self.bundled_source

    def __str__(self):
        return unicode(self).encode('utf-8')

    @cached_property
    def source(self):
        with codecs.open(self.absolute_path, encoding='utf-8') as f:
            return f.read()

    @cached_property
    def bundled_source(self):
        return u'\n'.join(r.processed_source for r in self.requirements)

    @cached_property
    def mtime(self):
        return os.stat(self.absolute_path).st_mtime

    @cached_property
    def hexdigest(self):
        return hashlib.sha1(self.source.encode('utf-8')).hexdigest()


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
