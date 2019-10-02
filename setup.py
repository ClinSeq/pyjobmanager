from setuptools import setup
from pip._internal.req import parse_requirements

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements("requirements.txt", session=False)

# reqs is a list of requirement
reqs = [str(ir.req) for ir in install_reqs if ir.req is not None]

setup(name='pyjobmanager',
      version='0.6.5',
      packages=['pyjobmanager', 'pyjobmanager.pipeline', 'pyjobmanager.runners', 'pyjobmanager.tools'],
      install_requires=reqs
      )
