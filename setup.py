from setuptools import setup, find_packages


setup(
    name = "piwikapi",
    version = "0.2.2",
    packages = find_packages(),
    test_suite = 'piwikapi.tests',

    # PyPI
    author = "Nicolas Kuttler",
    author_email = "pypi@kuttler.eu",
    description = "Python Piwik API",
    license = "BSD",
    long_description = open("README.rst").read(),
    url = "http://github.com/nkuttler/python-piwikapi",
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
)
