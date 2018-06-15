from setuptools import setup, find_packages

with open('README.md', 'rb') as f:
    readme = f.read().decode('utf-8')

setup(name='linguist256',
      version='0.2',
      long_description=readme,
      author='Lucas',
      author_email='stillwwater@gmail.com',
      license='MIT',
      url='https://github.com/stillwwater/linguist256',
      install_requires=['argparse'],
      packages=find_packages(exclude=('.git')),
      include_package_data=True)
