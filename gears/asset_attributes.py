import os
import re
from .utils import cached_property


class AssetAttributes(object):

    def __init__(self, environment, path):
        self.environment = environment
        self.path = path

    @cached_property
    def search_paths(self):
        paths = [self.path]
        if os.path.basename(self.path_without_extensions) != 'index':
            path = os.path.join(self.path_without_extensions, 'index')
            paths.append(path + ''.join(self.extensions))
        return paths

    @cached_property
    def path_without_extensions(self):
        if self.extensions:
            return self.path[:-len(''.join(self.extensions))]
        return self.path

    @cached_property
    def extensions(self):
        return re.findall(r'\.[^.]+', os.path.basename(self.path))

    @cached_property
    def format_extension(self):
        for extension in self.extensions:
            engine = self.environment.engines.get(extension)
            if not engine and self.environment.mimetypes.get(extension):
                return extension

    @cached_property
    def suffix(self):
        try:
            index = self.extensions.index(self.format_extension)
        except ValueError:
            return self.extensions
        return self.extensions[index:]

    @cached_property
    def engine_extensions(self):
        return [e for e in self.suffix[1:] if self.environment.engines.get(e)]

    @cached_property
    def engines(self):
        return [self.environment.engines.get(e) for e in self.engine_extensions]

    @cached_property
    def preprocessors(self):
        return self._get_processors(self.environment.preprocessors)

    @cached_property
    def postprocessors(self):
        return self._get_processors(self.environment.postprocessors)

    @cached_property
    def processors(self):
        engines = list(reversed(self.engines))
        return self.preprocessors + engines + self.postprocessors

    @cached_property
    def mimetype(self):
        return (self.environment.mimetypes.get(self.format_extension) or
                'application/octet-stream')

    def _get_processors(self, storage):
        return [cls(self) for cls in storage.get(self.mimetype)]
