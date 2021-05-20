import sys

from setuptools import setup, find_packages

with open("requirements.txt", "r") as fid:
    reqs = [line.replace("\n", "") for line in fid.readlines()]


def readme():
    with open('README.md') as f:
        return f.read()


def get_version(VERSIONFILE="cgnal/_version.py"):
    import re
    verstrline = open(VERSIONFILE, "rt").read()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        return mo.group(1)
    else:
        raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))


if sys.version_info < (3, 7):
    sys.exit('Sorry, Python < 3.7 is not supported')

setup(
    name='cgnal-core',
    version=get_version(),
    description='Python Core Functionalities Package',
    long_description=readme(),
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=reqs,
    test_suite='nose.collector',
    tests_require=['nose'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: MacOS X',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.7',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Topic :: Scientific/Engineering :: Artificial Intelligence'
    ],
    url='https://github.com/CGnal/cgnal-data-ingestion',
    author='CGnal',
    author_email='datascience@cgnal.com',
    package_data={"tests": ['../resources/tests/data/*']},
    include_package_data=True,
)
