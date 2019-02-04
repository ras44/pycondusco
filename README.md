# PyCondusco

## Overview

pycondusco lets you run a function iteratively, passing it the rows of a dataframe or the results of a query.

We call the functions pycondusco runs pipelines, and define a pipeline as a function that accepts a list of parameters and run a series of customized commands based on the values of the parameters.

The most common use case for pycondusco are data pipelines.  For data pipelines that primarily run SQL queries, we can template queries with a library (ie. [whisker](https://github.com/edwindj/whisker)), so that parametrized values are separated from the query logic.  We can then render the query with the appropriate values:

```
parameters <- source("params.R")

#define a pipeline
pipeline <- function(parameters){
 query <- "SELECT * FROM {{dataset}}.{{table_prefix}}_results LIMIT {{limit_size}}"
 query_with_params <- whisker.render(query, parameters)
 run_query(query_with_params)
}

# run the pipeline with the parameters in 'params.R'
pipeline(parameters)
```


pycondusco provides the following extensions in functionality to the above design pattern:
 - the user can provide a data-frame that contains multiple rows of parameters to be iteratively passed to the pipeline
 - the user can provide a query and each row of results is iteratively passed to the pipeline
 - any JSON-string parameter will be converted to an object before being passed to the pipeline
 

## Functions

|function|description|
|:--------------|:--------------|
|run_pipeline(pipeline, parameters)| iteratively pass each row of parameters to a pipeline, converting any JSON parameters to objects|
|run_pipeline_gbq(pipeline, query, project)|calls run_pipeline with the results of query executed via bigrquery|
|run_pipeline_dbi(pipline, query, con)|calls run_pipeline with the results of query executed via DBI|


## Installation

```{r, eval = FALSE}
install.packages("pycondusco")
```

## Features

*   Name-based substitution of local parameters into pipelines, iterating through rows of parameters:
    
    ```{r}
    run_pipeline(
      #the pipeline
      function(parameters){
        query <- "SELECT * FROM {{table_prefix}}_results;"
        print(whisker.render(query,parameters))
      },
      #the parameters
      data.frame(
        table_prefix = c('batman', 'robin')
      )
    )
    ```



*   Name-based substitution of query-results into pipelines, iterating through rows of parameters dataframe:
    
    ```{r}
    con <- dbConnect(RSQLite::SQLite(), ":memory:")

    pipeline <- function(parameters){

      query <-"
        SELECT count(*) as n_hits 
        FROM user_hits 
        WHERE date(date_time) BETWEEN date('{{{date_low}}}') AND date('{{{date_high}}}')
      ;"

      whisker.render(query,parameters)

    }

    run_pipeline_dbi(pipeline,
      "SELECT date('now', '-5 days') as date_low, date('now') as date_high",
      con
    )

    dbDisconnect(con)
    ```


*   Dynamic query generation based on JSON strings:
    
    ```{r}
    con <- dbConnect(RSQLite::SQLite(), ":memory:")
    mtcars
    dbWriteTable(con, "mtcars", mtcars)

    #for each cylinder count, count the number of top 5 hps it has
    pipeline <- function(swap){

      query <- "SELECT
        {{#list}}
          SUM(CASE WHEN hp='{{val}}' THEN 1 ELSE 0 END )as n_hp_{{val}},
        {{/list}}
        cyl
        FROM mtcars
        GROUP BY cyl
      ;"

      print(whisker.render(query,swap))

      print(
        dbGetQuery(
          con,
          whisker.render(query,swap)
        )
      )
    }


    #pass the top 5 most common hps as val parameters
    run_pipeline_dbi(
      pipeline,
      '
      SELECT "[" || GROUP_CONCAT("{ ""val"": """ || hp ||  """ }") || "]" AS list
      FROM (
        SELECT 
          CAST(hp as INTEGER) as HP,
          count(hp) as cnt
        FROM mtcars 
        GROUP BY hp
        ORDER BY cnt DESC
        LIMIT 5
      )
      ',
      con
    )


    dbDisconnect(con)
    ```


