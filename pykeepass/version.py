__all__= ["__version__"]

try:
    # Retrieval of metadata version for Python 3.8 and above
    from importlib.metadata import version
    __version__ = version('pykeepass')
except ImportError:
    # Fallback for older Python versions (< 3.8)
    from pkg_resources import get_distribution
    __version__ = get_distribution('pykeepass').version