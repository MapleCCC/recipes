import functools


__all__ = ["singleton_class"]


# A decorator to transform a class into a singleton
singleton_class = functools.cache
