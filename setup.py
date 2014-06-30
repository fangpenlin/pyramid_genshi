import os

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

try:
    here = os.path.abspath(os.path.dirname(__file__))
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
except:
    README = ''
    CHANGES = ''


version = '0.1.4'

setup(
    name='pyramid_genshi',
    description='Genshi template bindings for the Pyramid web framework',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    keywords='bfg pyramid pylons genshi templates',
    author="Victor Lin",
    author_email="bornstub@gmail.com",
    url="https://github.com/victorlin/pyramid_genshi",
    license="MIT",
    version=version,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite="pyramid_genshi.tests",
    install_requires=[
        'Genshi',
        'Pyramid',
    ],
    test_requires=[
        'nose',
        'nose-cov',
        'mock',
    ],
)
