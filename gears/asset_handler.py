# -*- coding: utf-8 -*-

from functools import wraps
from subprocess import Popen, PIPE


class AssetHandlerError(Exception):
    pass


class BaseAssetHandler(object):
    """Base class for all asset handlers (processors, compilers and
    compressors). A subclass has to implement :meth:`__call__` which is called
    with asset as argument.
    """

    def __call__(self, asset):
        """Subclasses have to override this method to implement the actual
        handler function code. This method is called with asset as argument.
        Depending on the type of the handler, this method must change asset
        state (as it does in :class:`~gears.processors.Directivesprocessor`)
        or return some value (in case of asset compressors).
        """
        raise NotImplementedError

    @classmethod
    def as_handler(cls, **initkwargs):
        """Converts the class into an actual handler function that can be used
        when registering different types of processors in
        :class:`~gears.enviroment.Environment` class instance.

        The arguments passed to :meth:`as_handler` are forwarded to the
        constructor of the class.
        """
        @wraps(cls, updated=())
        def handler(asset):
            return handler.handler_class(**initkwargs)(asset)
        handler.handler_class = cls
        return handler


class ExecMixin(object):
    """Provides the ability to process asset through external command."""

    #: The name of the executable to run. It must be a command name, if it is
    #: available in the PATH environment variable, or a path to the executable.
    executable = None

    #: The list of executable parameters.
    params = []

    def run(self, input):
        """Runs :attr:`executable` with ``input`` as stdin.
        :class:`AssetHandlerError` exception is raised, if execution is failed,
        otherwise stdout is returned.
        """
        p = self.get_process()
        output, errors = p.communicate(input=input.encode('utf-8'))
        if p.returncode != 0:
            raise AssetHandlerError(errors)
        return output.decode('utf-8')

    def get_process(self):
        """Returns :class:`subprocess.Popen` instance with args from
        :meth:`get_args` result and piped stdin, stdout and stderr.
        """
        return Popen(self.get_args(), stdin=PIPE, stdout=PIPE, stderr=PIPE)

    def get_args(self):
        """Returns the list of :class:`subprocess.Popen` arguments."""
        return [self.executable] + self.params
