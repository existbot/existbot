from setuptools import setup, find_packages
from ezzybot import __version__

setup(name='ezzybot',
      version=__version__,
      description="Python IRC framework",
      url='https://ezzybot.zzirc.xyz',
      author='EzzyBot team',
      author_email='me@lukej.me',
      license='GNU',
      packages=find_packages(),
      install_requires=['thingdb', 'pysocks', 'requests'],
      include_package_data=True,
      zip_safe=False)
