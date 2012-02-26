# -*- coding: utf-8 -*-

import os
import re
from .utils import cached_property


class AssetAttributes(object):
    """Provides access to asset path properties. The attributes object is
    created with environment object and relative (or logical) asset path.

    Some properties may be useful or not, depending on the type of passed path.
    If it is a relative asset path, you can use all properties except
    :attr:`search_paths`. In case of a logical asset path it makes sense to
    use only those properties that are not related to processors and compressor.

    :param environment: an instance of :class:`~gears.environment.Environment`
                        class.
    :param path: a relative or logical path of the asset.
    """

    def __init__(self, environment, path):
        #: Used to access the registries of compilers, processors, etc.
        #: It can be also used by asset. See
        #: :class:`~gears.environment.Environment` for more information.
        self.environment = environment

        #: The relative (or logical) path to asset.
        self.path = path

        #: The relative path to the directory the asset.
        self.dirname = os.path.dirname(path)

    @cached_property
    def search_paths(self):
        """The list of logical paths which are used to search for an asset.
        This property makes sense only if the attributes was created with
        logical path.

        It is assumed that the logical path can be a directory containing a
        file named ``index`` with the same suffix.

        Example::

            >>> attrs = AssetAttributes(environment, 'js/app.js')
            >>> attrs.search_paths
            ['js/app.js', 'js/app/index.js']

            >>> attrs = AssetAttributes(environment, 'js/app/index.js')
            >>> attrs.search_paths
            ['js/models/index.js']
        """
        paths = [self.path]
        if os.path.basename(self.path_without_suffix) != 'index':
            path = os.path.join(self.path_without_suffix, 'index')
            paths.append(path + ''.join(self.suffix))
        return paths

    @cached_property
    def path_without_suffix(self):
        """The relative path to asset without suffix.
        Example::

            >>> attrs = AssetAttributes(environment, 'js/app.js')
            >>> attrs.path_without_suffix
            'js/app'
        """
        if self.suffix:
            return self.path[:-len(''.join(self.suffix))]
        return self.path

    @property
    def logical_path(self):
        """The logical path to asset.
        Example::

            >>> attrs = AssetAttributes(environment, 'js/models.js.coffee')
            >>> attrs.logical_path
            'js/models.js'
        """
        return self.path_without_suffix + self.format_extension

    @cached_property
    def extensions(self):
        """The list of asset extensions.
        Example::

            >>> attrs = AssetAttributes(environment, 'js/models.js.coffee')
            >>> attrs.extensions
            ['.js', '.coffee']

            >>> attrs = AssetAttributes(environment, 'js/lib/external.min.js.coffee')
            >>> attrs.format_extension
            ['.min', '.js', '.coffee']
        """
        return re.findall(r'\.[^.]+', os.path.basename(self.path))

    @cached_property
    def format_extension(self):
        """The format extension of asset.
        Example::

            >>> attrs = AssetAttributes(environment, 'js/models.js.coffee')
            >>> attrs.format_extension
            '.js'

            >>> attrs = AssetAttributes(environment, 'js/lib/external.min.js.coffee')
            >>> attrs.format_extension
            '.js'
        """
        for extension in reversed(self.extensions):
            compiler = self.environment.compilers.get(extension)
            if not compiler and self.environment.mimetypes.get(extension):
                return extension

    @cached_property
    def suffix(self):
        """The list of asset extensions starting from the format extension.
        Example::

            >>> attrs = AssetAttributes(environment, 'js/lib/external.min.js.coffee')
            >>> attrs.suffix
            ['.js', '.coffee']
        """
        try:
            index = self.extensions.index(self.format_extension)
        except ValueError:
            return self.extensions
        return self.extensions[index:]

    @cached_property
    def compiler_extensions(self):
        """The list of compiler extensions.
        Example::

            >>> attrs = AssetAttributes(environment, 'js/lib/external.min.js.coffee')
            >>> attrs.suffix
            ['.coffee']
        """
        return [e for e in self.suffix[1:] if self.environment.compilers.get(e)]

    @cached_property
    def compilers(self):
        """The list of compilers used to build asset."""
        return [self.environment.compilers.get(e) for e in self.compiler_extensions]

    @property
    def preprocessors(self):
        """The list of preprocessors used to build asset."""
        return self.environment.preprocessors.get(self.mimetype)

    @property
    def postprocessors(self):
        """The list of postprocessors used to build asset."""
        return self.environment.postprocessors.get(self.mimetype)

    @property
    def processors(self):
        """The list of all processors (preprocessors, compilers,
        postprocessors) used to build asset.
        """
        return self.preprocessors + list(reversed(self.compilers)) + self.postprocessors

    @property
    def compressor(self):
        """The compressors used to compress the asset."""
        return self.environment.compressors.get(self.mimetype)

    @cached_property
    def mimetype(self):
        """MIME-type of the asset."""
        return (self.environment.mimetypes.get(self.format_extension) or
                'application/octet-stream')
