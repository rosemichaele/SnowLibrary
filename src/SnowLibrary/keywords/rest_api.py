import os
import sys
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

    *Valid query types*:
     - ``EQUALS``
     - ``DOES NOT EQUAL``
     - ``CONTAINS``
     - ``DOES NOT CONTAIN``
     - ``STARTS WITH``
     - ``ENDS WITH``
     - ``IS EMPTY``
     - ``GREATER THAN``
     - ``LESS THAN``

    *Valid query operators*:
     - ``AND``
     - ``OR``
     - ``NQ``
    """
    ROBOT_LIBRARY_SCOPE = "TEST CASE"

    VALID_QUERY_TYPES = ["EQUALS", "DOES NOT EQUAL", "CONTAINS", "DOES NOT CONTAIN", "STARTS WITH", "ENDS WITH",
                         "IS EMPTY", "GREATER THAN", "LESS THAN", "BETWEEN"]

    VALID_OPERANDS = ["AND", "OR", "NQ"]

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
            raise AssertionError(
                "Unable to determine SNOW Instance. Verify that the SNOW_TEST_URL environment variable been set.")
        self.client = pysnow.Client(instance=self.instance, user=self.user, password=self.password)
        self.query_table = query_table
        self.query = pysnow.QueryBuilder()
        self.response = response

    @staticmethod
    def _parse_datetime(date):
        """
        Parse an input date string in the form ``YYYY-MM-DD hh:mm:ss`` and return an equivalent Python datetime object.
        """
        try:
            year, month, day = date.split()[0].split("-")
            hour, minute, second = date.split()[1].split(":")
            dt = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        except (KeyError, ValueError, IndexError):
            raise AssertionError("Input date arguments were not provided in the correct format. Verify that they are in"
                                 " the format YYYY-MM-DD hh:mm:ss.")
        return dt

    def _add_valid_query_parameter(self, logical, field, condition_type, param_1=None, param_2=None):
        """
        Helper function to handle adding parameters to a query, which are then passed to the pysnow.QueryBuilder
        object.
        """
        if logical == "NONE":
            self.query.field('{}'.format(field))
        elif logical.upper() == "AND":
            self.query.AND().field('{}'.format(field))
        elif logical.upper() == "OR":
            self.query.AND().field('{}'.format(field))
        else:
            self.query.NQ().field('{}'.format(field))

        if param_1 is None and param_2 is None:
            if condition_type.upper() != "IS EMPTY":
                raise AssertionError(
                    "Unexpected arguments for condition type {condition_type}: expected 1 or 2 arguments, but got "
                    "none.".format(condition_type=condition_type.upper()))
            else:
                logger.debug("sysparm_query contains: {q}".format(q=self.query._query))
                self.query.is_empty()

        elif param_2 is None:
            if condition_type.upper() in ["IS EMPTY", "BETWEEN"]:
                raise AssertionError(
                    "Unexpected arguments for condition type {condition_type}: expected 0 or 2 arguments,"
                    " but got 1.".format(condition_type=condition_type.upper()))
            else:
                if condition_type.upper() == "GREATER THAN":
                    if isinstance(param_1, datetime):
                        self.query.greater_than(param_1)
                    else:
                        try:
                            self.query.greater_than(int(param_1))
                        except AssertionError:
                            raise AssertionError("Invalid parameter for this query type, must be an integer or a date.")
                elif condition_type.upper() == "LESS THAN":
                    if isinstance(param_1, datetime):
                        self.query.less_than(param_1)
                    else:
                        try:
                            self.query.less_than(int(param_1))
                        except AssertionError:
                            raise AssertionError("Invalid parameter for this query type, must be an integer or a date.")
                elif condition_type.upper() == "EQUALS":
                    self.query.equals('{}'.format(param_1))
                elif condition_type.upper() == "DOES NOT EQUAL":
                    self.query.not_equals('{}'.format(param_1))
                elif condition_type.upper() == "CONTAINS":
                    self.query.contains('{}'.format(param_1))
                elif condition_type.upper() == "DOES NOT CONTAIN":
                    self.query.not_contains('{}'.format(param_1))
                elif condition_type.upper() == "STARTS WITH":
                    self.query.starts_with('{}'.format(param_1))
                elif condition_type.upper() == "ENDS WITH":
                    self.query.ends_with('{}'.format(param_1))
                logger.debug("sysparm_query contains: {q}".format(q=self.query._query))

        else:
            if condition_type.upper() != "BETWEEN":
                raise AssertionError(
                    "Unexpected arguments for condition type {condition_type}: expected 0 or 1 argument,"
                    " but got 2.".format(condition_type=condition_type.upper()))
            else:
                if isinstance(param_1, datetime) and isinstance(param_2, datetime):
                    self.query.between(param_1, param_2)
                else:
                    try:
                        self.query.between(int(param_1), int(param_2))
                    except AssertionError:
                        raise AssertionError("Invalid parameter for this query type, must be and integer or a date")
                logger.debug("sysparm_query contains: {q}".format(q=self.query._query))

    def _query_is_empty(self):
        """Checks if there are any current query parameters."""
        return not self.query._query

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
    def add_query_parameter(self, logical, field, condition_type, param_1=None, param_2=None, is_date_field=False):
        """
        Adds a parameter to the query.  Expected arguments are a logical operator (e.g. AND, OR, NQ), the field or table
        column to use (e.g. number, state), the condition type, and up to 2 query parameters depending on the type of
        query.  For example, the EMPTY query type does not require any parameters, CONTAINS requires one parameter, and
        BETWEEN requires two parameters. If the field that is being queried against in this parameter is a date field,
        then is_date_field must be set to True or this keyword will fail in execution. In this case, parameters must also
        be provided in the format ``YYYY-MM-DD hh:mm:ss`` for proper parsing to a Python datetime object. For example:

        | Add Query Parameter | AND | sys_created_on | BETWEEN | 2018-08-10 00:00:00 | 2018-08-15 23:59:59 | is_date_field=True |
        """
        if is_date_field:
            if param_1 is not None:
                param_1 = self._parse_datetime(param_1)
            if param_2 is not None:
                param_2 = self._parse_datetime(param_2)

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
                raise AssertionError(
                    "No query parameters have been specified yet. Use the ``Required Query Parameter Is`` keyword first.")
            elif logical.upper() in self.VALID_OPERANDS and condition_type.upper() in self.VALID_QUERY_TYPES:
                self._add_valid_query_parameter(logical, field.lower(), condition_type, param_1, param_2)
            else:
                raise AssertionError(
                    "Invalid operand '{l}' and/or query type '{q}'.".format(l=logical, q=condition_type))

    @keyword
    def required_query_parameter_is(self, field, condition_type, param_1=None, param_2=None, is_date_field=False):
        """
        Adds the first (required) query parameter to a SNOW Query.  If another parameter has already been added,
        this keyword will fail. Otherwise, this is the same as `Add Query Parameter`.  If the field that is being
        queried against in this parameter is a date field, then is_date_field must be set to True or this keyword
        will fail in execution.  In this case, parameters must also be provided in the format ``YYYY-MM-DD hh:mm:ss``
        for proper parsing to a Python datetime object. For example:

        | Required Query Parameter Is | sys_created_on | BETWEEN | 2018-08-10 00:00:00 | 2018-08-15 23:59:59 |  is_date_field=True |
        """
        self.add_query_parameter("NONE", field.lower(), condition_type, param_1, param_2, is_date_field)

    @keyword
    def execute_query(self):
        """
        Executes the query that has been created with the specified conditions AND sets the response to the first record
        in the returned data or None. If no query parameters are provided, an error is thrown. Keyword usage with 2+
        data records is not yet supported.
        """
        assert self.query_table is not None, "Query table must already be specified in this test case, but is not."
        query_resource = self.client.resource(api_path="/table/{query_table}".format(query_table=self.query_table))
        try:  # Catch empty queries or errors making the request
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
            raise AssertionError(
                "Field not found in response from {table}: {field}".format(table=self.query_table, field=field_to_get))
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
        start_dt = self._parse_datetime(start)
        end_dt = self._parse_datetime(end)

        query_resource = self.client.resource(api_path="/table/{query_table}".format(query_table=self.query_table))
        fields = ['sys_id']
        content = query_resource.get(
            query="sys_created_onBETWEENjavascript:gs.dateGenerate('{start}')@javascript:gs.dateGenerate('{end}')".format(
                start=start_dt, end=end_dt), fields=fields)
        num_records = len(content.all())
        logger.info("Found {num} records in date range.".format(num=num_records))
        return num_records
