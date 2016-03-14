from setuptools import setup, find_packages

#Don't actually use this ATM, this is only so I can keep track of install requires


setup(name='ezzybot',
      version='1.1.0',
      description="Python IRC framework",
      url='https://ezzybot.zzirc.xyz',
      author='EzzyBot team',
      author_email='me@lukej.me',
      license='GNU',
      packages=find_packages(),
      install_requires=['thingdb', 'pysocks'],
      include_package_data=True,
      zip_safe=False)
