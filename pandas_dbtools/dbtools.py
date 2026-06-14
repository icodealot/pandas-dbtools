_runtime_client = None 
_active_profile = None


def read_sql(query=None, connection_id=None, oci_profile="DEFAULT", pandas_kqargs=None):
    """
    Uses the Database Tools Runtime to execute a SQL query and return the resultset as 
    a Pandas DataFrame object.
    """

    if not query or not query.strip():
        raise ValueError("A SQL query is required")
    if not connection_id or not connection_id.strip():
        raise ValueError("A connection id is required")
    if not oci_profile or not oci_profile.strip():
        raise ValueError("An oci profile name is required")

    # Use the Database Tools Runtime SDK client to execute a SQL query
    response = _get_runtime_response(
        query=query,
        connection_id=connection_id,
        oci_profile=oci_profile,
    )
    return _response_to_dataframe(data=response.data, pandas_kqargs=pandas_kqargs)


def _get_runtime_response(query=None, connection_id=None, oci_profile=None):
    models = _oci_sdk_runtime_models()

    details = models.ExecuteSqlDatabaseToolsConnectionSynchronousDetails(
        input=models.ExecuteSqlInputStandardDetails(
            statement_text=query,
        )
    )

    client = _get_runtime_client(oci_profile=oci_profile)

    try:
        return client.execute_sql_database_tools_connection(
            database_tools_connection_id=connection_id,
            execute_sql_database_tools_connection_details=details,
        )
    except Exception as e:
        raise ValueError(f"Error executing query using connection {connection_id}") from e


def _response_to_dataframe(data=None, pandas_kqargs=None):
    pd = _pandas()
    pandas_kqargs = pandas_kqargs or {}

    statements = _value(data, "items") or []

    if not statements:
        return pd.DataFrame(**pandas_kqargs)

    statement = statements[0]
    error = _value(statement, "error")
    if error:
        raise ValueError(f"Statement resulted in an error: {error}")

    result_set = _value(statement, "result-set")
    rows = _value(result_set, "items") or []
    return pd.DataFrame(rows, **pandas_kqargs)


def _value(obj=None, name=None):
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get(name, obj.get(name.replace("-","_"), None))
    return getattr(obj, name.replace("-","_"), None)


def _get_runtime_client(oci_profile=None):
    """Returns an instance of the Database Tools Runtime client"""

    global _runtime_client
    global _active_profile

    if _runtime_client and _active_profile == oci_profile:
        return _runtime_client

    try:
        oci_config = _oci().config.from_file(profile_name=oci_profile)
    except Exception as e:
        raise RuntimeError(f"Error reading OCI config file for profile {oci_profile}") from e

    _runtime_client = _oci().database_tools_runtime.DatabaseToolsRuntimeClient(oci_config)
    _active_profile = oci_profile

    return _runtime_client


def _oci():
    try:
        import oci
    except ImportError as e:
        raise RuntimeError("The OCI Python SDK is required to use pandas-dbtools") from e
    return oci


def _oci_sdk_runtime_models():
    try:
        from oci.database_tools_runtime import models
    except ImportError as e:
        raise RuntimeError("The OCI Python SDK is required to use pandas-dbtools") from e
    return models


def _pandas():
    try:
        import pandas as pd
    except ImportError as e:
        raise RuntimeError("Pandas is required to use pandas-dbtools") from e
    return pd
