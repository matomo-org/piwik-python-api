try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from distutils.core import Extension, Command


class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys, subprocess
        raise SystemExit(
            subprocess.call([sys.executable,
                # Turn on deprecation warnings
                '-Wd',
                'piwikapi/tests/__init__.py']))

cmdclass = dict(test=TestCommand)
kw = dict(cmdclass=cmdclass)
setup(
    name = "piwikapi",
    version = "0.2.2",
    author = "Nicolas Kuttler",
    author_email = "pypi@kuttler.eu",
    description = "Python Piwik API",
    long_description = open("README.rst").read(),
    license = "BSD",
    url = "http://github.com/nkuttler/python-piwikapi",
    packages = ['piwikapi', 'piwikapi.tests'],
#    include_package_data = True,
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    **kw
#    zip_safe = True,
)
