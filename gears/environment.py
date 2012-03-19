from __future__ import with_statement

import os

from .asset_attributes import AssetAttributes
from .assets import build_asset
from .cache import Cache
from .compilers import (
    CoffeeScriptCompiler, HandlebarsCompiler, LessCompiler, StylusCompiler)
from .exceptions import FileNotFound
from .processors import DirectivesProcessor


class Finders(list):
    """The registry for file finders. This is just a list of finder objects.
    Each finder object must be an instance of any
    :class:`~gears.finders.BaseFinder` subclass. Finders from this registry are
    used by :class:`~gears.environment.Environment` object in the order they
    were added.
    """

    def register(self, finder):
        """Append passed ``finder`` to the list of finders."""
        if finder not in self:
            self.append(finder)

    def unregister(self, finder):
        """Remove passed ``finder`` from the list of finders. If ``finder``
        does not found in the registry, nothing happens.
        """
        if finder in self:
            self.remove(finder)


class MIMETypes(dict):
    """The registry for MIME-types. It acts like a dict with extensions as
    keys and MIME-types as values.
    """

    def register_defaults(self):
        """Register MIME-types for ``.js`` and ``.css`` extensions."""
        self.register('.css', 'text/css')
        self.register('.js', 'application/javascript')

    def register(self, extension, mimetype):
        """Register passed ``mimetype`` MIME-type with ``extension`` extension.
        """
        self[extension] = mimetype

    def unregister(self, extension):
        """Remove registered MIME-type for passed ``extension`` extension. If
        MIME-type for this extension does not found in the registry, nothing
        happens.
        """
        if extension in self:
            del self[extension]


class Compilers(dict):
    """The registry for compilers. It acts like a dict with extensions as keys
    and compilers as values.
    """

    def __init__(self):
        super(Compilers, self).__init__()

    def register_defaults(self):
        """Register :class:`~gears.compilers.CoffeeScriptCompiler`,
        :class:`~gears.compilers.HandlebarsCompiler`,
        :class:`~gears.compilers.LessCompiler` and
        :class:`~gears.compilers.StylusCompiler` for ``.coffee``,
        ``.handlebars``, ``.less`` and ``.styl`` extensions, respectively.
        """
        self.register('.coffee', CoffeeScriptCompiler.as_handler())
        self.register('.handlebars', HandlebarsCompiler.as_handler())
        self.register('.less', LessCompiler.as_handler())
        self.register('.styl', StylusCompiler.as_handler())

    def register(self, extension, compiler):
        """Register passed `compiler` with passed `extension`."""
        self[extension] = compiler

    def unregister(self, extension):
        """Remove registered compiler for passed `extension`. If compiler for
        this extension does not found in the registry, nothing happens.
        """
        if extension in self:
            del self[extension]


class Processors(dict):
    """Base class for processors registries."""

    def register(self, mimetype, processor_class):
        """Register passed `processor` for passed `mimetype`."""
        if mimetype not in self or processor_class not in self[mimetype]:
            self.setdefault(mimetype, []).append(processor_class)

    def unregister(self, mimetype, processor_class):
        """Remove passed `processor` for passed `mimetype`. If processor for
        this mimetype does not found in the registry, nothing happens.
        """
        if mimetype in self and processor_class in self[mimetype]:
            self[mimetype].remove(processor_class)

    def get(self, mimetype):
        """Return a list of processors, registered for passed `mimetype`. If
        no processors are registered for this mimetype, empty list is returned.
        """
        return super(Processors, self).get(mimetype, [])


class Preprocessors(Processors):
    """The registry for asset preprocessors. It acts like a dictionary with
    mimetypes as keys and lists of processors as values.
    """

    def register_defaults(self):
        """Register :class:`~gears.processors.DirectivesProcessor` as
        a preprocessor for `text/css` and `application/javascript` MIME-types.
        """
        self.register('text/css', DirectivesProcessor.as_handler())
        self.register('application/javascript', DirectivesProcessor.as_handler())


class Postprocessors(Processors):
    """The registry for asset postprocessors. It acts like a dictionary with
    MIME-types as keys and lists of processors as values.
    """


class Compressors(dict):
    """The registry for asset compressors. It acts like a dictionary with
    MIME-types as keys and compressors as values.
    """

    def register(self, mimetype, compressor):
        """Register passed `compressor` for passed `mimetype`."""
        self[mimetype] = compressor

    def unregister(self, mimetype):
        """Remove registered compressors for passed `mimetype`. If compressor
        for this MIME-type does not found in the registry, nothing happens.
        """
        if mimetype in self:
            del self[mimetype]


