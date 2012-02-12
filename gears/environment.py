from __future__ import with_statement

import os

from .asset_attributes import AssetAttributes
from .assets import build_asset
from .cache import Cache
from .engines import (
    CoffeeScriptEngine, HandlebarsEngine, LessEngine, StylusEngine)
from .exceptions import FileNotFound
from .processors import DirectivesProcessor


class Finders(list):

    def register(self, finder):
        if finder not in self:
            self.append(finder)

    def unregister(self, finder):
        if finder in self:
            self.remove(finder)


class MIMETypes(dict):

    def register_defaults(self):
        self.register('.css', 'text/css')
        self.register('.js', 'application/javascript')

    def register(self, extension, mimetype):
        self[extension] = mimetype

    def unregister(self, extension):
        if extension in self:
            del self[extension]


class Engines(dict):

    def __init__(self):
        super(Engines, self).__init__()

    def register_defaults(self):
        self.register('.coffee', CoffeeScriptEngine.as_engine())
        self.register('.handlebars', HandlebarsEngine.as_engine())
        self.register('.less', LessEngine.as_engine())
        self.register('.styl', StylusEngine.as_engine())

    def register(self, extension, engine):
        self[extension] = engine

    def unregister(self, extension):
        if extension in self:
            del self[extension]


class Processors(dict):

    def register(self, mimetype, processor_class):
        if mimetype not in self or processor_class not in self[mimetype]:
            self.setdefault(mimetype, []).append(processor_class)

    def unregister(self, mimetype, processor_class):
        if mimetype in self and processor_class in self[mimetype]:
            self[mimetype].remove(processor_class)

    def get(self, mimetype):
        return super(Processors, self).get(mimetype, [])


class Preprocessors(Processors):

    def register_defaults(self):
        self.register('text/css', DirectivesProcessor.as_processor())
        self.register('application/javascript', DirectivesProcessor.as_processor())


class Postprocessors(Processors):
    pass


class PublicAssets(list):

    def register_defaults(self):
        self.register('css/style.css')
        self.register('js/script.js')

    def register(self, path):
        if path not in self:
            self.append(path)

    def unregister(self, path):
        if path in self:
            self.remove(path)


class Suffixes(list):

    def register(self, extension, root=False, to=None, mimetype=None):
        if root:
            self.append({'extensions': [extension], 'mimetype': mimetype})
            return
        new = []
        for suffix in self:
            if to is not None and suffix['mimetype'] != to:
                continue
            extensions = list(suffix['extensions'])
            extensions.append(extension)
            new.append({'extensions': extensions, 'mimetype': mimetype})
        self.extend(new)

    def unregister(self, extension):
        for suffix in list(self):
            if extension in suffix['extensions']:
                self.remove(suffix)

    def find(self, *extensions):
        extensions = list(extensions)
        length = len(extensions)
        return [''.join(suffix['extensions']) for suffix in self
                if suffix['extensions'][:length] == extensions]


class Environment(object):

    def __init__(self, root):
        self.root = root
        self.cache = Cache()
        self.finders = Finders()
        self.engines = Engines()
        self.mimetypes = MIMETypes()
        self.public_assets = PublicAssets()
        self.preprocessors = Preprocessors()
        self.postprocessors = Postprocessors()

    @property
    def suffixes(self):
        if not hasattr(self, '_suffixes'):
            suffixes = Suffixes()
            for extension, mimetype in self.mimetypes.items():
                suffixes.register(extension, root=True, mimetype=mimetype)
            for extension, engine in self.engines.items():
                suffixes.register(extension, to=engine.result_mimetype)
            self._suffixes = suffixes
        return self._suffixes

    def register_defaults(self):
        self.engines.register_defaults()
        self.mimetypes.register_defaults()
        self.public_assets.register_defaults()
        self.preprocessors.register_defaults()

    def find(self, item, logical=False):
        if isinstance(item, AssetAttributes):
            for path in item.search_paths:
                try:
                    return self.find(path, logical)
                except FileNotFound:
                    continue
            raise FileNotFound(item.path)
        if isinstance(item, (list, tuple)):
            for path in item:
                try:
                    return self.find(path, logical)
                except FileNotFound:
                    continue
        elif logical:
            asset_attribute = AssetAttributes(self, item)
            path = asset_attribute.path_without_suffix
            for suffix in self.suffixes.find(*asset_attribute.suffix):
                try:
                    return self.find(path + suffix)
                except FileNotFound:
                    continue
        else:
            for finder in self.finders:
                try:
                    absolute_path = finder.find(item)
                except FileNotFound:
                    continue
                return AssetAttributes(self, item), absolute_path
        raise FileNotFound(item)

    def read(self, path, mode='rb'):
        with open(path, mode) as f:
            return f.read()

    def list(self, path, suffix=None):
        found = set()
        suffixes = self.suffixes.find(*suffix)
        for finder in self.finders:
            for logical_path, absolute_path in finder.list(path):
                asset_attributes = AssetAttributes(self, logical_path)
                if ''.join(asset_attributes.suffix) not in suffixes:
                    continue
                if logical_path not in found:
                    yield asset_attributes, absolute_path
                    found.add(logical_path)

    def save(self):
        for path in self.public_assets:
            try:
                self.save_file(path, str(build_asset(self, path)))
            except FileNotFound:
                pass

    def save_file(self, path, source):
        filename = os.path.join(self.root, path)
        path = os.path.dirname(filename)
        if not os.path.exists(path):
            os.makedirs(path)
        elif not os.path.isdir(path):
            raise OSError("%s exists and is not a directory." % path)
        with open(filename, 'w') as f:
            f.write(source)
