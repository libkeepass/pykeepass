from setuptools import find_packages, setup


setup(
    name='pykeepass',
    version='2.3.0',
    license='GPL3',
    description='Low-level library to interact with keepass databases '\
                '(supports the v.4 format)',
    long_description=open('README.rst').read(),
    author='Philipp Schmitt',
    author_email='philipp@schmitt.co',
    url='https://github.com/pschmitt/pykeepass',
    packages=find_packages(),
    install_requires=['libkeepass-unicode', 'easypysmb'],
    entry_points={
        'console_scripts': ['pkpwrite=pykeepass.pkpwrite:main']
    }
)
