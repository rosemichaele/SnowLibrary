import os

import pytest

from SnowLibrary.keywords.rest_api import RESTQuery
from SnowLibrary.keywords.rest_api import RESTInsert


class TestRESTQuery:

    def test_default_new_rest_query_object(self):
        r = RESTQuery()
        assert r.instance == "iceuat", "SNOW_TEST_URL environment variable has not been set correctly, it should be configured to the iceuat instance."
        assert r.user is not None and r.user == os.environ.get("SNOW_REST_USER"), "SNOW_REST_USER environment variable has not been set."
        assert r.password is not None and r.password == os.environ.get("SNOW_REST_PASS"), "SNOW_REST_PASS environment variable has not been set."
        assert r.client
        assert r.query_table is None
        assert r.response is None

    def test_new_rest_query_instance(self):
        r = RESTQuery(host="iceqa.service-now.com")
        assert r.instance == "iceqa"
        with pytest.raises(AssertionError) as e:
            r = RESTQuery(host="")
        assert "Unable to determine SNOW Instance. Verify that the SNOW_TEST_URL environment variable been set." in str(e)

    def test_new_rest_query_instance_whitespace_in_host_is_trimmed(self):
        r = RESTQuery(host="    https://iceuat.service-now.com/  ")
        assert r.host == "https://iceuat.service-now.com/"
        assert r.instance == "iceuat"

    def test_cannot_add_query_parameter_first(self):
        r = RESTQuery()
        with pytest.raises(AssertionError) as e:
            r.add_query_parameter("AND", "sys_id", "EQUALS", "546565465e4f654efewfweefeewz")
        assert "No query parameters have been specified yet. Use the ``Required Query Parameter Is`` keyword first." in str(e)

    def test_invalid_query_condition_type(self):
        r = RESTQuery()
        with pytest.raises(AssertionError) as e:
            r.required_query_parameter_is(field="sys_id", condition_type="INVALID", param_1="ehe876387364nkje")
        assert "Invalid condition type specified." in str(e)
        r.required_query_parameter_is(field="sys_id", condition_type="EQUALS", param_1="ehe876387364nkje")
        with pytest.raises(AssertionError) as e:
            r.add_query_parameter("INVALID", field="number", condition_type="EQUALS", param_1="TKT546259")
        assert "Invalid operand" in str(e)

    def test_is_empty_query_required_if_no_params(self):
        r = RESTQuery()
        with pytest.raises(AssertionError) as e:
            r.required_query_parameter_is("my_field", "equals")
        assert "Unexpected arguments for condition type EQUALS: expected 1 or 2 arguments, but got none." in str(e)
        r.required_query_parameter_is(field="sys_id", condition_type="EQUALS", param_1="ehe876387364nkje")
        with pytest.raises(AssertionError) as e:
            r.add_query_parameter("AND", "my_field", "greater than")
        assert "Unexpected arguments for condition type GREATER THAN: expected 1 or 2 arguments, but got none." in str(e)

    def test_one_parameter_not_enough_for_between_condition(self):
        r = RESTQuery()
        with pytest.raises(AssertionError) as e:
            r.required_query_parameter_is("my_field", "BeTWeeN", param_1=10)
        assert "Unexpected arguments for condition type BETWEEN: expected 0 or 2 arguments, but got 1." in str(e)

    def test_two_params_too_many_unless_between(self):
        r = RESTQuery()
        with pytest.raises(AssertionError) as e:
            r.required_query_parameter_is("my_field", "CONTAINs", param_1="Lily", param_2="Callie")
        assert "Unexpected arguments for condition type CONTAINS: expected 0 or 1 argument, but got 2." in str(e)

    def test_get_individual_response_field_no_response(self):
        r = RESTQuery()
        with pytest.raises(AssertionError) as e:
            r.get_individual_response_field("test_no_response")
        assert "Failed to retrieve data required for this test." in str(e)

    def test_get_individual_response_field_wrong_field(self):
        response = {'bill_to': '', 'init_request': '', 'short_description': 'PO 76069-14341 - 95032', 'total_cost': '0', 'due_by': '', 'description': '', 'requested_for': '', 'sys_updated_on': '2018-08-08 14:40:48', 'budget_number': '', 'u_received_cost': '0', 'u_business': '', 'number': 'PO0022269', 'sys_id': '0407cfa5dbb75b00fdd99257db9619e5', 'sys_updated_by': 'michael.rose', 'shipping': '', 'terms': '', 'sys_created_on': '2018-08-08 14:40:48', 'vendor': {'link': 'https://iceuat.service-now.com/api/now/table/core_company/4407cfa5dbb75b00fdd99257db9619e3', 'value': '4407cfa5dbb75b00fdd99257db9619e3'}, 'sys_domain': {'link': 'https://iceuat.service-now.com/api/now/table/sys_user_group/global', 'value': 'global'}, 'department': '', 'u_po_number': '76069-14341', 'sys_created_by': 'michael.rose', 'assigned_to': '', 'ordered': '', 'po_date': '7413-01-11 00:10:28', 'vendor_contract': '', 'contract': '', 'expected_delivery': '', 'sys_mod_count': '0', 'u_project': {'link': 'https://iceuat.service-now.com/api/now/table/planned_task/02d1a2fa0f94fe809d486eb8b1050e86', 'value': '02d1a2fa0f94fe809d486eb8b1050e86'}, 'received': '', 'sys_tags': '', 'requested': '2018-08-08 04:00:00', 'requested_by': '', 'u_import_source': {'link': 'https://iceuat.service-now.com/api/now/table/sys_import_set/e2f68fa5dbb75b00fdd99257db961950', 'value': 'e2f68fa5dbb75b00fdd99257db961950'}, 'ship_rate': '0', 'location': '', 'vendor_account': '', 'ship_to': '', 'status': 'ordered'}
        r = RESTQuery(query_table="proc_po", response=response)
        with pytest.raises(AssertionError) as e:
            r.get_individual_response_field("po_aint_got_no_field")
        assert "Field not found in response from proc_po: po_aint_got_no_field" in str(e)

    def test_get_individual_response_field(self):
        response = {'bill_to': '', 'init_request': '', 'short_description': 'PO 76069-14341 - 95032', 'total_cost': '0', 'due_by': '', 'description': '', 'requested_for': '', 'sys_updated_on': '2018-08-08 14:40:48', 'budget_number': '', 'u_received_cost': '0', 'u_business': '', 'number': 'PO0022269', 'sys_id': '0407cfa5dbb75b00fdd99257db9619e5', 'sys_updated_by': 'michael.rose', 'shipping': '', 'terms': '', 'sys_created_on': '2018-08-08 14:40:48', 'vendor': {'link': 'https://iceuat.service-now.com/api/now/table/core_company/4407cfa5dbb75b00fdd99257db9619e3', 'value': '4407cfa5dbb75b00fdd99257db9619e3'}, 'sys_domain': {'link': 'https://iceuat.service-now.com/api/now/table/sys_user_group/global', 'value': 'global'}, 'department': '', 'u_po_number': '76069-14341', 'sys_created_by': 'michael.rose', 'assigned_to': '', 'ordered': '', 'po_date': '7413-01-11 00:10:28', 'vendor_contract': '', 'contract': '', 'expected_delivery': '', 'sys_mod_count': '0', 'u_project': {'link': 'https://iceuat.service-now.com/api/now/table/planned_task/02d1a2fa0f94fe809d486eb8b1050e86', 'value': '02d1a2fa0f94fe809d486eb8b1050e86'}, 'received': '', 'sys_tags': '', 'requested': '2018-08-08 04:00:00', 'requested_by': '', 'u_import_source': {'link': 'https://iceuat.service-now.com/api/now/table/sys_import_set/e2f68fa5dbb75b00fdd99257db961950', 'value': 'e2f68fa5dbb75b00fdd99257db961950'}, 'ship_rate': '0', 'location': '', 'vendor_account': '', 'ship_to': '', 'status': 'ordered'}
        r = RESTQuery(query_table="proc_po", response=response)
        value = r.get_individual_response_field("short_description")
        assert "PO 76069-14341 - 95032" in value

    def test_execute_query_no_table(self):
        r = RESTQuery()
        r.required_query_parameter_is(field="sys_id", condition_type="EQUALS", param_1="ehe876387364nkje")
        with pytest.raises(AssertionError) as e:
            r.execute_query()
        assert "Query table must already be specified in this test case, but is not." in str(e)

    def test_get_record_by_sys_id_no_table(self):
        r = RESTQuery()
        with pytest.raises(AssertionError) as e:
            r.get_record_by_sys_id("ehe876387364nkje")
        assert "Query table must already be specified in this test case, but is not." in str(e)

    def test_get_records_created_in_date_range_requires_query_table(self):
        r = RESTQuery()
        with pytest.raises(AssertionError) as e:
            r.get_records_created_in_date_range("1970-01-01 00:01:00", "2012-12-12 10:10:45")
        assert "Query table must already be specified in this test case, but is not." in str(e)

    def test_get_records_created_in_date_range_invalid_format(self):
        r = RESTQuery()
        r.query_table_is("ticket")
        with pytest.raises(AssertionError) as e:
            r.get_records_created_in_date_range("1970-01-01", "2012-12-12")
        assert "Input date arguments were not provided in the correct format. Verify that they are in the format YYYY-MM-DD hh:mm:ss." in str(e)
        with pytest.raises(AssertionError) as e:
            r.get_records_created_in_date_range("Michael Rules", "2012-12-12")
        assert "Input date arguments were not provided in the correct format. Verify that they are in the format YYYY-MM-DD hh:mm:ss." in str(e)

    def test_required_query_parameter_is_date_field(self):
        r = RESTQuery()
        r.query_table_is("incident")
        try:
            r.required_query_parameter_is("sys_created_on", "BETWEEN", "2016-05-02 09:45:01", "2016-05-09 09:45:01", is_date_field=True)
            r.add_query_parameter("OR", "sys_updated_on", "EQUALS", "2018-08-10 10:23:40")
        except AssertionError:
            pytest.fail("Unexpected AssertionError raised when setting date field query parameter.")

    def test_add_parameter_with_and(self):
        r = RESTQuery()
        r.required_query_parameter_is("description", "CONTAINS", "michael")
        r.add_query_parameter("AND", "status", "EQUALS", "Open")
        assert r.query._query[-2] == "^"

    def test_add_parameter_with_or(self):
        r = RESTQuery()
        r.required_query_parameter_is("description", "CONTAINS", "michael")
        r.add_query_parameter("OR", "status", "EQUALS", "Open")
        assert r.query._query[-2] == "^OR"

    def test_add_parameter_with_nq(self):
        r = RESTQuery()
        r.required_query_parameter_is("description", "CONTAINS", "michael")
        r.add_query_parameter("NQ", "status", "EQUALS", "Open")
        assert r.query._query[-2] == "^NQ"


