from setuptools import setup, find_packages
import sys

with open('requirements.txt') as f:
    reqs = f.read()

reqs = reqs.strip().split('\n')

install = [req for req in reqs if not req.startswith("git+git://")]
depends = [req.replace("git+git://","git+http://") for req in reqs if req.startswith("git+git://")]

setup(
    name='fever-baselines',
    version='1.0.0',
    description='Fact Extraction and VERification baseline implementation',
    long_description="readme",
    license=license,
    python_requires='>=3.6',
    package_dir={'fever': 'src', 
                 'fever.common':'src/common', 
                 'fever.common.dataset':'src/common/dataset',
                 'fever.common.features':'src/common/features',
                 'fever.common.framework':'src/common/framework',
                 'fever.common.training':'src/common/training',
                 'fever.common.util':'src/common/util', 
                 'fever.retrieval':'src/retrieval',
                 'fever.rte':'src/rte',
                 'fever.rte.parikh':'src/rte/parikh',
                 'fever.rte.riedel':'src/rte/riedel'},
    packages=['fever', 
              'fever.common', 
              'fever.common.dataset',
              'fever.common.features',
              'fever.common.framework',
              'fever.common.training',
              'fever.common.util', 
              'fever.retrieval',
              'fever.rte',
              'fever.rte.parikh',
              'fever.rte.riedel'],
    install_requires=install,
    dependency_links=depends,
)
