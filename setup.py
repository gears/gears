import os
from setuptools import setup, find_packages


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='Gears',
    version='0.4',
    license='ISC',
    description='Compiles and concatenates JavaScript and CSS assets.',
    long_description=read('README.rst'),
    url='https://github.com/gears/gears',
    author='Mike Yumatov',
    author_email='mike@yumatov.org',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2'],
)
