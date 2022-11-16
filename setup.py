from setuptools import find_packages, setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name='evpn',
    packages=find_packages(),
    version='0.1.0',
    description='Cross Platform Express VPN API for Python',
    long_description=long_description,
    author='thewh1teagle',
    license='MIT',
)