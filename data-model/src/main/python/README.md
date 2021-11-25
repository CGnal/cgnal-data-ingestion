
<div align="center">
  <img src="https://cgnal.com/wp-content/uploads/2016/05/Gnal_logo.png"><br>
</div>

-----------------


# cgnal-core : DevOps library written in Python to build end to end data ingestion pipelines and provides data structures optmized for machine learning pipelines 


## What is it ?
**cgnal-core** is a Python based package that provides powerful abstractions and modular design to build data 
ingestion  pipelines and offers data structures designed for running end to end machine learning pipelines. 
The library offers lightweight objected oriented interface to MongoDB as well as Pandas based data structures. 
The aim of the library is to provide extensive 
support for developing machine learning based applications with a focus on practicing clean code and modular design. 

## Supported Python version
Currently the library supports Python 3.6.x 

## Features
Some cool features that we are proud to mention : 

### Data layers 
1. Archivers: Offers an object oriented design to perform ETL on Mongodb collections as well as Pandas DataFrames.
2. DAOs: Allow Archivers to serialize domain objects into the proper persistence layer support object, for example 
in the case of MongoDB, a DAO serializes a domain object into MongoDB document.


### Data Model 
Implements a library for the data domain model to be used in the ingestion pipelines


Offers data structures 
1. Document : A data structure specifically designed to work with NLP applications that parses a json like document 
into a Document object. 
2. Dataset : Another data structure designed to be used specifically for machine learning based applications which 
parses a Pandas DataFrame or a list of many Pandas DataFrames into a Dataset object. 

## Installation
From pypi server
```
pip install cgnal-core
```

From source
```
git clone https://github.com/CGnal/cgnal-data-ingestion.git
cd cgnal-data-ingestion/data-model/src/main/python
pip install -r requirements/requirements.txt 
pip install -r requirements/requirements_dev.txt
python setup.py install 
```

## Tests 
```
bash bin/run_tests.sh
```

## Mypy 
```
mypy --follow-imports silent path/to/python/file.py
```

## Examples 

#### Data Layers
Creating a Database of Table objects
```python
import pandas as pd 
from cgnal.data.layer.pandas.databases import Database


# sample df
df1 = pd.DataFrame([[1, 2, 3], [6, 5, 4]], columns=['a', 'b', 'c'])

# creating a database 
db = Database('/path/to/db')
table1 = db.table('df1')

#write table to path
table1.write(df1)
#get path  
table1.filename

# convert to pandas dataframe 
table1.to_df()

# get table from database 
db.__getitem__('df1')

```

Using an Archiver with Dao objects
```python
from cgnal.data.layer.pandas.archivers import CsvArchiver
from cgnal.data.layer.pandas.dao import DataFrameDAO

# create a dao object 
dao = DataFrameDAO()

# create a csv archiver 
arch = CsvArchiver('/path/to/csvfile.csv', dao)

# get pandas dataframe 
arch.data

# retrieve a single document object 
doc = next(arch.retrieve())
# retrieve a list of document objects 
docs = [i for i in arch.retrieve()]
# retrieve a document by it's id 
arch.retrieveById(doc.uuid)

# archive a single document 
doc = next(self.a.retrieve())
# update column_name field of the document with the given value
doc.data.update({'column_name': value})
# archive the document 
arch.archiveOne(doc)
#archive list of documents
a.archiveMany([doc, doc])

# get a document object as a pandas series 
arch.dao.get(doc)

```
#### Data Model

Creating a PandasDataset object 
```python
import pandas as pd 
from cgnal.data.model.ml import PandasDataset

dataset = PandasDataset(features=pd.concat([pd.Series([1, np.nan, 2, 3], name="feat1"),
                                                 pd.Series([1, 2, 3, 4], name="feat2")], axis=1),
                             labels=pd.Series([0, 0, 0, 1], name="Label"))


# access features as a pandas dataframe 
dataset.features 
# access labels as pandas dataframe 
dataset.labels
# access features as a python dictionary 
dataset.getFeaturesAs('dict')
# access features as numpy array 
dataset.getFeaturesAs('array')


# indexing operations 
# access features and labels at the given index as a pandas dataframe  
dataset.loc(2).features
dataset.loc(2).labels
```

Creating a PandasTimeIndexedDataset object
```python
import pandas as pd 
from cgnal.data.model.ml import PandasTimeIndexedDataset 

dateStr = [str(x) for x in pd.date_range('2010-01-01', '2010-01-04')]
dataset = PandasTimeIndexedDataset(
         features=pd.concat([
             pd.Series([1, np.nan, 2, 3], index=dateStr, name="feat1"),
             pd.Series([1, 2, 3, 4], index=dateStr, name="feat2")
         ], axis=1))


```

## How to contribute ? 

We are very much willing to welcome any kind of contribution whether it is bug reports, bug fixes, contributions to the 
existing codebase, enriching/improving the documentation. 

### Where to start ? 
Please look at the [Github issues tab](https://github.com/CGnal/cgnal-data-ingestion/issues) to start working on open 
issues 

### Contributing to cgnal-core 
Please make sure the general guidelines for contributing to the code base are respected
1. [Fork](https://docs.github.com/en/get-started/quickstart/contributing-to-projects) the cgnal-core repository. 
2. Create/choose an issue to work on in the [Github issues page](https://github.com/CGnal/cgnal-data-ingestion/issues). 
3. [Create a new branch](https://docs.github.com/en/get-started/quickstart/github-flow) to work on the issue. 
4. Commit your changes and run the tests to make sure the changes do not break any test. 
5. Open a Pull Request on Github referencing the issue.
6. Once the PR is approved, please do a "Rebase and Merge" operation from the Github UI. 

## Changelog

1.0.1 Refactor packages (for document models) 
