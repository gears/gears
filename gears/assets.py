import codecs
import hashlib
import os
import re

from .asset_attributes import AssetAttributes
from .compat import is_py3, str, UnicodeMixin
from .exceptions import GearsUnicodeError
from .utils import cached_property, unique


EXTENSION_RE = re.compile(r'(\.\w+)$')
FINGERPRINT_RE = re.compile(r'(\.[0-9a-f]{40})\.\w+$')


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


class Dependency(object):

    def __init__(self, environment, absolute_path):
        self.environment = environment
        self.absolute_path = absolute_path
        if self.expired:
            self._save_to_cache()

    def __eq__(self, other):
        return self.absolute_path == other.absolute_path

    def __hash__(self):
        return hash(self.absolute_path)

    @cached_property
    def source(self):
        if os.path.isdir(self.absolute_path):
            source = ', '.join(sorted(os.listdir(self.absolute_path)))
            return source.encode('utf-8') if is_py3 else source
        with open(self.absolute_path, 'rb') as f:
            return f.read()

    @cached_property
    def mtime(self):
        return os.stat(self.absolute_path).st_mtime

    @cached_property
    def hexdigest(self):
        return hashlib.sha1(self.source).hexdigest()

    @cached_property
    def expired(self):
        data = self.environment.cache.get(self._get_cache_key())
        return (data is None or
                self.mtime > data['mtime'] or
                self.hexdigest > data['hexdigest'])

    def to_dict(self):
        return {'mtime': self.mtime, 'hexdigest': self.hexdigest}

    def _save_to_cache(self):
        self.environment.cache.set(self._get_cache_key(), self.to_dict())

    def _get_cache_key(self):
        return 'dependency:%s' % self.absolute_path


class Dependencies(object):

    def __init__(self, environment):
        self.environment = environment
        self._registry = set()

    @classmethod
    def from_list(cls, environment, data):
        self = cls(environment)
        for absolute_path in data:
            self.add(absolute_path)
        return self

    @cached_property
    def expired(self):
        return any(d.expired for d in self._registry)

    @cached_property
    def mtime(self):
        if not self._registry:
            return None
        return max(d.mtime for d in self._registry)

    def add(self, absolute_path):
        self._registry.add(Dependency(self.environment, absolute_path))

    def clear(self):
        self._registry.clear()

    def to_list(self):
        return [d.absolute_path for d in self._registry]


class BaseAsset(object):

    gzippable = True

    def __init__(self, attributes, absolute_path, calls=None):
        self.attributes = attributes
        self.absolute_path = absolute_path

        self.calls = calls.copy() if calls else set()
        if self.absolute_path in self.calls:
            raise CircularDependencyError(self.absolute_path)
        self.calls.add(self.absolute_path)

    def __repr__(self):
        return '<%s absolute_path=%s>' % (self.__class__.__name__, self.absolute_path)

    @cached_property
    def is_public(self):
        environment = self.attributes.environment
        logical_path = os.path.normpath(self.attributes.logical_path)
        return environment.is_public(logical_path) or self.params.get('public')

    @cached_property
    def params(self):
        return {}

    @cached_property
    def hexdigest_path(self):
        return EXTENSION_RE.sub(
            r'.{0}\1'.format(self.final_hexdigest),
            self.attributes.logical_path,
        )


