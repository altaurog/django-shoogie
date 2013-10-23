from os.path import join, dirname
from setuptools import setup

def read(filename):
    f = open(join(dirname(__file__), filename))
    return f.read()


setup(
    name = "django-shoogie",
    version = "0.4",
    description = "Log server errors to database",
    long_description = read("README.rst"),
    author = "Aryeh Leib Taurog",
    author_email = "python@aryehleib.com",
    url = "http://bitbucket.org/altaurog/django-shoogie",
    packages = ["shoogie"],
    install_requires = ["django>=1.3"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Environment :: Web Environment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: System :: Logging",
        "Topic :: Database",
        "Framework :: Django",
    ],
)
