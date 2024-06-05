from setuptools import setup, find_packages

setup(
    name='github-analyzer',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'pydot',
        'requests',
    ],
)