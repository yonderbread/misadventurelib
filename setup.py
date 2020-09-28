from os.path import abspath, dirname
from setuptools import setup
from misadventure import __version__, __author__, __liscense__, __repo__

ROOT = abspath(dirname(__file__))

with open('README.md', 'r') as readme_file:
    README = readme_file.read()
    readme_file.close()

setup(
    name='misadventurelib',
    description='Scary easy text adventures',
    long_description=README,
    long_description_content_type="text/markdown",
    version=__version__,
    author=__author__,
    author_email='',
    url=__repo__,
    project_urls={
        'Documentation': ''
    },
    py_modules=['misadventurelib'],
    extras_require={
        ':python_version < "3.3"': [
            'backports.shutil_get_terminal_size>=1.0.0',
        ],
    },
    python_requires='>=3',
    classifiers=[
        'Development Status :: Beta',
        'Enviorment :: Console',
        'Intended Audience :: Developers',
        f'License :: {__liscense__}',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Text Adventures :: Games'
    ]
)
