import os
import sys

from .asset_attributes import AssetAttributes
from .assets import build_asset
from .cache import SimpleCache
from .exceptions import FileNotFound
from .processors import DirectivesProcessor
from .utils import get_condition_func


DEFAULT_PUBLIC_ASSETS = (
    lambda path: not any(path.endswith(ext) for ext in ('.css', '.js')),
    r'^css/style\.css$',
    r'^js/script\.js$',
)


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
    """The registry for MIME types. It acts like a dict with extensions as
    keys and MIME types as values. Every registered extension can have only one
    MIME type.
    """

    def register_defaults(self):
        """Register MIME types for ``.js`` and ``.css`` extensions."""
        self.register('.css', 'text/css')
        self.register('.js', 'application/javascript')

    def register(self, extension, mimetype):
        """Register passed ``mimetype`` MIME type with ``extension`` extension.
        """
        self[extension] = mimetype

    def unregister(self, extension):
        """Remove registered MIME type for passed ``extension`` extension. If
        MIME type for this extension does not found in the registry, nothing
        happens.
        """
        if extension in self:
            del self[extension]


class Compilers(dict):
    """The registry for compilers. It acts like a dict with extensions as keys
    and compilers as values. Every registered extension can have only one
    compiler.
    """

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

    def register(self, mimetype, processor):
        """Register passed `processor` for passed `mimetype`."""
        if mimetype not in self or processor not in self[mimetype]:
            self.setdefault(mimetype, []).append(processor)

    def unregister(self, mimetype, processor):
        """Remove passed `processor` for passed `mimetype`. If processor for
        this MIME type does not found in the registry, nothing happens.
        """
        if mimetype in self and processor in self[mimetype]:
            self[mimetype].remove(processor)

    def get(self, mimetype):
        """Return a list of processors, registered for passed `mimetype`. If
        no processors are registered for this MIME type, empty list is
        returned.
        """
        return super(Processors, self).get(mimetype, [])


class Preprocessors(Processors):
    """The registry for asset preprocessors. It acts like a dictionary with
    MIME types as keys and lists of processors as values. Every registered MIME
    type can have many preprocessors. Preprocessors for the MIME type are used
    in the order they were added.
    """

    def register_defaults(self):
        """Register :class:`~gears.processors.DirectivesProcessor` as
        a preprocessor for `text/css` and `application/javascript` MIME types.
        """
        self.register('text/css', DirectivesProcessor.as_handler())
        self.register('application/javascript', DirectivesProcessor.as_handler())


class Postprocessors(Processors):
    """The registry for asset postprocessors. It acts like a dictionary with
    MIME types as keys and lists of processors as values. Every registered MIME
    type can have many postprocessors. Postprocessors for the MIME type are
    used in the order they were added.
    """


class Compressors(dict):
    """The registry for asset compressors. It acts like a dictionary with
    MIME types as keys and compressors as values. Every registered MIME type
    can have only one compressor.
    """

    def register(self, mimetype, compressor):
        """Register passed `compressor` for passed `mimetype`."""
        self[mimetype] = compressor

    def unregister(self, mimetype):
        """Remove registered compressors for passed `mimetype`. If compressor
        for this MIME type does not found in the registry, nothing happens.
        """
        if mimetype in self:
            del self[mimetype]


class Suffixes(list):
    """The registry for asset suffixes. It acts like a list of dictionaries.
    Every dictionary has three keys: ``extensions``, ``result_mimetype`` and
    ``mimetype``:

    - ``suffix`` is a suffix as a list of extensions (e.g. ``['.js', '.coffee']``);
    - ``result_mimetype`` is a MIME type of a compiled asset with this suffix;
    - ``mimetype`` is a MIME type, for which this suffix is registered.
    """

    def register(self, extension, root=False, to=None, mimetype=None):
        if root:
            self.append({
                'suffix': [extension],
                'full': [extension],
                'result_mimetype': mimetype,
                'mimetype': mimetype,
            })
            return
        new = []
        for item in self:
            if to is not None and item['mimetype'] != to:
                continue
            suffix = list(item['suffix'])
            suffix.append(extension)
            full = list(item['full'])
            full.append(extension)
            new.append({
                'suffix': suffix,
                'full': full,
                'result_mimetype': item['result_mimetype'],
                'mimetype': mimetype,
            })
            if to is not None:
                new.append({
                    'suffix': [extension],
                    'full': full,
                    'result_mimetype': item['result_mimetype'],
                    'mimetype': mimetype,
                })
        self.extend(new)

    def unregister(self, extension):
        for item in list(self):
            if extension in item['full']:
                self.remove(item)

    def find(self, mimetype=None):
        suffixes = []
        for item in self:
            if mimetype is None or item['result_mimetype'] == mimetype:
                suffixes.append(''.join(item['suffix']))
        return suffixes


