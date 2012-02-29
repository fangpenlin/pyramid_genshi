from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

extra = {}

version = '0.1'

setup(
    name='pyramid_genshi',
    version=version,
    packages=find_packages(),
    install_requires=[
    ], **extra
)
