try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name = "piwikapi",
    version = "0.2",
    author = "Nicolas Kuttler",
    author_email = "pypi@nicolaskuttler.com",
    description = "Piwik tracking API for Django",
    long_description = open("README.rst").read(),
    license = "BSD",
    url = "http://github.com/nkuttler/python-piwikapi",
    packages = ['piwik_tracking'],
    include_package_data = True,
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ],
    install_requires = [
        "Django >= 1.3",
    ],
    zip_safe = True,
)