class Environment(object):
    """This is the central object, that links all Gears parts. It is passed the
    absolute path to the directory where public assets will be saved.
    Environment contains registries for file finders, compilers, compressors,
    processors and supported MIME types.

    :param root: the absolute path to the directory where handled public assets
                 will be saved by :meth:`save` method.
    :param public_assets: a list of public assets paths.
    :param cache: a cache object. It is used by assets and dependencies to
                  store compilation results.
    """

    def __init__(self, root, public_assets=DEFAULT_PUBLIC_ASSETS, cache=None):
        self.root = root
        self.public_assets = [get_condition_func(c) for c in public_assets]
        self.cache = cache if cache is not None else SimpleCache()

        #: The registry for file finders. See
        #: :class:`~gears.environment.Finders` for more information.
        self.finders = Finders()

        #: The registry for asset compilers. See
        #: :class:`~gears.environment.Compilers` for more information.
        self.compilers = Compilers()

        #: The registry for supported MIME types. See
        #: :class:`~gears.environment.MIMETypes` for more information.
        self.mimetypes = MIMETypes()

        #: The registry for asset compressors. See
        #: :class:`~gears.environment.Compressors` for more information.
        self.compressors = Compressors()

        #: The registry for asset preprocessors. See
        #: :class:`~gears.environment.Preprocessors` for more information.
        self.preprocessors = Preprocessors()

        #: The registry for asset postprocessors. See
        #: :class:`~gears.environment.Postprocessors` for more information.
        self.postprocessors = Postprocessors()

    @property
    def suffixes(self):
        """The registry for supported suffixes of assets. It is built from
        MIME types and compilers registries, and is cached at the first call.
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
        """Register default compilers, preprocessors and MIME types."""
        self.mimetypes.register_defaults()
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
            asset_attributes = AssetAttributes(self, item)
            suffixes = self.suffixes.find(asset_attributes.mimetype)
            if not suffixes:
                return self.find(item)
            path = asset_attributes.path_without_suffix
            for suffix in suffixes:
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

    def list(self, path, mimetype=None, recursive=False):
        """Yield two-tuples for all files found in the directory given by
        ``path`` parameter. Result can be filtered by the second parameter,
        ``mimetype``, that must be a MIME type of assets compiled source code.
        If ``recursive`` is ``True``, then ``path`` will be scanned
        recursively. Each tuple has
        :class:`~gears.asset_attributes.AssetAttributes` instance for found
        file path as first item, and absolute path to this file as second item.

        Usage example::

            # Yield all files from 'js/templates' directory.
            environment.list('js/libs')

            # Yield only files that are in 'js/templates' directory and have
            # 'application/javascript' MIME type of compiled source code.
            environment.list('js/templates', mimetype='application/javascript')
        """
        found = set()
        for finder in self.finders:
            for logical_path, absolute_path in finder.list(path, recursive=recursive):
                asset_attributes = AssetAttributes(self, logical_path)
                if mimetype is not None and asset_attributes.mimetype != mimetype:
                    continue
                if logical_path not in found:
                    yield asset_attributes, absolute_path
                    found.add(logical_path)

    def save(self):
        """Save handled public assets to :attr:`root` directory."""
        for asset_attributes, absolute_path in self.list('.', recursive=True):
            logical_path = os.path.normpath(asset_attributes.logical_path)
            if self.is_public(logical_path):
                asset = build_asset(self, logical_path)
                if sys.version_info < (3, 0):
                    source = str(asset)
                else:
                    source = bytes(asset)
                self.save_file(logical_path, source)

    def save_file(self, path, source):
        filename = os.path.join(self.root, path)
        path = os.path.dirname(filename)
        if not os.path.exists(path):
            os.makedirs(path)
        elif not os.path.isdir(path):
            raise OSError("%s exists and is not a directory." % path)
        with open(filename, 'wb') as f:
            f.write(source)

    def is_public(self, logical_path):
        return any(condition(logical_path) for condition in self.public_assets)
