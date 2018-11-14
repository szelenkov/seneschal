#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Setup
    pip install -e . -U -r requirements.txt
    python setup.py sdist
    See:
https://packaging.python.org/en/latest/distributing.html

Excellent guide "Less known packaging features and tricks"
    Ionel Cristian Mărieș, @ionelmc
    https://blog.ionelmc.ro/presentations/packaging/#slide:2
    https://blog.ionelmc.ro/2014/05/25/python-packaging/
'''
from glob import glob

import sys
# To use a consistent encoding
from os.path import abspath, basename, dirname, isdir, join, realpath, splitext

from shutil import rmtree

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from pypandoc import convert_file

import leo.core.leoGlobals as g
import leo.core.leoVersion

__author__ = "Serhiy Zelenkov"
__copyright__ = "Copyright 2019"
__credits__ = []
__license__ = "MIT License"
__version__ = "0.0.1"
__maintainer__ = __author__
__email__ = "zelenkov@gmail.com"
__status__ = "Production"
REQUIRED_PYTHON_VER = (3, 6, 5)

HERE = abspath(dirname(__file__))

class PyTest(TestCommand):
    '''
    Setup test class

    Arguments:
        TestCommand
    '''

    user_options = [("pytest-args=", "a", "Arguments to pass to pytest")]

    def __init__(self, dist, **kw):
        super().__init__(dist, **kw)
        self.pytest_args = ""

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ""

    def run_tests(self):
        import shlex

        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)

def clean():
    '''Removing build, dist and egg directories'''
    print(__doc__)
    root = dirname(realpath(__file__))
    for directory in ['build', 'dist', 'seneschal.egg-info', '.eggs']:
        dpath = join(root, directory)
        if isdir(dpath):
            rmtree(dpath)

clean()
with open("README.md", "r") as fh:
    long_description = fh.read()

# https://www.python.org/dev/peps/pep-0345/#fields
setup(author=__author__,
      author_email=__email__,
      # https://www.python.org/dev/peps/pep-0301/
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Operating System :: MacOS',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Topic :: Software Development',
          'Topic :: Text Editors',
          'Topic :: Text Processing',
          ],
      cmdclass={"pytest": PyTest},
      entry_points={
          'console_scripts': ['seneschal=seneschal.core.run:run'],
          'gui_scripts': ['seneschal=seneschal.core.run:run']
          },
      # becomes 'Summary' in pkg-info
      description='An IDE, PIM and Outliner',
      download_url='http://leoeditor.com/download.html',
      # also include MANIFEST files in wheels
      include_package_data=True,
      install_requires=[
          'docutils', # used by Sphinx, rST plugin
          'nbformat', # for Jupyter notebook integration
          'pylint', 'pyflakes', # coding syntax standards
          'pypandoc', # doc format conversion
          'sphinx', # rST plugin
          'semantic_version', # Pip packaging
          'twine', 'wheel', 'keyring' # Pip packaging, uploading to PyPi
      ],
      keywords='seneschal',
      license=__license__,
      long_description=long_description,
      long_description_content_type="text/markdown",
      name='seneschal',
      packages=find_packages(),
      package_dir={'': '.'},
      platforms=['Linux', 'Windows', 'MacOS'],
      project_urls={
          'Bug Reports': '{}/issues'.format(GITHUB_URL),
          'Dev Docs': 'https://developers.home-assistant.io/',
          'Discord': 'https://discordapp.com/invite/c5DvZ4e',
          'Forum': 'https://community.home-assistant.io/'
      },
      py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
      python_requires='>={}'.format('.'.join(map(str, REQUIRED_PYTHON_VER))),
      #semantic_version here to force download and making available before installing Leo
      #Is also in `user_requires` so pip installs it too for general use
      setup_requires=['semantic_version', 'pytest-runner'],
      tests_require=['pytest'],
      url='https://www.python.org/sigs/distutils-sig/',
      version=__version__,
      zip_safe=False
      )
