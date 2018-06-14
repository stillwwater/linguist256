from setuptools import setup, find_packages

setup(name='linguist256',
      version='0.1',
      author='Lucas',
      author_email='stillwwater@gmail.com',
      license='MIT',
      url='https://github.com/stillwwater/linguist256',
      install_requires=['argparse'],
      packages=find_packages(exclude=('.git')))
