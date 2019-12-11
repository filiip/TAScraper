import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="TAScraper-fib",
    version="0.0.1",
    author="Filip Burda",
    author_email="burda.filip@yahoo.com",
    description="Trip Adviser review scraper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/filiip/TAScraper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
