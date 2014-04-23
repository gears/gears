import gzip
import os
from pkg_resources import iter_entry_points
from glob2.fnmatch import fnmatch

from .asset_attributes import AssetAttributes
from .assets import build_asset
from .cache import SimpleCache
from .compat import bytes
from .exceptions import FileNotFound
from .manifest import Manifest
from .processors import (
    DirectivesProcessor,
    HexdigestPathsProcessor,
    SemicolonsProcessor
)
from .utils import get_condition_func, unique


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

    def list(self, path):
        for finder in self:
            for item in finder.list(path):
                yield item


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

    def register_defaults(self):
        self.register('application/javascript', SemicolonsProcessor.as_handler())
        self.register('text/css', HexdigestPathsProcessor.as_handler())


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
    :param fingerprinting: if set to `True`, fingerprinted versions of assets
                           won't be created.
    """

    def __init__(self, root, public_assets=DEFAULT_PUBLIC_ASSETS,
                 manifest_path=None, cache=None, gzip=False,
                 fingerprinting=True):
        self.root = root
        self.public_assets = [get_condition_func(c) for c in public_assets]

        if manifest_path is not None:
            self.manifest_path = manifest_path
        else:
            self.manifest_path = os.path.join(self.root, '.manifest.json')
        self.manifest = Manifest(self.manifest_path)

        if cache is not None:
            self.cache = cache
        else:
            self.cache = SimpleCache()

        self.gzip = gzip
        self.fingerprinting = fingerprinting

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

    @property
    def paths(self):
        """The list of search paths. It is built from registered finders, which
        has ``paths`` property. Can be useful for compilers to resolve internal
        dependencies.
        """
        if not hasattr(self, '_paths'):
            paths = []
            for finder in self.finders:
                if hasattr(finder, 'paths'):
                    paths.extend(finder.paths)
            self._paths = paths
        return self._paths

    def register_defaults(self):
        """Register default compilers, preprocessors and MIME types."""
        self.mimetypes.register_defaults()
        self.preprocessors.register_defaults()
        self.postprocessors.register_defaults()

    def register_entry_points(self, exclude=()):
        """Allow Gears plugins to inject themselves to the environment. For
        example, if your plugin's package contains such ``entry_points``
        definition in ``setup.py``, ``gears_plugin.register`` function will be
        called with current enviroment during ``register_entry_points`` call::

            entry_points = {
                'gears': [
                    'register = gears_plugin:register',
                ],
            }

        Here is an example of such function::

            def register(environment):
                assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
                assets_dir = os.path.absolute_path(assets_dir)
                environment.register(FileSystemFinder([assets_dir]))

        If you want to disable this behavior for some plugins, list their
        packages using ``exclude`` argument::

            environment.register_entry_points(exclude=['plugin'])
        """
        for entry_point in iter_entry_points('gears', 'register'):
            if entry_point.module_name not in exclude:
                register = entry_point.load()
                register(self)

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
        if logical:
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

    def list(self, path, mimetype=None):
        """Yield two-tuples for all files found in the directory given by
        ``path`` parameter. Result can be filtered by the second parameter,
        ``mimetype``, that must be a MIME type of assets compiled source code.
        Each tuple has :class:`~gears.asset_attributes.AssetAttributes`
        instance for found file path as first item, and absolute path to this
        file as second item.

        Usage example::

            # Yield all files from 'js/templates' directory.
            environment.list('js/templates/*')

            # Yield only files that are in 'js/templates' directory and have
            # 'application/javascript' MIME type of compiled source code.
            environment.list('js/templates/*', mimetype='application/javascript')
        """
        basename_pattern = os.path.basename(path)

        if path.endswith('**'):
            paths = [path]
        else:
            paths = AssetAttributes(self, path).search_paths
        paths = map(lambda p: p if p.endswith('*') else p + '*', paths)

        results = unique(self._list_paths(paths), lambda x: x[0])
        for logical_path, absolute_path in results:
            asset_attributes = AssetAttributes(self, logical_path)
            if mimetype is not None and asset_attributes.mimetype != mimetype:
                continue

            basename = os.path.basename(asset_attributes.path_without_suffix)
            if not fnmatch(basename, basename_pattern) and basename != 'index':
                continue

            yield asset_attributes, absolute_path

    def _list_paths(self, paths):
        for path in paths:
            for result in self.finders.list(path):
                yield result

    def save(self):
        """Save handled public assets to :attr:`root` directory."""
        for asset_attributes, absolute_path in self.list('**'):
            logical_path = os.path.normpath(asset_attributes.logical_path)
            if self.is_public(logical_path):
                asset = build_asset(self, logical_path)
                source = bytes(asset)
                self.save_file(logical_path, source, asset.gzippable)
                if self.fingerprinting:
                    self.save_file(asset.hexdigest_path, source, asset.gzippable)
                    self.manifest.files[logical_path] = asset.hexdigest_path
        self.manifest.dump()

    def save_file(self, path, source, gzippable=False):
        filename = os.path.join(self.root, path)
        path = os.path.dirname(filename)
        if not os.path.exists(path):
            os.makedirs(path)
        elif not os.path.isdir(path):
            raise OSError("%s exists and is not a directory." % path)
        with open(filename, 'wb') as f:
            f.write(source)
        if self.gzip and gzippable:
            with gzip.open('{}.gz'.format(filename), 'wb') as f:
                f.write(source)

    def is_public(self, logical_path):
        return any(condition(logical_path) for condition in self.public_assets)
