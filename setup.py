from distutils.core import setup


setup(
    name = "piwikapi",
    version = "0.2.2",
    packages = (
        'piwikapi',
        'piwikapi.plugins',
        'piwikapi.tests',
    ),
    #test_suite = 'piwikapi.tests',

    # PyPI
    author = "Nicolas Kuttler",
    author_email = "pypi@kuttler.eu",
    description = "Python Piwik API",
    license = "BSD",
    long_description = open("README.rst").read(),
    url = "https://github.com/piwik/piwik-python-api",
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
    extras_require = {
        'Python 2.5':  ["simplejson", ],
    }
)
