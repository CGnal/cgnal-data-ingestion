from setuptools import setup, find_packages


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


setup(
    name='cgnal-core',
    version=get_version(),
    description='Python Core Functionalities Package',
    long_description=readme(),
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        "pymongo>=3.6",
        "mongomock>=3.19",
        "numpy>=1.16",
        "setuptools>=40.3",
        "PyYAML>=5.1",
        "pandas>=1.0",
        "requests>=2.22",
        "cfg-load>=0.8",
        "dill>=0.3"
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: MacOS X',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.6',
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
