import logging
import time
import functools
import datetime


def timed(operation):
    def wrapper(func):
        @functools.wraps(func)
        def wrapped(self, *args, **kwargs):
            start = time.time()
            result = func(self, *args, **kwargs)
            duration_s = round(time.time() - start, 3)
            logging.info(f"{operation} took {str(datetime.timedelta(seconds=duration_s))}")
            return result
        return wrapped
    return wrapper
