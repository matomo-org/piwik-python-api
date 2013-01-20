try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name = "piwikapi",
    version = "0.2.2",
    author = "Nicolas Kuttler",
    author_email = "pypi@kuttler.eu",
    description = "Python Piwik API",
    long_description = open("README.rst").read(),
    license = "BSD",
    url = "http://github.com/nkuttler/python-piwikapi",
    packages = ['piwikapi'],
    include_package_data = True,
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    zip_safe = True,
)
