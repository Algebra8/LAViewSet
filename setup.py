import setuptools
import codecs
import os.path


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_package_info(rel_path):
    vals = {'author': '', 'email': '', 'version': ''}

    def get_delim(_line):
        return '"' if '"' in _line else "'"

    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            vals['version'] = line.split(get_delim(line))[1]
        elif line.startswith('__author__'):
            vals['author'] = line.split(get_delim(line))[1]
        elif line.startswith('__email__'):
            vals['email'] = line.split(get_delim(line))[1]

    if not all(vals.values()):
        raise RuntimeError(
            f"Unable to find one of the following: {vals.keys()}"
        )

    return vals


package_info = get_package_info("laviewset/__init__.py")

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="LAViewSet",
    version=package_info['version'],
    author=package_info['author'],
    author_email=package_info['email'],
    description="A Lyte (light) Async Viewset.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Algebra8/LAViewSet",
    packages=setuptools.find_packages(exclude=['tests*']),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 2 - Pre-Alpha",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
    ],
    python_requires='>=3.7',
    install_requires=["aiohttp"]
)
