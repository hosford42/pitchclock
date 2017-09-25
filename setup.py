from setuptools import setup
import os, warnings

import pitchclock


def get_long_description():
    """Load the long description from the README file. In the process,
    convert the README from .md to .rst using Pandoc, if possible."""
    rst_path = os.path.join(os.path.dirname(__file__), 'README.rst')
    md_path = os.path.join(os.path.dirname(__file__), 'README.md')

    try:
        # Imported here to avoid creating a dependency in the setup.py
        # if the .rst file already exists.

        # noinspection PyUnresolvedReferences,PyPackageRequirements
        from pypandoc import convert_file
    except ImportError:
        warnings.warn("Module pypandoc not installed. Unable to generate README.rst.")
    else:
        # First, try to use convert_file, assuming Pandoc is already installed.
        # If that fails, try to download & install it, and then try to convert
        # again.
        # noinspection PyBroadException
        try:
            # pandoc, you rock...
            rst_content = convert_file(md_path, 'rst')
            with open(rst_path, 'w') as rst_file:
                for line in rst_content.splitlines(keepends=False):
                    rst_file.write(line + '\n')
        except Exception:
            try:
                # noinspection PyUnresolvedReferences,PyPackageRequirements
                from pypandoc.pandoc_download import download_pandoc

                download_pandoc()
            except FileNotFoundError:
                warnings.warn("Unable to download & install pandoc. Unable to generate README.rst.")
            else:
                # pandoc, you rock...
                rst_content = convert_file(md_path, 'rst')
                with open(rst_path, 'w') as rst_file:
                    for line in rst_content.splitlines(keepends=False):
                        rst_file.write(line + '\n')

    if os.path.isfile(rst_path):
        with open(rst_path) as rst_file:
            return rst_file.read()
    else:
        # It will be messy, but it's better than nothing...
        with open(md_path) as md_file:
            return md_file.read()


setup(
    name='pitchclock',
    version=pitchclock.__version__,
    packages=['pitchclock'],
    url=pitchclock.__url__,
    license=pitchclock.__license__,
    author=pitchclock.__author__,
    author_email=pitchclock.__author_email__,
    description='Tone clock visualizations',
    long_description=get_long_description(),
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
