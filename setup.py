from setuptools import setup

import pitchclock

with open('README.md') as readme:
    long_description = readme.read()

setup(
    name='pitchclock',
    version=pitchclock.__version__,
    packages=['pitchclock'],
    url=pitchclock.__url__,
    license=pitchclock.__license__,
    author=pitchclock.__author__,
    author_email=pitchclock.__author_email__,
    description='Tone clock visualizations',
    long_description=long_description
)
