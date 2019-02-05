# PyCondusco

## Overview

pycondusco lets you run a function iteratively, passing it the rows of a dataframe or the results of a query.

We call the functions pycondusco runs pipelines, and define a pipeline as a function that accepts a list of parameters and run a series of customized commands based on the values of the parameters.

The most common use case for pycondusco are data pipelines.  For data pipelines that primarily run SQL queries, we can template queries with a library (ie. [pystache](https://github.com/defunkt/pystache)), so that parametrized values are separated from the query logic.  We can then render the query with the appropriate values:

```
import pycondusco
from pycondusco.run_pipeline import run_pipeline
import pystache

json_string = '{"first_name": "First", "last_name":"Last"}'

params = [
    {
        'k1':'v1',
        'k2':'v2',
    },
    {
        'k1':'v1',
        'k2': json_string,
    },
]

def pipeline(params):
    print pystache.render('k1 value is {{k1}}, k2 is {{k2}}',params)

run_pipeline(pipeline,params)
```


pycondusco provides the following extensions in functionality to the above design pattern:
 - the user can provide a query and each row of results is iteratively passed to the pipeline
 - any JSON-string parameter will be converted to an object before being passed to the pipeline
 

## Functions

|function|description|
|:--------------|:--------------|
|run_pipeline(pipeline, parameters)| iteratively pass each row of parameters to a pipeline, converting any JSON parameters to objects|
|run_pipeline_gbq(pipeline, query, project)|calls run_pipeline with the results of query executed via bigquery|


## Installation

```
pip install pycondusco
```

## Features

*   Name-based substitution of query-results including JSON into pipelines, iterating through rows of parameters dataframe:
```
import pystache
from google.cloud import bigquery
import pycondusco
from pycondusco.run_pipeline_gbq import run_pipeline_gbq

client = bigquery.Client()

def pipeline(params):
    query = """
      SELECT
        {{#list}}
          SUM(CASE WHEN author.name ='{{name}}' THEN 1 ELSE 0 END) as n_{{name_clean}},
        {{/list}}
        repo_name
      FROM `bigquery-public-data.github_repos.sample_commits`
      GROUP BY repo_name
    """

    query_job = client.query(pystache.render(query, params))
    results = query_job.result()  # Waits for job to complete.
    for row in results:
        print(dict(row.items()))


query = """
   SELECT CONCAT('[',
   STRING_AGG(
     CONCAT('{\"name\":\"',name,'\",'
       ,'\"name_clean\":\"', REGEXP_REPLACE(name, r'[^[:alpha:]]', ''),'\"}'
     )
   ),
   ']') as list
   FROM (
     SELECT author.name,
       COUNT(commit) n_commits
     FROM `bigquery-public-data.github_repos.sample_commits`
     GROUP BY 1
     ORDER BY 2 DESC
     LIMIT 10
   )
"""

run_pipeline_gbq(pipeline, client, query)
```

