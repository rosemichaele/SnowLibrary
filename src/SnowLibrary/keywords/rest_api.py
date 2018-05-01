import os
from urllib.parse import urlparse

import pysnow
from robot.api import logger
from robot.api.deco import keyword


class RESTQuery:
    """
    This library implements keywords for retrieving current data for testing from ServiceNow. It utilizes the open-source
    module pysnow under the hood.
    """

    ROBOT_LIBRARY_SCOPE = 'TEST CASE'

    def __init__(self, host=None, user=None, password=None, query_table=None, response=None):
        if not host:
            self.host = os.environ.get("SNOW_TEST_URL")
        if not user:
            self.user = os.environ.get("SNOW_REST_USER")
        if not password:
            self.password = os.environ.get("SNOW_REST_PASS")
        self.instance = urlparse(self.host).netloc.split(".")[0]
        self.client = pysnow.Client(instance=self.instance, user=self.user, password=self.password)
        self.query_table = query_table
        self.query = pysnow.QueryBuilder()
        self.response = response

    @keyword
    def query_table_is(self, query_table):
        """Sets the table that will be used for the query."""
        self.query_table = query_table
        logger.info("Query table is: {query_table}".format(query_table=query_table))

    @keyword
    def execute_query(self):
        """
        Executes the query that has been created with the specified conditions AND sets the response to the first record
        in the returned data. keyword usage with 2+ data records is not yet supported.
        """
        query_resource = self.client.resource(api_path="/table/{query_table}".format(query_table=self.query_table))
        try:
            self.response = query_resource.get(query=self.query, stream=True).first_or_none()
        except IOError as e:
            logger.error(e.strerror)
            raise

    @keyword
    def get_individual_response_field(self, field_to_get):
        """Returns the specified data field from the REST response"""
        if not self.response:
            logger.error("No data matching query conditions was returned.")
            exit()
        try:
            data = self.response[field_to_get]
        except KeyError:
            logger.error("The following field was not found in the response from {table}: {field}".format(table=self.query_table, field=field_to_get))
            raise
        return data
