from setuptools import setup
setup(
    name = "django-shoogie",
    version = "0.2.1",
    description = "Log server errors to database",
    author = "Aryeh Leib Taurog",
    author_email = "python@aryehleib.com",
    url = "http://bitbucket.org/altaurog/django-shoogie",
    packages = ['shoogie'],
    install_requires = ['django>=1.3'],
)
