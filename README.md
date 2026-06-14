# pandas-dbtools

pandas-dbtools is an example of using the OCI Python SDK for the Database Tools Runtime service.

This code serves as a proof of concept for the blog post written here:

- https://icodealot.com/posts/build-tools-that-speak-to-data-in-oci

This example demonstrates a basic integration that allows a user to convert SQL results into a
Pandas DataFrame. The idea is that a data scientist, analyst, Pandas user, etc. can use a familiar
interface (Python and notebooks) to import data from relational sources in the cloud through the 
Database Tools runtime service.

For this to work I make some assumptions:

1. An Oracle Cloud Infrastructure (OCI) tenancy exists
2. An OCI CLI configuration file is setup with a valid profile (such as "DEFAULT")
3. A valid Database Tools connection resource is setup
4. The database user of the connection has access to the database objects for the query

Finally, pandas-dbtools not a production solution, it is just an example of what is possible! 
There is plenty of room for improvement and edge case handling. For example, you might want
to add session token authentication or support for running multiple statements and returning
a list of DataFrame objects.

Here is what the example does:

```
   Pandas user          pandas-dbtools     OCI Database Tools        Target
  (notebook/REPL)        (read_sql)         Runtime service         database
        |                    |                      |                   |
        |  read_sql(query,   |                      |                   |
        |    connection_id,  |                      |                   |
        |    oci_profile)    |                      |                   |
        |------------------->|                      |                   |
        |                    | load OCI config      |                   |
        |                    | for profile + build  |                   |
        |                    | runtime client       |                   |
        |                    |                      |                   |
        |                    | ExecuteSql request   |                   |
        |                    | (statement_text,     |                   |
        |                    |  connection_id)      |                   |
        |                    |--------------------->|                   |
        |                    |                      | run SQL over the  |
        |                    |                      |connection (HTTPS) |
        |                    |                      |------------------>|
        |                    |                      |                   |
        |                    |                      |   result-set rows |
        |                    |                      |<------------------|
        |                    |  ExecuteSql response |                   |
        |                    |   (statement items,  |                   |
        |                    |    result-set)       |                   |
        |                    |<---------------------|                   |
        |                    | build DataFrame      |                   |
        |                    | from result-set rows |                   |
        |  Pandas DataFrame  |                      |                   |
        |<-------------------|                      |                   |
        |                    |                      |                   |
```

Note, Python exceptions are simply raised for the caller to handle as needed.


## Example Usage

Here is an example of how this library can be used to query data to be converted to a Pandas
DataFrame in response.

```python
import pandas_dbtools as dbt

# Identify the Database Tools connection to use
connection_id = "ocid1.databasetoolsconnection.oc1.phx.aaaaaaaexampleocid"

# Define a SQL query to execute
select_iris_data = """
    select
        sepal_length,
        sepal_width,
        petal_length,
        petal_width,
        class_label
    from iris_data;
    """

# Save the result as a DataFrame for further model training and analysis tasks
df = dbt.read_sql(
    query=select_iris_data,
    connection_id=connection_id,
    oci_profile="DEFAULT"
)
...

X = df[["sepal_length", "sepal_width", "petal_length", "petal_width"]]
y = df["class_label"]
...
```

Given the above, users of Database Tools connections and the new Database Tools Runtime service will
be able to extract relevant samples from a database and work with them as DataFrames in a notebook.

Here is an example of pandas-dbtools running in a Jupyter notebook runtime locally.

TODO: capture screenshot


## Install from Github

First, you will need to import the library into your Python REPL or notebook. Since this package
is not published, you can do this by pulling from git directly:

```python
!pip install git+https://github.com/icodealot/pandas-dbtools.git
```