class Asset(UnicodeMixin, BaseAsset):

    def __init__(self, *args, **kwargs):
        super(Asset, self).__init__(*args, **kwargs)
        self.cache = self.attributes.environment.cache
        if self.expired:
            self.params.clear()
            self.dependencies.clear()
            self.requirements = Requirements(self)
            self.processed_source = self.source
            for process in self.attributes.processors:
                process(self)
            self._save_to_cache()
        else:
            self._init_from_cache()

    def __unicode__(self):
        return self.compressed_source

    def __iter__(self):
        return iter(str(self).encode('utf-8'))

    @property
    def cached_data(self):
        return self.cache.get(self._get_cache_key())

    @cached_property
    def params(self):
        if self.cached_data:
            return self.cached_data['params']
        return {}

    @cached_property
    def dependencies(self):
        if self.cached_data:
            data = self.cached_data['dependencies']
            return Dependencies.from_list(self.attributes.environment, data)
        return Dependencies(self.attributes.environment)

    @cached_property
    def source(self):
        try:
            with codecs.open(self.absolute_path, encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError as e:
            raise GearsUnicodeError(self.absolute_path, str(e))

    @cached_property
    def bundled_source(self):
        cache_key = self._get_cache_key('bundled_source')
        if not self.bundle_expired:
            bundled_source = self.cache.get(cache_key)
            if bundled_source is not None:
                return bundled_source
        bundled_source = '\n'.join(r.processed_source for r in self.requirements)
        self.cache.set(cache_key, bundled_source)
        return bundled_source

    @cached_property
    def compressed_source(self):
        cache_key = self._get_cache_key('compressed_source')
        if not self.bundle_expired:
            compressed_source = self.cache.get(cache_key)
            if compressed_source is not None:
                return compressed_source
        compressed_source = self.bundled_source
        compress = self.attributes.compressor
        if compress:
            compressed_source = compress(self)
        self.cache.set(cache_key, compressed_source)
        return compressed_source

    @cached_property
    def mtime(self):
        mtime = os.stat(self.absolute_path).st_mtime
        if self.dependencies.mtime is not None:
            return max(mtime, self.dependencies.mtime)
        return mtime

    @cached_property
    def hexdigest(self):
        return hashlib.sha1(self.source.encode('utf-8')).hexdigest()

    @cached_property
    def final_hexdigest(self):
        return hashlib.sha1(self.compressed_source.encode('utf-8')).hexdigest()

    @cached_property
    def expired(self):
        return (self.cached_data is None or
                self.mtime > self.cached_data['mtime'] or
                self.hexdigest > self.cached_data['hexdigest'] or
                self.dependencies.expired)

    @cached_property
    def bundle_expired(self):
        return self.expired or self.requirements.expired

    def to_dict(self):
        return {'processed_source': self.processed_source,
                'requirements': self.requirements.to_dict(),
                'dependencies': self.dependencies.to_list(),
                'params': self.params,
                'hexdigest': self.hexdigest,
                'mtime': self.mtime}

    def _init_from_cache(self):
        self.params = self.cached_data['params']
        self.dependencies = Dependencies.from_list(
            self.attributes.environment,
            self.cached_data['dependencies'])
        self.requirements = Requirements.from_dict(self, self.cached_data['requirements'])
        self.processed_source = self.cached_data['processed_source']

    def _save_to_cache(self):
        self.cache.set(self._get_cache_key(), self.to_dict())

    def _get_cache_key(self, suffix='data'):
        return 'asset:%s:%s' % (self.absolute_path, suffix)


class StaticAsset(BaseAsset):

    gzippable = False

    @cached_property
    def source(self):
        with open(self.absolute_path, 'rb') as f:
            return f.read()

    @cached_property
    def mtime(self):
        return os.stat(self.absolute_path).st_mtime

    @cached_property
    def hexdigest(self):
        return hashlib.sha1(self.source).hexdigest()

    @cached_property
    def final_hexdigest(self):
        return self.hexdigest

    def __iter__(self):
        return iter(self.source)


class CheckAsset(BaseAsset):

    def __init__(self, *args, **kwargs):
        super(CheckAsset, self).__init__(*args, **kwargs)
        self.processed_source = self.source
        for process in self.attributes.processors:
            if getattr(process, 'supports_check_mode', False):
                process(self, check=True)

    @cached_property
    def source(self):
        try:
            with codecs.open(self.absolute_path, encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError as e:
            raise GearsUnicodeError(self.absolute_path, str(e))


def build_asset(environment, path, check=False):
    path = strip_fingerprint(path)
    asset_attributes = AssetAttributes(environment, path)
    asset_attributes, absolute_path = environment.find(asset_attributes, True)
    if not asset_attributes.processors:
        return StaticAsset(asset_attributes, absolute_path)
    if check:
        return CheckAsset(asset_attributes, absolute_path)
    return Asset(asset_attributes, absolute_path)


def strip_fingerprint(path):
    match = FINGERPRINT_RE.search(path)
    if not match:
        return path
    fingerprint = match.group(1)
    return path.replace(fingerprint, '')
