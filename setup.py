from setuptools import find_packages, setup

with open("README.rst") as file:
    README = file.read()

version = {}
with open("pykeepass/version.py") as file:
    exec(file.read(), version)

setup(
    name="pykeepass",
    version=version["__version__"],
    license="GPL3",
    description="Python library to interact with keepass databases "
    "(supports KDBX3 and KDBX4)",
    long_description=README,
    long_description_content_type='text/x-rst',
    author="Philipp Schmitt",
    author_email="philipp@schmitt.co",
    url="https://github.com/libkeepass/pykeepass",
    packages=find_packages(include=['pykeepass', 'pykeepass.*']),
    install_requires=[
        "python-dateutil",
        "construct",
        "argon2_cffi",
        "pycryptodomex>=3.6.2",
        "lxml",
    ],
    include_package_data=True,
)
