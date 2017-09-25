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
    long_description=long_description,
    install_requires=['gizeh'],
    platforms=['any'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Artistic Software',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Sound/Audio :: Analysis',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
    keywords='music musical tone clock visualization just intonation tonal atonal key signature scale chord',
)
