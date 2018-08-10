import os
from datetime import datetime
from urllib.parse import urlparse

import pysnow
from pysnow.exceptions import QueryEmpty
from requests.exceptions import RequestException
from robot.api import logger
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn


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
        if host is None:
            self.host = os.environ.get("SNOW_TEST_URL")
        else:
            self.host = host
        if user is None:
            self.user = os.environ.get("SNOW_REST_USER")
        else:
            self.user = user
        if password is None:
            self.password = os.environ.get("SNOW_REST_PASS")
        else:
            self.password = password
        if "http" not in self.host:
            self.instance = urlparse(self.host).path.split(".")[0]
        else:
            self.instance = urlparse(self.host).netloc.split(".")[0]
        if self.instance == "":
            raise AssertionError("Unable to determine SNOW Instance. Verify that the SNOW_TEST_URL environment variable been set.")
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
                raise AssertionError("Unexpected arguments for condition type {condition_type}: expected 1 or 2 arguments, but got "
                                     "none.".format(condition_type=condition_type.upper()))
            else:
                logger.debug("Query added is: {query}".format(query=query))
                logger.debug("sysparm_query contains: {q}".format(q=self.query._query))
                self.query = eval(query)

        elif not param_2:
            if condition_type.upper() in ["IS EMPTY", "BETWEEN"]:
                raise AssertionError("Unexpected arguments for condition type {condition_type}: expected 0 or 2 arguments,"
                                     " but got 1.".format(condition_type=condition_type.upper()))
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
                raise AssertionError("Unexpected arguments for condition type {condition_type}: expected 0 or 1 argument,"
                                     " but got 2.".format(condition_type=condition_type.upper()))
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

    @keyword
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
                raise AssertionError("This is not the first parameter in the query, so you must first specify "
                                     "one of the following logical operators to add it: AND, OR, NQ. Alternatively, "
                                     "you can remove the first parameter.")
            elif condition_type.upper() not in self.VALID_QUERY_TYPES:
                raise AssertionError("Invalid condition type specified.")
            else:
                self._add_valid_query_parameter(logical, field.lower(), condition_type, param_1, param_2)

        else:
            if self._query_is_empty():
                raise AssertionError("No query parameters have been specified yet. Use the ``Required Query Parameter Is`` keyword first.")
            elif logical.upper() in self.VALID_OPERANDS and condition_type.upper() in self.VALID_QUERY_TYPES:
                self._add_valid_query_parameter(logical, field.lower(), condition_type, param_1, param_2)
            else:
                raise AssertionError("Invalid operand and/or query type.".format(l=logical, q=condition_type))

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
        assert self.query_table is not None, "Query table must already be specified in this test case, but is not."
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
            raise AssertionError("Field not found in response from {table}: {field}".format(table=self.query_table, field=field_to_get))
        return data

    @keyword
    def get_records_created_after(self, when):
        """Returns the number of records created in the defined query_table after ``when``. The argument ``when`` must
        be in the following format: ``YYYY-MM-DD hh:mm:ss``. Use Robot Framework's BuiltIn Library keyword `Get Time` to
        dynamically get the required time in this format. The query table must be set using `Query Table Is` keyword
        first.  This cannot be used in conjunction with other query parameters at this time and any other previously 
        provided parameters in the test case will be ignored when making this query. NOTE: if the number of records 
        exceeds 10K, 10K will STILL be the number returned. Example usage:
        
        | Query Table Is            | proc_po                   |
        | ${time}=                  | Get Time                  |                       # Returns YYYY-MM-DD hh:mm:ss |
        | ${actual_num}=            | Get Records Created After | ${time}         |     # Returns the number of records created in proc_po after the given time. |
        | Should Be Equal           | ${actual_num}             | ${expected_num} |    
        """
        bi = BuiltIn()
        now = bi.get_time()
        return self.get_records_created_in_date_range(when, now)

    @keyword
    def get_records_created_before(self, when):
        """Returns the number of records created in the defined query_table before ``when``. The argument ``when`` must
        be in the following format: ``YYYY-MM-DD hh:mm:ss``. Use Robot Framework's BuiltIn Library keyword `Get Time` to
        dynamically get the required time in this format. The query table must be set using `Query Table Is` keyword
        first.  This cannot be used in conjunction with other query parameters at this time and any other previously 
        provided parameters in the test case will be ignored when making this query. NOTE: if the number of records 
        exceeds 10K, 10K will STILL be the number returned. Example usage:

        | Query Table Is            | proc_po                       |
        | ${time}=                  | Get Time                      |                       # Returns YYYY-MM-DD hh:mm:ss |
        | ${actual_num}=            | Get Records Created before    | ${time}         |     # Returns the number of records created in proc_po before the given time. |
        | Should Be Equal           | ${actual_num}                 | ${expected_num} |    
        """
        return self.get_records_created_in_date_range('1970-01-01 00:00:01', when)

    @keyword
    def get_records_created_in_date_range(self, start, end):
        """Returns the number of records created in the defined query_table between ``start`` and ``end``. The arguments
        must be in this format: ``YYYY-MM-DD hh:mm:ss``. Use Robot Framework's BuiltIn Library keyword `Get Time` to
        dynamically get required times in this format. The query table must be set using `Query Table Is` keyword
        first.  This cannot be used in conjunction with other query parameters at this time and any other previously 
        provided parameters in the test case will be ignored when making this query. NOTE: if the number of records 
        exceeds 10K, 10K will STILL be the number returned. Example usage:

        | Query Table Is            | proc_po                           |
        | ${start_time}=            | 1970-01-01 00:00:01               | # The date can be provided directly if desired. |
        | ${end_time}=              | Get Time                          | # Returns YYYY-MM-DD hh:mm:ss |
        | ${actual_num}=            | Get Records Created In Date Range | ${start_time}   | ${end_time} |
        | Should Be Equal           | ${actual_num}                     | ${expected_num} |    
        """
        assert self.query_table is not None, "Query table must already be specified in this test case, but is not."
        try:
            start_year, start_month, start_day = start.split()[0].split("-")
            start_hour, start_minute, start_second = start.split()[1].split(":")
            end_year, end_month, end_day = end.split()[0].split("-")
            end_hour, end_minute, end_second = end.split()[1].split(":")
            start = datetime(int(start_year), int(start_month), int(start_day), int(start_hour), int(start_minute),
                             int(start_second))
            end = datetime(int(end_year), int(end_month), int(end_day), int(end_hour), int(end_minute), int(end_second))
        except (KeyError, ValueError, IndexError):
            raise AssertionError("Input date arguments were not provided in the correct format. Verify that they are in"
                                 " the format YYYY-MM-DD hh:mm:ss.")

        query_resource = self.client.resource(api_path="/table/{query_table}".format(query_table=self.query_table))
        fields = ['sys_id']
        content = query_resource.get(query="sys_created_onBETWEENjavascript:gs.dateGenerate('{start}')@javascript:gs.dateGenerate('{end}')".format(start=start, end=end), fields=fields)
        num_records = len(content.all())
        logger.info("Found {num} records in date range.".format(num=num_records))
        return num_records