class TestRESTInsert:
    def test_default_new_rest_insert_object(self):
        i = RESTInsert()
        assert i.instance == "iceuat", "SNOW_TEST_URL environment variable has not been set correctly, it should be configured to the iceuat instance."
        assert i.user is not None and i.user == os.environ.get("SNOW_REST_USER"), "SNOW_REST_USER environment variable has not been set."
        assert i.password is not None and i.password == os.environ.get("SNOW_REST_PASS"), "SNOW_REST_PASS environment variable has not been set."
        assert i.insert_table is None
        assert i.response is None

    def test_new_rest_insert_instance(self):
        i = RESTInsert(host="iceqa.service-now.com")
        assert i.instance == "iceqa"
        with pytest.raises(AssertionError) as e:
            i = RESTInsert(host="")
        assert "Unable to determine SNOW Instance. Verify that the SNOW_TEST_URL environment variable been set." in str(e)

    def test_new_rest_insert_instance_whitespace_in_host_is_trimmed(self):
        i = RESTInsert(host="    https://iceuat.service-now.com/  ")
        assert i.host == "https://iceuat.service-now.com/"
        assert i.instance == "iceuat"

    def test_insert_table_not_valid(self):
        i = RESTInsert()
        with pytest.raises(AssertionError) as e:
            i.insert_table_is("abcd")
        assert "Insert table not found, please check the table name" in str(e)

    def test_insert_table_not_specified(self):
        i = RESTInsert()
        with pytest.raises(AssertionError) as e:
            i.insert_record_parameters("short desc test")
        assert "Insert table must already be specified in this test case, but is not" in str(e)

    def test_insert_payload_not_specified(self):
        i = RESTInsert()
        values = {}
        with pytest.raises(AssertionError) as e:
            i.insert_table_is("ticket")
            i.insert_record_parameters(values)
        assert "No values specified for insert. Expected at least one argument" in str(e)

    def test_insert_payload_not_valid(self):
        i = RESTInsert()
        values = {"short_description":"this is a test","test123":"yes"}
        with pytest.raises(AssertionError) as e:
            i.insert_table_is("ticket")
            i.insert_record_parameters(values)
        assert "Field not found in response from ticket: test123" in str(e)

    def test_insert(self):
        i = RESTInsert()
        values = {"short_description": "this is a test"}
        i.insert_table_is("ticket")
        i.insert_record_parameters(values)
        result = i.insert_record()
        assert result is not None
