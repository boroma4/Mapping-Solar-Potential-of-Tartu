import logging
import time
import functools

def timed(operation):
    def wrapper(func):
        @functools.wraps(func)
        def wrapped(self, *args, **kwargs):
            start = time.time()
            result = func(self, *args, **kwargs)
            duration_s =  round(time.time() - start, 3)
            logging.info(f"{operation} took {duration_s} seconds")
            return result
        return wrapped
    return wrapper
