import setuptools
from setuptools import find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Pjono",
    version="0.0.1",
    author="Xp-op",
    author_email="muhammad184276@gmail.com",
    description="a Web Framework made by Xp-op",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Xp-op/Pjono",
    project_urls={
        "Bug Tracker": "https://github.com/Xp-op/Pjono/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_data={"Pjono":["PAGES/*.html"]},
    include_package_data=True,
    packages=["Pjono", "Pjono.PAGES", "Pjono.PARSE"],
    python_requires=">=3.6",
)
