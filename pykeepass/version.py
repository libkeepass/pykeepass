__all__ = ["__version__"]

try:
    # Retrieval of metadata version for Python 3.8 and above
    from importlib.metadata import version

    __version__ = version("pykeepass")
except ImportError:
    # Fallback for older Python versions (< 3.8)
    from pkg_resources import (  # pyright: ignore[reportMissingImports]
        get_distribution,  # pyright: ignore[reportUnknownVariableType]
    )

    __version__: str = get_distribution("pykeepass").version  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
