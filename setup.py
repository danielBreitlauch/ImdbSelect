from distutils.core import setup
from setuptools import find_packages

setup(
    name='imdbSelect',
    version='0.1.0',
    packages=find_packages(),
    url='',
    license='MIT',
    author='Daniel Breitlauch',
    author_email='github@flying-stampe.de',
    description='Add movies of actors you like.'
                'This can be done be by specifying the actors directly in the config.'
                'Or it takes the actors of your plex library that are in most of your movies.',
    install_requires=[
        'requests',
        'IMDbPY',
        'plexapi',
        'jsonpickle',
        'python-dateutil',
        'colorama',
        'bs4',
        'parsedatetime',
        'urllib3',
    ],
    long_description=open('README.md').read(),
    keywords=['online food shop', 'home automation', 'codecheck', 'wunderlist', 'barcode', 'anti captcha']
)

