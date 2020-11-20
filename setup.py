import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="laviewset-algebra8", # Replace with your own username
    version="0.0.1",
    author="Milad M. Nasrollahi",
    author_email="milad.m.nasr@gmail.com",
    description="A Lyte (light) Async Viewset.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)