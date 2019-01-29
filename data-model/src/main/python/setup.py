from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='cgnal-core',
    version='1.0.2',
    description='Python Analytics Package Core Functionalities',
    long_description=readme(),
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    test_suite='nose.collector',
    tests_require=['nose'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: MacOS X',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 2.7',
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
