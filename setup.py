from distutils.core import setup


setup(
    name='pykeepass',
    version='1.0',
    description='Low-level library to interact with keepass databases '\
                '(supports the v.4 format)',
    author='Philipp Schmitt',
    author_email='philipp@schmitt.co',
    url='https://github.com/pschmitt/pykeepass',
    packages=['pykeepass'],
    install_requires=['libkeepass'],
    entry_points={
        'console_scripts': ['pkpwrite=pykeepass.pkpwrite:main']
    }
)
