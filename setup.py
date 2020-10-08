from setuptools import find_packages, setup
from pykeepass import __version__

with open("README.rst") as file:
    README = file.read()

setup(
    name="pykeepass",
    version=__version__,
    license="GPL3",
    description="Python library to interact with keepass databases "
                "(supports KDBX3 and KDBX4)",
    long_description=README,
    author="Philipp Schmitt",
    author_email="philipp@schmitt.co",
    url="https://github.com/pschmitt/pykeepass",
    packages=find_packages(),
    install_requires=[
        "python-dateutil",
        # FIXME python2 - last version to support python2
        "construct==2.10.54",
        "argon2_cffi",
        "pycryptodomex>=3.6.2",
        "lxml",
        # FIXME python2
        "future"
    ],
    include_package_data=True
)
