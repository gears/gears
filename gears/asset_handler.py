from functools import wraps


class BaseAssetHandler(object):

    def __call__(self, asset):
        raise NotImplementedError

    @classmethod
    def as_handler(cls, **initkwargs):
        @wraps(cls, updated=())
        def handler(asset):
            return handler.handler_class(**initkwargs)(asset)
        handler.handler_class = cls
        return handler
