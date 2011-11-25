from .asset_attributes import AssetAttributes
from .processors import DirectivesProcessor
from .utils import first, first_or_none


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

    def register(self, extension, engine):
        self[extension] = engine

    def unregister(self, extension):
        if extension in self:
            del self[extension]


class Processors(dict):

    def register(self, mimetype, processor_class):
        self.setdefault(mimetype, []).append(processor_class)

    def unregister(self, mimetype, processor_class):
        if mimetype in self and processor_class in self[mimetype]:
            self[mimetype].remove(processor_class)

    def get(self, mimetype):
        return super(Processors, self).get(mimetype, [])


class Preprocessors(Processors):

    def register_defaults(self):
        self.register('text/css', DirectivesProcessor)
        self.register('application/javascript', DirectivesProcessor)


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
        for suffix in self:
            if extension in self['extensions']:
                self.remove(suffix)

    def find(self, *extensions):
        extensions = list(extensions)
        length = len(extensions)
        return [''.join(suffix['extensions']) for suffix in self
                if suffix['extensions'][:length] == extensions]


class Environment(object):

    def __init__(self, root):
        self.root = root
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
        self.mimetypes.register_defaults()
        self.public_assets.register_defaults()
        self.preprocessors.register_defaults()

    def find(self, item, logical=False):
        if isinstance(item, AssetAttributes):
            return self.find(item.search_paths, logical)
        if isinstance(item, (list, tuple)):
            try:
                return first(all, (self.find(p, logical) for p in item))
            except ValueError:
                return None, None
        if logical:
            asset_attribute = AssetAttributes(self, item)
            path = asset_attribute.path_without_extensions
            suffixes = self.suffixes.find(*asset_attribute.suffix)
            try:
                return first(all, (self.find(path + s) for s in suffixes))
            except ValueError:
                return None, None
        path = first_or_none(bool, (f.find(item) for f in self.finders))
        if path:
            return AssetAttributes(self, item), path
        return None, None
