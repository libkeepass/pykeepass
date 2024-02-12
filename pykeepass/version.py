__all__= ["__version__"]

# FIXME: switch to using importlib.metadata when dropping Python<=3.7
import pkg_resources
__version__ = pkg_resources.get_distribution('pykeepass').version
