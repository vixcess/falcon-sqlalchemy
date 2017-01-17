import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

install_requires = open("requirements.txt").read().strip().splitlines()
if sys.version_info.major != 3:
    raise EnvironmentError("only support python >= 3.4")
if sys.version_info.minor == 4:
    install_requires.append("typing")

setup(
    name='falcon_sqlalchemy',
    version="0.2.2",
    packages=['falcon_sqlalchemy'],
    url='https://github.com/vixcess/falcon-sqlalchemy',
    license='Apache License version 2',
    author='Shiqiao Du',
    author_email='lucidfrontier.45@gmail.com',
    description='Falcon extension to easily use SQLAlchemy',
    install_requires=install_requires,
    long_description=open('README.md').read(),
    classifiers=[
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ]
)
