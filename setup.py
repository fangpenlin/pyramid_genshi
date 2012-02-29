import os

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

extra = {}

try:
    here = os.path.abspath(os.path.dirname(__file__))
    README = open(os.path.join(here, 'README.txt')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except:
    README = ''
    CHANGES = ''

version = '0.1.0'

setup(
    name='pyramid_genshi',
    description='Genshi template bindings for the Pyramid web framework',
    long_description=README + '\n\n' +  CHANGES,
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    keywords='bfg pyramid pylons genshi templates',
    author="Victor Lin",
    author_email="bornstub@gmail.com",
    url="https://bitbucket.org/victorlin/pyramid_genshi",
    license="MIT",
    version=version,
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'Genshi',
        'Pyramid'
    ], **extra
)
