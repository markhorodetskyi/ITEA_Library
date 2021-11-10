from setuptools import setup

setup(
    name='LibraryItea',
    version='1.0.0',
    description='library for test sql and json',
    author='None',
    author_email='none',
    packages=['Library', 'Library.db', 'Library.units'],
    install_requires=['colorama==0.4.4', 'loguru==0.5.3', 'win32-setctime==1.0.3']
)