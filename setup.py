import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


install_requires = [
    "aiohttp",
]


setuptools.setup(
    name="laviewset-algebra8",
    version="0.0.1",
    author="Milad M. Nasrollahi",
    author_email="milad.m.nasr@gmail.com",
    description="A Lyte (light) Async Viewset.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Algebra8/LAViewSet",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=install_requires
)