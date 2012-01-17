from __future__ import with_statement

from .asset_attributes import AssetAttributes
from .call_stack import CallStack
from .exceptions import FileNotFound


class AssetAlreadyUsed(Exception):
    pass


class BaseAsset(object):

    def __init__(self, attributes, absolute_path, context=None, calls=None):
        self.attributes = attributes
        self.absolute_path = absolute_path
        self.context = context or {}
        self.calls = calls if calls is not None else CallStack()
        if self.absolute_path in self.calls:
            raise AssetAlreadyUsed(
                'Asset %r already used earlier.' % absolute_path)
        self.calls.add(self.absolute_path)

    def get_source(self):
        raise NotImplementedError()

    def get_cached_source(self):
        cache = self.attributes.environment.cache
        if not cache.is_modified(self.absolute_path):
            return cache.get_source(self.absolute_path)
        self.calls.push()
        source = self.get_source()
        dependencies = self.calls.pop()
        cache(self.absolute_path, source, dependencies)
        return source

    def __str__(self):
        return self.get_cached_source()


class Asset(BaseAsset):

    def get_source(self):
        with open(self.absolute_path, 'rb') as f:
            source = f.read()
        for processor_class in self.attributes.preprocessors:
            processor = processor_class(
                self.attributes, source, self.context, self.calls)
            source = processor.process()
        for engine in reversed(self.attributes.engines):
            source = engine.process(source, self.get_context())
        for processor_class in self.attributes.postprocessors:
            processor = processor_class(
                self.attributes, source, self.context, self.calls)
            source = processor.process()
        return source

    def get_context(self):
        context = self.context.copy()
        context['name'] = self.attributes.path_without_suffix
        context['absolute_path'] = self.absolute_path
        return context


class StaticAsset(BaseAsset):

    def get_source(self):
        with open(self.absolute_path, 'rb') as f:
            return f.read()


def build_asset(environment, path):
    if path not in environment.public_assets:
        raise FileNotFound(path)
    asset_attributes = AssetAttributes(environment, path)
    asset_attributes, absolute_path = environment.find(asset_attributes, True)
    if asset_attributes.is_static:
        return StaticAsset(asset_attributes, absolute_path)
    return Asset(asset_attributes, absolute_path, calls=CallStack())