class PublicAssets(list):
    """The registry for public assets. It acts like a list of logical paths of
    assets.
    """

    def register_defaults(self):
        """Register ``css/style.css`` and ``js/script.js`` as public assets."""
        self.register('css/style.css')
        self.register('js/script.js')

    def register(self, path):
        """Register passed `path` as public asset."""
        if path not in self:
            self.append(path)

    def unregister(self, path):
        """Remove passed `path` from registry. If `path` does not found in the
        registry, nothing happens.
        """
        if path in self:
            self.remove(path)


class Suffixes(list):
    """The registry for asset suffixes. It acts like a list of dictionaries.
    Every dictionary has two keys: ``extensions`` and ``mimetype``:

    - ``extensions`` is a suffix as a list (e.g. ``['.js', '.coffee']);
    - ``mimetype`` is a MIME-type, for which this suffix is registered.
    """

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
    """This is the central object, that links all Gears parts. It is passed the
    absolute path to the directory where public assets will be saved.
    Environment contains registries for file finders, compilers, compressors,
    processors, supported MIME-types and public assets.

    :param root: the absolute path to the directory where handled public assets
                 will be saved by :meth:`save` method.
    """

    def __init__(self, root):
        self.root = root

        #: A cache object. It is used by assets and dependencies to store
        #: compilation results.
        self.cache = Cache()

        #: The registry for file finders. See
        #: :class:`~gears.environment.Finders` for more information.
        self.finders = Finders()

        #: The registry for asset compilers. See
        #: :class:`~gears.environment.Compilers` for more information.
        self.compilers = Compilers()

        #: The registry for supported MIME-types. See
        #: :class:`~gears.environment.MIMETypes` for more information.
        self.mimetypes = MIMETypes()

        #: The registry for asset compressors. See
        #: :class:`~gears.environment.Compressors` for more information.
        self.compressors = Compressors()

        #: The registry for public assets. Only assets from this registry will
        #: be saved to the :attr:`root` path. See
        #: :class:`~gears.environment.PublicAsets` for more information.
        self.public_assets = PublicAssets()

        #: The registry for asset preprocessors. See
        #: :class:`~gears.environment.Preprocessors` for more information.
        self.preprocessors = Preprocessors()

        #: The registry for asset postprocessors. See
        #: :class:`~gears.environment.Postprocessors` for more information.
        self.postprocessors = Postprocessors()

    @property
    def suffixes(self):
        """The registry for supported suffixes of assets. It is built from
        MIME-types and compilers registries, and is cached at the first call.
        See :class:`~gears.environment.Suffixes` for more information.
        """
        if not hasattr(self, '_suffixes'):
            suffixes = Suffixes()
            for extension, mimetype in self.mimetypes.items():
                suffixes.register(extension, root=True, mimetype=mimetype)
            for extension, compiler in self.compilers.items():
                suffixes.register(extension, to=compiler.result_mimetype)
            self._suffixes = suffixes
        return self._suffixes

    def register_defaults(self):
        """Register default compilers, preprocessors, MIME-Types and public
        assets.
        """
        self.compilers.register_defaults()
        self.mimetypes.register_defaults()
        self.public_assets.register_defaults()
        self.preprocessors.register_defaults()

    def find(self, item, logical=False):
        """Find files using :attr:`finders` registry. The ``item`` parameter
        can be an instance of :class:`~gears.asset_attributes.AssetAttributes`
        class, a path to the asset or a logical path to the asset. If ``item``
        is a logical path, `logical` parameter must be set to ``True``.

        Returns a tuple with :class:`~gears.asset_attributes.AssetAttributes`
        instance for found file path as first item, and absolute path to this
        file as second item.

        If nothing is found, :class:`gears.exceptions.FileNotFound` exception
        is rased.
        """
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

    def list(self, path, suffix=None):
        """Yield two-tuples for all files found in the directory given by
        ``path`` parameter. Result can be filtered by the second parameter,
        ``suffix``, that must be a list or tuple of file extensions. Each tuple
        has :class:`~gears.asset_attributes.AssetAttributes` instance for found
        file path as first item, and absolute path to this file as second item.

        Usage example::

            # Yield all files from 'js/templates' directory.
            environment.list('js/libs')

            # Yield only files that are in 'js/templates' directory and match
            # pattern '*.js.handlebars' or are compiled to files that match
            # pattern.
            environment.list('js/templates', suffix=('.js', '.handlebars'))
        """
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
        """Save handled public assets to :attr:`root` directory."""
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
