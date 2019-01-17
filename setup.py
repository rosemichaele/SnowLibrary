from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='robotframework-snowlibrary',
    version='1.3.2',
    url='',
    license='Apache License 2.0',
    author='Michael Rose',
    author_email='michael.rose@theice.com',
    long_description=long_description,
    package_dir={'': 'src'},
    packages=find_packages('src', exclude=['contrib', 'docs', 'tests']),
    install_requires=['requests', 'bs4', 'selenium', 'robotframework', 'robotframework-seleniumlibrary', 'docutils',
                      'robotremoteserver', 'pysnow', 'robotframework-sshlibrary', 'rstr'],
    description='A Robot Framework Library with keywords for testing ServiceNow.',
    # Test requirements
    tests_require=['pytest'],
)
