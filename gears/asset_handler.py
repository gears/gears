# -*- coding: utf-8 -*-

from functools import wraps


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
