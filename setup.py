try:
    from ez_setup import use_setuptools
    use_setuptools()
except ImportError:
    pass

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    
from setuptools.command.test import test as TestCommand
import io
import os
import codecs
import sys
import re

here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    # intentionally *not* adding an encoding option to open
    return codecs.open(os.path.join(here, *parts), 'r').read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

from setuptools import setup
from setuptools import find_packages
setup(
    name="pyAniSort",
    version=find_version('pyanisort', '__init__.py'),
    packages=['pyanisort'],
    py_modules=['ez_setup'],
    include_package_data=True,
    package_data={'pyanisort': ['conf/**', 'logs/**']}, 
    url='https://github.com/jotaro0010/pyanisort',
    license='MIT Software License',
    author='Jeremy Ottesen',
    author_email="jotaro0010@gmail.com",
    description="Automatically sorts anime using information from anidb.net",
    long_description=read('README'),
    platforms='any',

    entry_points = {
        'console_scripts': [
            'pyanisort = pyanisort.pyanisort:main',
        ],
    },
	
    classifiers = [
        "Development Status :: 3 - Alpha",
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        ],

    )

