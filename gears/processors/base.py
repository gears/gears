from functools import wraps


class BaseProcessor(object):

    @classmethod
    def as_processor(cls, **initkwargs):
        @wraps(cls, updated=())
        def processor(asset):
            instance = processor.processor_class(**initkwargs)
            return instance.process(asset)
        processor.processor_class = cls
        return processor

    def process(self, asset):
        raise NotImplementedError()
