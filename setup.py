#!/usr/bin/env python -u
# -*- mode: python; coding: utf-8 -*-
#
# pylama: ignore:E2651
"""
Setup script for seneschal application.

Copyright (C) Serhiy Zelenkov

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

Setup.

    pip install -e . -U -r requirements.txt
    python setup.py sdist
    See:
https://packaging.python.org/en/latest/distributing.html

Excellent guide "Less known packaging features and tricks"
    https://blog.ionelmc.ro/2014/05/25/python-packaging/

Usage:
--------------------------------------------------------------------------
    to build package:       python setup.py build
    to install package:     python setup.py install
    to remove installation: python setup.py uninstall
--------------------------------------------------------------------------
    to create source distribution:   python setup.py sdist
--------------------------------------------------------------------------
    to create binary RPM distribution:  python setup.py bdist_rpm
--------------------------------------------------------------------------
    to create binary DEB distribution:  python setup.py bdist_deb
--------------------------------------------------------------------------.
    Help on available distribution formats: --help-formats
"""
import sys
from pathlib import Path

from setuptools import setup, find_packages
from setuptools.command.test import test as test_command

# %%
__copyright__ = __doc__.split('\n')[3]
__app__ = __doc__.split('\n')[1].split(' ')[-2]
__author__ = ' '.join(__copyright__.split()[-2:])
__credits__ = []  # type: list
__license__ = 'Creative Commons Legal Code'
__maintainer__ = __author__
__email__ = '@'.join([__author__.rsplit(" ", maxsplit=1)[1].lower(), 'gmail.com'])
__status__ = 'Protoduction'
__version_info__ = (0, 0, 1)
__version__ = '.'.join(map(str, __version_info__))

# %%
REQUIRED_PYTHON_VER = (3, 10, 9)
GITHUB_URL = f'https://github.com/s{__email__.split("@", maxsplit=1)[0]}/{__app__}'
HERE = Path(__file__).parent.absolute()


class PyTest(test_command):
    """
    Setup test class.

    Arguments:
        test_command
    """

    user_options = [('pytest-args=', 'a', 'Arguments to pass to pytest')]

    def __init__(self, dist, **kw):
        """Initialize."""
        super().__init__(dist, **kw)
        self.pytest_args = ''

    def initialize_options(self):
        """Initialize options."""
        test_command.initialize_options(self)
        self.pytest_args = ''

    def run_tests(self):
        """Import here, cause outside the eggs aren't loaded."""
        # pylint: disable=import-outside-toplevel
        import shlex
        import pytest

        error_no = pytest.main(shlex.split(self.pytest_args))
        sys.exit(error_no)


if __name__ == '__main__':
    # clean(None)

    with open('README.md', 'r', encoding='utf-8') as fh:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            # https://www.python.org/dev/peps/pep-0345/#fields
            setup(author=__author__,
                  author_email=__email__,
                  # https://www.python.org/dev/peps/pep-0301/
                  classifiers=[
                      'Development Status :: 4 - Beta',
                      'Environment :: Console',
                      'Intended Audience :: End Users/Desktop',
                      'Intended Audience :: Developers',
                      'Libraries :: Python Modules',
                      f'License :: OSI Approved :: {__license__} License',
                      'Natural Language :: English',
                      'Operating System :: OS Independent',
                      'Programming Language :: Python',
                      'Programming Language :: Python :: 3',
                      'Programming Language :: Python :: 3.10',
                      'Programming Language :: Python :: 3.11',
                      'Programming Language :: Python :: 3.12',
                      'Programming Language :: Python :: Implementation :: CPython',
                      'Programming Language :: Python :: Implementation :: PyPy',
                      'Topic :: Software Development',
                      'Topic :: Text Editors',
                      'Topic :: Text Processing',
                      'Topic :: Utilities',
                  ],
                  cmdclass={'pytest': PyTest},
                  # becomes 'Summary' in pkg-info
                  description=__doc__.split('\n')[1],
                  download_url=f'{GITHUB_URL}/download.html',
                  entry_points={'console_scripts': (f'{__app__} = {__app__}:main',), },
                  extras_require={
                      'dev': ('pylint>=2.3.1',),
                      'test': ('pytest', 'coverage',),
                  },
                  # also include MANIFEST files in wheels
                  include_package_data=True,
                  install_requires=(req for req in f.read().splitlines()
                                    if req and not req.startswith('#')),
                  keywords=__app__,
                  license=__license__,
                  long_description=fh.read(),
                  long_description_content_type='text/markdown',
                  name=__app__,
                  packages=find_packages(exclude=['tests*']),
                  package_data={},
                  package_dir={'': '.'},
                  platforms=['Linux', 'Windows', 'MacOS'],
                  # List additional URLs that are relevant to project as a dict.
                  project_urls={
                      'Bug Reports': f'{GITHUB_URL}/issues',
                      'Dev Docs': f'{GITHUB_URL}/devdoc'
                  },
                  py_modules=[__app__,],
                  python_requires=f'>={".".join(map(str, REQUIRED_PYTHON_VER))}',
                  # semantic_version here to force download and making available
                  # before installing Leo Is also in `user_requires` so pip installs
                  # it too for general use
                  setup_requires=('semantic_version', 'setuptools >= 53.0.0', 'pytest-runner'),
                  requires=f.read().splitlines(),
                  tests_require=('pytest',),
                  url=GITHUB_URL,
                  version=__version__,
                  zip_safe=False
                  )
