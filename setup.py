from setuptools import setup, find_packages
import ast

version = "1.0.0"
with open('ezzybot/__init__.py') as f:
    for line in f.read().split("\n"):
        if line.startswith('__version__'):
            version = ast.parse(line).body[0].value.s
            break

setup(name='ezzybot',
      version=version,
      description="Python IRC framework",
      url='https://github.com/Azure-Developments/ezzybot',
      author='EzzyBot team',
      author_email='me@lukej.me',
      license='GNU',
      packages=find_packages(),
      install_requires=['thingdb', 'pysocks', 'requests', 'pyfiglet'],
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'ezzybot = ezzybot:cmd'
          ]
      },
      zip_safe=False)
