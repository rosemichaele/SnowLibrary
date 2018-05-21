import os
from urllib.parse import urlparse

import pysnow
from pysnow.exceptions import QueryEmpty
from requests.exceptions import RequestException
from robot.api import logger
from robot.api.deco import keyword


class RESTQuery:
    """
    This library implements keywords for retrieving current data for testing from ServiceNow. It leverages the 
    pysnow module. Keywords can be used in your test suite by importing SnowLibrary.RESTQuery.   Currently supported
    query types and operands are as follows (case-insensitive):
    
    VALID_QUERY_TYPES = ["EQUALS", "DOES NOT EQUAL", "CONTAINS", "DOES NOT CONTAIN" "STARTS WITH", "ENDS WITH",
                         "IS EMPTY"]
                         
    VALID_OPERANDS = ["AND", "OR", "NQ"]
    """
    VALID_QUERY_TYPES = {"EQUALS": "equals", "DOES NOT EQUAL": "not_equals",
                         "CONTAINS": "contains", "DOES NOT CONTAIN": "not_contains",
                         "STARTS WITH": "starts_with", "ENDS WITH": "ends_with",
                         "GREATER THAN": "greater_than", "LESS THAN": "less_than",
                         "IS EMPTY": "is_empty()", "BETWEEN": "between"}

    VALID_OPERANDS = {"AND": "AND()", "OR": "OR()", "NQ": "NQ()"}

    ROBOT_LIBRARY_SCOPE = "TEST CASE"

    def __init__(self, host=None, user=None, password=None, query_table=None, response=None):
        """
        The following arguments can be optionally provided when importing this library:
        - ``host``: The URL to your target ServiceNow instance (e.g. https://iceuat.service-now.com/). If none is provided,
                    the library will attempt to use the ``SNOW_TEST_URL`` environment variable.
        - ``user``: The username to use when authenticating the ServiceNow REST client. This can, and *should*, be set using
                    the ``SNOW_REST_USER`` environment variable.
        - ``password``:  The password to use when authenticating the ServiceNow REST client. This can, and *should*, be set using
                    the ``SNOW_REST_PASS`` environment variable.
        - ``query_table``: The table to query.  This can be changed or set at any time with the `Query Table Is` keyword.
        - ``response``: Set the response object from the ServiceNow REST API (intended to be used for testing).

        """
        if not host:
            self.host = os.environ.get("SNOW_TEST_URL")
        if not user:
            self.user = os.environ.get("SNOW_REST_USER")
        if not password:
            self.password = os.environ.get("SNOW_REST_PASS")
        try:
            self.instance = urlparse(self.host).netloc.split(".")[0]
        except TypeError:
            logger.error("Unable to determine SNOW Instance. Have environment variables been set correctly?")
            raise
        self.client = pysnow.Client(instance=self.instance, user=self.user, password=self.password)
        self.query_table = query_table
        self.query = pysnow.QueryBuilder()
        self.response = response

    def _add_valid_query_parameter(self, logical, field, condition_type, param_1=None, param_2=None):
        """
        Helper function to handle adding parameters to a query, which are then passed to the pysnow.QueryBuilder
        object.
        """
        qb_function = self.VALID_QUERY_TYPES.get(condition_type.upper())
        qb_operand = self.VALID_OPERANDS.get(logical.upper())
        if logical == "NONE":
            query = "self.query.field('{field}').{condition_type}".format(field=field,
                                                                          condition_type=qb_function)
        else:
            query = "self.query.{logical}.field('{field}').{condition_type}".format(field=field,
                                                                                    logical=qb_operand,
                                                                                    condition_type=qb_function)
        if not param_1 and not param_2:
            if condition_type.upper() != "IS EMPTY":
                raise AssertionError("Unexpected arguments for {condition_type}: expected 1 or 2 arguments, but got "
                                     "none.".format(condition_type=condition_type))
            else:
                logger.debug("Query added is: {query}".format(query=query))
                logger.debug("sysparm_query contains: {q}".format(q=self.query._query))
                self.query = eval(query)

        elif not param_2:
            if condition_type in ["IS EMPTY", "BETWEEN"]:
                raise AssertionError("Unexpected arguments for {condition_type}: expected 0 or 2 arguments,"
                                     " but got 1.".format(condition_type=condition_type))
            else:
                if condition_type.upper() in ["GREATER THAN", "LESS THAN"]:
                    query += "({param})".format(param=param_1)
                else:
                    query += "('{param}')".format(param=param_1)
                logger.debug("Query added is: {query}".format(query=query))
                logger.debug("sysparm_query contains: {q}".format(q=self.query._query))
                self.query = eval(query)

        else:
            if condition_type.upper() != "BETWEEN":
                raise AssertionError("Unexpected arguments for {condition_type}: expected 0 or 1 argument,"
                                     " but got 2.".format(condition_type=condition_type))
            else:
                query += "({param_1}, {param_2})".format(param_1=param_1, param_2=param_2)
                logger.debug("Query added is: {query}".format(query=query), html=True)
                logger.debug("sysparm_query is contains: {q}".format(q=self.query._query))
                self.query = eval(query)

    def _query_is_empty(self):
        """Checks if there are any current query parameters."""
        return not self.query.current_field

    def _reset_query(self):
        """
        Used to reset the current query object in case multiple queries are required during a single test case.
        Intended to be used after a query is executed.
        """
        self.query = pysnow.QueryBuilder()

    def get_record_by_sys_id(self, sys_id):
        """
        Helper method to retrieve an individual SNOW record given the sys_id. Query table must already be set.
        Any other un-executed query parameters will be lost.
        """
        assert self.query_table is not None, "Query table must already be specified in this test case, but is not."
        self._reset_query()
        self.required_query_parameter_is("sys_id", "EQUALS", sys_id)
        self.execute_query()
        return self.response

    @keyword
    def query_table_is(self, query_table):
        """Sets the table that will be used for the query."""
        self.query_table = query_table
        logger.info("Query table is: {query_table}".format(query_table=query_table))

    @keyword
    def add_query_parameter(self, logical, field, condition_type, param_1=None, param_2=None):
        """
        Adds a parameter to the query.  Expected arguments are a logical operator (e.g. AND, OR, NQ), the field or table
        column to use (e.g. number, state), the condition type, and up to 2 query parameters depending on the type of 
        query.  For example, the EMPTY query type does not require any parameters, CONTAINS requires one parameter, and 
        BETWEEN requires two parameters.
        """
        if logical == "NONE":
            if not self._query_is_empty():
                logger.error("No logical operator specified.")
                raise AssertionError("This is not the first parameter in the query, so you must first specify "
                                     "once of the following logical operators to add it: AND, OR, NQ. Alternatively, "
                                     "you can remove the first parameter.")
            else:
                self._add_valid_query_parameter(logical, field.lower(), condition_type, param_1, param_2)
        else:
            if logical.upper() in self.VALID_OPERANDS and condition_type.upper() in self.VALID_QUERY_TYPES:
                self._add_valid_query_parameter(logical, field.lower(), condition_type, param_1, param_2)
            else:
                raise AssertionError("Invalid operand '{l}' and/or query type '{q}'.".format(l=logical, q=condition_type))

    @keyword
    def required_query_parameter_is(self, field, condition_type, param_1=None, param_2=None):
        """
        Adds the first (required) query parameter to a SNOW Query.  If another parameter has already been added, 
        this keyword will fail. Otherwise, this is the same as `Add Query Parameter`.
        """
        self.add_query_parameter("NONE", field.lower(), condition_type, param_1, param_2)

    @keyword
    def execute_query(self):
        """
        Executes the query that has been created with the specified conditions AND sets the response to the first record
        in the returned data or None. If no query parameters are provided, an error is thrown. Keyword usage with 2+ 
        data records is not yet supported.
        """
        query_resource = self.client.resource(api_path="/table/{query_table}".format(query_table=self.query_table))
        try:    # Catch empty queries or errors making the request
            self.response = query_resource.get(query=self.query, stream=True).first_or_none()
        except (QueryEmpty, RequestException) as e:
            logger.error(e.args)
            self._reset_query()
            raise
        self._reset_query()

    @keyword
    def get_individual_response_field(self, field_to_get):
        """
        Returns the specified data field from the first record on the response, if available.
        Otherwise, an error is thrown.
        """
        if not self.response:
            logger.error("No data matching query conditions was returned.")
            raise AssertionError("Failed to retrieve data required for this test.")
        try:
            data = self.response[field_to_get]
        except KeyError:
            logger.error("Field not found in response from {table}: {field}".format(table=self.query_table,
                                                                                    field=field_to_get))
            raise
        return data
