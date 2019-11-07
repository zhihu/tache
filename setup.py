from setuptools import setup, find_packages
from codecs import open
from os import path

__version__ = '0.2.1'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), 'r') as f:
    long_description = f.read()

# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if x]

setup(
    name='tache',
    version=__version__,
    description='A tag based invalidation caching library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/zhihu/tache',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License'
    ],
    keywords='',
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    author='wayhome',
    install_requires=install_requires,
    author_email='y@zhihu.com'
)
